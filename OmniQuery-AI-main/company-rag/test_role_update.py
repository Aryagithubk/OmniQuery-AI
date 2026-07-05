import requests

# Login as superadmin
login = requests.post("http://localhost:8001/api/v1/auth/login", json={
    "email": "krisha.arya@company.com",
    "password": "krishapassword"
})
token = login.json()["access_token"]
print("Logged in as:", login.json()["role"])

# Send query
res = requests.post("http://localhost:8001/api/v1/query", json={
    "query": "remove role as superadmin from arjun sharma. email arjun.sharma@company.com. make role as user"
}, headers={"Authorization": f"Bearer {token}"})

data = res.json()
print("Agents used:", data.get("agents_used"))
print("Confidence:", data.get("confidence"))
print("Sources:", [s.get("source_type") for s in data.get("sources", [])])
print()
print("=== ANSWER ===")
print(data.get("answer", ""))
