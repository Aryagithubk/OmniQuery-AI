import requests
r = requests.get("http://localhost:8001/api/v1/agents")
data = r.json()
for a in data.get("agents", []):
    print(f"{a['agent_name']}: {a['status']}")
