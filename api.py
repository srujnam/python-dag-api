from flask import Flask, request, jsonify
import json
from collections import deque
import asyncio
from tabulate import tabulate
import networkx as nx
import matplotlib.pyplot as plt

app = Flask(__name__)

def build_dag(data):
    graph = {}
    for component, details in data.get("components", {}).items():
        graph[component] = {"depends_on": details.get("depends_on", []), "health": details.get("health")}
    return graph

async def check_component_health(component_name, health_status):
    await asyncio.sleep(0.1)
    return component_name, health_status

async def traverse_and_check_health(graph):
    start_nodes = [node for node, details in graph.items() if not details["depends_on"]]
    queue = deque(start_nodes)
    visited = set(start_nodes)
    component_health = {}
    tasks = []

    while queue:
        current_component = queue.popleft()
        health_status = graph[current_component].get("health", "unknown")
        tasks.append(check_component_health(current_component, health_status))

        for neighbor, details in graph.items():
            if current_component in details["depends_on"] and neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    results = await asyncio.gather(*tasks)
    for name, health in results:
        component_health[name] = health

    return component_health

@app.route('/healthcheck', methods=['POST'])
async def health_check():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        graph = build_dag(data)
        if not graph:
            return jsonify({"error": "Invalid or empty component definitions"}), 400

        component_health = await traverse_and_check_health(graph)

        table_data = []
        for component, health in component_health.items():
            table_data.append([component, health])

        table = tabulate(table_data, headers=["Component", "Health"], tablefmt="grid")

        filepath = r"D:\SRUJANA\API_Code\system_health_graph.png" 
        graph_message = generate_graph_image(graph, component_health, filepath)

        response = {
            "overall_health": "Degraded" if any(h == "unhealthy" for h in component_health.values()) else "Healthy",
            "component_health": component_health,
            "health_table": f"<pre>{table}</pre>",
            "graph_status": graph_message
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_graph_image(graph_data, component_health, filepath):
    """Generates a graph image with failed components highlighted and saves it to a file."""
    graph = nx.DiGraph()
    for component, details in graph_data.items():
        graph.add_node(component, health=details.get("health"))
        for dependency in details.get("depends_on", []):
            graph.add_edge(dependency, component)

    node_colors = ['red' if component_health.get(node) == 'unhealthy' else 'lightblue' for node in graph.nodes()]

    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color=node_colors, node_size=2000, font_size=10, font_weight='bold', arrowsize=20)

    plt.savefig(filepath)
    plt.close()
    return f"Graph image saved to: {filepath}"

if __name__ == '__main__':
    app.run(debug=True)
