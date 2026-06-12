import json
from app.services.llm_classifier import llm_classifier

# Test the extract_json method
test_cases = [
    '{"category": "Billing"}',
    '```json\n{"category": "Billing"}\n```',
    '```\n{"category": "Billing"}\n```',
    'Some text before {\n  "category": "Billing"\n} and after',
]

for i, test in enumerate(test_cases):
    result = llm_classifier._extract_json(test)
    print(f'Test {i+1}: {result}')
    if result:
        try:
            parsed = json.loads(result)
            print(f'  Parsed: {parsed}')
        except:
            print(f'  Parse failed')
    else:
        print(f'  No JSON found')
