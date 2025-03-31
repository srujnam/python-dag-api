**Sample Input JSON File:**
{
  "components": {
    "Step 1": {"depends_on": [], "health": "healthy"},
    "Step 2": {"depends_on": ["Step 1"], "health": "healthy"},
    "Step 3": {"depends_on": ["Step 2"], "health": "unhealthy"},
    "Step 4": {"depends_on": ["Step 2"], "health": "healthy"},
    "Step 5": {"depends_on": ["Step 3"], "health": "healthy"},
    "Step 6": {"depends_on": ["Step 5"], "health": "healthy"},
    "Step 7": {"depends_on": ["Step 3"], "health": "healthy"},
    "Step 8": {"depends_on": ["Step 7"], "health": "healthy"},
    "Step 9": {"depends_on": ["Step 4"], "health": "healthy"},
    "Step 10": {"depends_on": ["Step 6", "Step 8", "Step 9"], "health": "healthy"},
    "Step 11": {"depends_on": ["Step 10"], "health": "healthy"}
  }
}

**Sample OutPUT Tabular Format:**
![image](https://github.com/user-attachments/assets/b7a1b8e6-5370-49da-8246-6323513f2ce7)

**Sample output Graph Image:**
![system_health_graph](https://github.com/user-attachments/assets/ab93eb8d-3df6-459d-b024-c0eb207c6037)

