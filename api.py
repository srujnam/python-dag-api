from flask import Flask, request, jsonify
import json
from collections import deque
import asyncio
from tabulate import tabulate
import networkx as nx
import matplotlib.pyplot as plt

app = Flask(__name__)

def build_dg(d):
    g = {}
    for c, det in d.get("components", {}).items():
        g[c] = {"depends_on": det.get("depends_on", []), "health": det.get("health")}
    return g

async def check_health(comp_name, health_stat):
    await asyncio.sleep(0.1)
    return comp_name, health_stat

async def traverse_check(g):
    starts = [n for n, det in g.items() if not det["depends_on"]]
    q = deque(starts)
    visited = set(starts)
    comp_health = {}
    tasks = []

    while q:
        curr = q.popleft()
        h_stat = g[curr].get("health", "unknown")
        tasks.append(check_health(curr, h_stat))

        for neighbor, det in g.items():
            if curr in det["depends_on"] and neighbor not in visited:
                visited.add(neighbor)
                q.append(neighbor)

    res = await asyncio.gather(*tasks)
    for name, health in res:
        comp_health[name] = health

    return comp_health

@app.route('/healthcheck', methods=['POST'])
async def health_check_api():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        graph = build_dg(data)
        if not graph:
            return jsonify({"error": "Invalid definitions"}), 400

        comp_health = await traverse_check(graph)

        table_data = []
        for c, h in comp_health.items():
            table_data.append([c, h])

        table = tabulate(table_data, headers=["Component", "Health"], tablefmt="grid")

        fp = r"D:\SRUJANA\API_Code\system_health_graph.png"
        graph_msg = gen_graph(graph, comp_health, fp)

        resp = {
            "overall_health": "Degraded" if any(h == "unhealthy" for h in comp_health.values()) else "Healthy",
            "component_health": comp_health,
            "health_table": f"<pre>{table}</pre>",
            "graph_status": graph_msg
        }

        return jsonify(resp)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def gen_graph(gd, ch, fp):
    g = nx.DiGraph()
    for c, det in gd.items():
        g.add_node(c, health=det.get("health"))
        for dep in det.get("depends_on", []):
            g.add_edge(dep, c)

    n_colors = ['red' if ch.get(n) == 'unhealthy' else 'lightblue' for n in g.nodes()]

    pos = nx.spring_layout(g)
    nx.draw(g, pos, with_labels=True, node_color=n_colors, node_size=2000, font_size=10, font_weight='bold', arrowsize=20)

    plt.savefig(fp)
    plt.close()
    return f"Graph image saved to: {fp}"

if __name__ == '__main__':
    app.run(debug=True)
