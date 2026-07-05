import requests
import json
import time

BASE_URL = "http://localhost:8001/api/v1"

def test_workflow():
    print("1. Registering 'Krisha Arya' as a standard user...")
    register_payload = {
        "first_name": "Krisha",
        "last_name": "Arya",
        "email": "krisha.arya@company.com",
        "password": "krishapassword",
        "department_id": 1,
        "job_title": "AI Architect",
        "salary": 180000,
        "hire_date": "2024-04-13"
    }

    res_reg = requests.post(f"{BASE_URL}/auth/register", json=register_payload)
    if res_reg.status_code == 200:
        print("   ✅ Successfully registered Krisha. Her initial role is:", res_reg.json().get('role'))
    else:
        print("   ⚠️ Registration issue:", res_reg.json())

    # Now login as Superadmin to elevate her role
    print("\n2. Logging in as superadmin Arjun Sharma...")
    login_payload = {
        "email": "arjun.sharma@company.com",
        "password": "password"
    }
    res_login = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    superadmin_token = res_login.json().get("access_token")
    print(f"   ✅ Authenticated context. Role: {res_login.json().get('role')}")

    # Use the Agent to run the UPDATE query
    print("\n3. Instructing OmniQuery DB Agent to promote Krisha to Superadmin...")
    query_payload = {
        "query": "UPDATE employees SET role = 'superadmin' WHERE email = 'krisha.arya@company.com'; Return the exact updated row to confirm."
    }
    headers = {"Authorization": f"Bearer {superadmin_token}"}
    
    res_query = requests.post(f"{BASE_URL}/query", json=query_payload, headers=headers)
    
    print("\n[AI RESPONSE]")
    print(res_query.json().get("answer"))

if __name__ == "__main__":
    test_workflow()
