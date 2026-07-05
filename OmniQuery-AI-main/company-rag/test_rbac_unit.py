"""Unit tests for the new RBAC-aware classify node logic."""
import sys
sys.path.insert(0, '.')

from src.core.orchestrator.nodes.classify import (
    _detect_db_intent, _check_db_rbac, _classify_intent
)

all_pass = True

# ── db_intent detection tests ─────────────────────────────────────────────────
tests_intent = [
    ('list all employees',                  'select'),
    ('show me all departments',             'select'),
    ('how many employees are there',        'select'),
    ('delete employee bob@email.com',       'delete'),
    ('remove user alice from database',     'delete'),
    ('update salary of john to 90000',      'update'),
    ('change the role of alice to admin',   'update'),
    ('promote jane to superadmin',          'update'),
    ('add a new employee John Doe',         'insert'),
    ('hire a new staff member',             'insert'),
    ('insert employee data',                'insert'),
    ('onboard new developer',               'insert'),
]

print('=== db_intent detection ===')
for query, expected in tests_intent:
    detected = _detect_db_intent(query)
    status = 'PASS' if detected == expected else 'FAIL'
    if status == 'FAIL':
        all_pass = False
    print(f'  {status}  [{expected:6}]  Got [{detected:6}]  "{query}"')

# ── RBAC tests ────────────────────────────────────────────────────────────────
print('\n=== RBAC checks ===')
rbac_tests = [
    # (role, db_intent, expected_allow)
    ('user',       'select', True),
    ('user',       'update', False),
    ('user',       'insert', False),
    ('user',       'delete', False),
    ('admin',      'select', True),
    ('admin',      'update', True),
    ('admin',      'insert', False),
    ('admin',      'delete', False),
    ('superadmin', 'select', True),
    ('superadmin', 'update', True),
    ('superadmin', 'insert', True),
    ('superadmin', 'delete', True),
]

for role, intent, expected in rbac_tests:
    allowed, reason = _check_db_rbac(intent, role)
    status = 'PASS' if allowed == expected else 'FAIL'
    if status == 'FAIL':
        all_pass = False
    result = 'ALLOW' if allowed else 'DENY '
    print(f'  {status}  role={role:10} intent={intent:6} -> {result}')

# ── classify_intent mutation keyword tests ────────────────────────────────────
print('\n=== classify intent (mutation keywords now route to data_query) ===')
classify_tests = [
    ('update the salary of alice', 'data_query'),
    ('delete employee',            'data_query'),
    ('hire new staff',             'data_query'),
    ('list all employees',         'data_query'),
    ('what is the weather',        'web_search'),
    ('company leave policy',       'document_search'),
]
for query, expected in classify_tests:
    got = _classify_intent(query)
    status = 'PASS' if got == expected else 'FAIL'
    if status == 'FAIL':
        all_pass = False
    print(f'  {status}  [{expected:16}]  Got [{got:16}]  "{query}"')

print('\n' + ('ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'))
sys.exit(0 if all_pass else 1)
