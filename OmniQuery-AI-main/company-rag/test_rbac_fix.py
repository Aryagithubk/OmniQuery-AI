import requests
import json

BASE = "http://localhost:8001"

# --- Login as superadmin ---
login = requests.post(f"{BASE}/api/v1/auth/login", json={"email": "arjun.sharma@company.com", "password": "password123"})
print("Login status:", login.status_code)
token = ""
role = "anonymous"
if login.status_code == 200:
    data = login.json()
    token = data.get("access_token", "")
    role = data.get("role", "unknown")
    print(f"Logged in as: {data.get('first_name')} {data.get('last_name')} | role={role}")
else:
    print("Login failed:", login.text)

headers = {"Authorization": f"Bearer {token}"} if token else {}


def test(label, query, hdrs=None):
    if hdrs is None:
        hdrs = headers
    r = requests.post(f"{BASE}/api/v1/query", json={"query": query}, headers=hdrs)
    d = r.json()
    print(f"\n--- {label} ---")
    print(f"  Agents : {d.get('agents_used')}")
    print(f"  Confidence: {d.get('confidence')}")
    ans = d.get("answer", "")
    print(f"  Answer : {ans[:400]}")
    sources = d.get("sources", [])
    if sources:
        print(f"  Source : {sources[0].get('excerpt','')[:80]}")


# Test 1: The original bug — "address" must NOT trigger INSERT
test("T1: Pooja Iyer email (must be SELECT)", "what is Pooja Iyer's email address?")

# Test 2: Superadmin INSERT (must succeed)
test("T2: Superadmin INSERT", "add employee Prince Singh, email prince.singh@company.com, department_id 1, job title Software Engineer, salary 95000")

# Test 3: Verify the insert by looking up the new record
test("T3: Verify insert", "what is Prince Singh's email?")

# Test 4: Superadmin DELETE (must succeed)
test("T4: Superadmin DELETE", "delete employee prince.singh@company.com")

# Test 5: User-role INSERT — must be BLOCKED
user_login = requests.post(f"{BASE}/api/v1/auth/login", json={"email": "neha.verma@company.com", "password": "password123"})
user_token = ""
if user_login.status_code == 200:
    ud = user_login.json()
    user_token = ud.get("access_token", "")
    print(f"\nLogged in as user: {ud.get('first_name')} | role={ud.get('role')}")
user_headers = {"Authorization": f"Bearer {user_token}"} if user_token else {}
test("T5: User-role INSERT (must be BLOCKED)", "add employee John Doe, email john.doe@company.com, salary 80000", hdrs=user_headers)

print("\nAll tests done.")
