"""Debug the classify function to find why 'what is company policy' scores wrong."""
import sys, os
sys.path.insert(0, '.')

# Fix encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.core.orchestrator.nodes.classify import _classify_intent, _INTENT_KEYWORDS

queries = [
    "what is company policy",
    "what is the average salary",
    "latest news about AI",
]

for q in queries:
    ql = q.lower()
    print(f"\n{'='*60}")
    print(f"QUERY: {repr(q)}")
    print(f"{'='*60}")
    
    for intent_name, config in _INTENT_KEYWORDS.items():
        matches = [kw for kw in config['keywords'] if kw in ql]
        score = config['base_score'] + len(matches) * config['weight']
        if matches:
            print(f"  {intent_name}: {matches} => score={score:.1f}")
        else:
            print(f"  {intent_name}: (no matches) => score={score:.1f}")
    
    result = _classify_intent(q)
    print(f"  RESULT: intent={result[0]}, primary_agent={result[1]}")
