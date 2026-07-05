"""
Verification Test Suite for OmniQuery Orchestrator Overhaul
Tests all 6 scenarios from the implementation plan.
"""

import sys
import os
# Fix Windows cp1252 encoding issues with emoji characters
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ["PYTHONIOENCODING"] = "utf-8"

import requests
import json
import time
import hashlib

BASE_URL = "http://localhost:8001"

# ── Helper ──────────────────────────────────────────────────────────
def query(text, token=None, label=""):
    """Send a query and print results."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print(f"\n{'='*70}")
    print(f"TEST: {label}")
    print(f"QUERY: \"{text}\"")
    print(f"{'='*70}")
    
    start = time.time()
    resp = requests.post(f"{BASE_URL}/api/v1/query", json={"query": text}, headers=headers)
    elapsed = (time.time() - start) * 1000
    
    if resp.status_code != 200:
        print(f"  ERROR: HTTP {resp.status_code} — {resp.text[:200]}")
        return None
    
    data = resp.json()
    answer = data.get("answer", "")
    agents = data.get("agents_used", [])
    confidence = data.get("confidence", 0)
    sources = data.get("sources", [])
    exec_time = data.get("execution_time_ms", 0)
    
    print(f"  AGENTS USED: {agents}")
    print(f"  CONFIDENCE:  {confidence}")
    print(f"  EXEC TIME:   {exec_time:.0f}ms (client: {elapsed:.0f}ms)")
    print(f"  SOURCES:     {[s.get('source_type') for s in sources]}")
    
    # Print first 500 chars of answer
    preview = answer[:500].replace('\n', '\n  ')
    print(f"  ANSWER:\n  {preview}")
    if len(answer) > 500:
        print(f"  ... ({len(answer)} total chars)")
    
    return data

def login(email, password):
    """Login and return token."""
    resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": email, "password": password})
    if resp.status_code == 200:
        data = resp.json()
        print(f"  LOGIN OK: role={data.get('role')}, name={data.get('first_name')} {data.get('last_name')}")
        return data.get("access_token")
    else:
        print(f"  LOGIN FAILED: {resp.status_code} — {resp.text[:200]}")
        return None


# ── Run Tests ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*70)
    print("   OMNIQUERY ORCHESTRATOR VERIFICATION TESTS")
    print("="*70)
    
    results = {}
    
    # ── Test 1: "show me all employee details" → DB fast-path, ALL employees
    r = query("show me all employee details", label="BUG 1 FIX — Should return ALL employees via DB fast-path")
    if r:
        answer = r.get("answer", "")
        agents = r.get("agents_used", [])
        has_db = "DBAgent" in agents
        has_table = "|" in answer
        no_web = "WebSearchAgent" not in agents
        row_count = answer.count("\n|") - 1 if has_table else 0  # rough count
        results["test1"] = {
            "pass": has_db and has_table and no_web and row_count > 1,
            "detail": f"DBAgent={has_db}, table={has_table}, rows~{row_count}, noWeb={no_web}"
        }
    
    # ── Test 2: "what is company policy" → DocAgent, NOT WebSearchAgent
    r = query("what is company policy", label="BUG 2 FIX — Should route to DocAgent, NOT WebSearchAgent")
    if r:
        agents = r.get("agents_used", [])
        has_doc = "DocAgent" in agents
        no_web = "WebSearchAgent" not in agents
        results["test2"] = {
            "pass": has_doc and no_web,
            "detail": f"DocAgent={has_doc}, noWeb={no_web}, agents={agents}"
        }
    
    # ── Test 3: "what is the average salary" → DBAgent
    r = query("what is the average salary", label="BUG 2 VARIANT — Should route to DBAgent")
    if r:
        agents = r.get("agents_used", [])
        has_db = "DBAgent" in agents
        results["test3"] = {
            "pass": has_db,
            "detail": f"DBAgent={has_db}, agents={agents}"
        }
    
    # ── Test 4: "latest news about AI" → Fallback to WebSearchAgent
    r = query("latest news about AI", label="WEB FALLBACK — Should eventually use WebSearchAgent or Fallback")
    if r:
        agents = r.get("agents_used", [])
        answer = r.get("answer", "")
        # Accept either WebSearchAgent in agents_used OR fallback general knowledge
        is_web_or_fallback = "WebSearchAgent" in agents or "Fallback" in agents
        results["test4"] = {
            "pass": is_web_or_fallback,
            "detail": f"agents={agents}, hasAnswer={bool(answer)}"
        }
    
    # ── Test 5: "how many employees are there" → DBAgent fast-path
    r = query("how many employees are there", label="FAST-PATH — Should use DBAgent fast-path COUNT")
    if r:
        agents = r.get("agents_used", [])
        answer = r.get("answer", "")
        has_db = "DBAgent" in agents
        # Check if answer contains a number (the count)
        has_count = any(c.isdigit() for c in answer)
        results["test5"] = {
            "pass": has_db and has_count,
            "detail": f"DBAgent={has_db}, hasCount={has_count}, agents={agents}"
        }
    
    # ── Test 6: RBAC — mutation with 'user' role should be denied
    # First login as a regular user
    print(f"\n{'='*70}")
    print(f"TEST: RBAC — Login as regular user and attempt DELETE")
    print(f"{'='*70}")
    
    # Try to find a user account — use the auth endpoint
    token = login("arya@company.com", "password123")
    if not token:
        # Try with a sha256 hashed password approach
        print("  Trying alternate login...")
        token = login("pooja.iyer@techcorp.com", "password123")
    
    if token:
        r = query("delete employee with id 999", token=token, label="RBAC DENY — user role attempting DELETE")
        if r:
            answer = r.get("answer", "")
            is_denied = "permission denied" in answer.lower() or "denied" in answer.lower()
            results["test6"] = {
                "pass": is_denied,
                "detail": f"denied={is_denied}"
            }
    else:
        print("  SKIPPED: Could not login. Testing without auth (default 'user' role).")
        r = query("delete employee with id 999", label="RBAC DENY — default user role attempting DELETE")
        if r:
            answer = r.get("answer", "")
            is_denied = "permission denied" in answer.lower() or "denied" in answer.lower()
            results["test6"] = {
                "pass": is_denied,
                "detail": f"denied={is_denied}"
            }
    
    # ── Summary ─────────────────────────────────────────────────────
    print(f"\n\n{'='*70}")
    print("   VERIFICATION RESULTS SUMMARY")
    print(f"{'='*70}")
    
    test_names = {
        "test1": "BUG 1: 'show all employees' returns ALL rows",
        "test2": "BUG 2: 'company policy' routes to DocAgent",
        "test3": "LOOPHOLE 4: 'average salary' routes to DBAgent",
        "test4": "COMPONENT 2: 'latest news' uses WebSearchAgent/Fallback",
        "test5": "COMPONENT 3: 'how many employees' uses fast-path",
        "test6": "RBAC: DELETE denied for user role",
    }
    
    passed = 0
    failed = 0
    for key, name in test_names.items():
        if key in results:
            status = "PASS" if results[key]["pass"] else "FAIL"
            icon = "+" if results[key]["pass"] else "x"
            detail = results[key]["detail"]
            if results[key]["pass"]:
                passed += 1
            else:
                failed += 1
            print(f"  [{icon}] {name}")
            print(f"      {detail}")
        else:
            print(f"  [?] {name} — SKIPPED")
    
    print(f"\n  TOTAL: {passed} passed, {failed} failed, {len(test_names) - passed - failed} skipped")
    print(f"{'='*70}")
