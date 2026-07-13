"""
SETU Phase 5 — Self-Test Suite

Runs 6 diverse realistic queries end-to-end through the full pipeline.
Includes: normal queries, Hindi query, low-confidence trigger, and unanswerable query.
"""

import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.orchestrator import run_setu


TEST_QUERIES = [
    {
        "id": 1,
        "name": "SC student scholarship (English)",
        "query": "I am an SC student from Rajasthan, family income 2 lakh. I passed 12th with 65%. What scholarships can I get?",
        "expected_schemes": ["Post-Matric Scholarship", "Uttar Matric"],
        "expected_intent": "find_schemes",
    },
    {
        "id": 2,
        "name": "Hindi query — widow pension",
        "query": "मैं एक विधवा हूँ, BPL परिवार से हूँ, उम्र 50 साल है। मुझे कौन सी पेंशन मिल सकती है?",
        "expected_schemes": ["Indira Gandhi", "Widow Pension"],
        "expected_intent": "find_schemes",
    },
    {
        "id": 3,
        "name": "Farmer query",
        "query": "I am a farmer with 2 acres of land in Rajasthan. What government help is available for me?",
        "expected_schemes": ["PM Kisan", "MGNREGA"],
        "expected_intent": "find_schemes",
    },
    {
        "id": 4,
        "name": "Girl child savings",
        "query": "My daughter is 4 years old. Is there any savings scheme for her education?",
        "expected_schemes": ["Sukanya Samriddhi"],
        "expected_intent": "find_schemes",
    },
    {
        "id": 5,
        "name": "LOW CONFIDENCE TRIGGER — fabricated scheme",
        "query": "Tell me about the Pradhan Mantri Digital Laptop Yojana that gives free laptops to all students",
        "expected_schemes": [],
        "expected_intent": "find_schemes",
        "expect_low_confidence": True,
    },
    {
        "id": 6,
        "name": "UNANSWERABLE — out of scope",
        "query": "What is the current stock price of Reliance Industries?",
        "expected_schemes": [],
        "expected_intent": "general_question",
        "expect_no_results": True,
    },
]


def run_test(test_case):
    """Run a single test case and return results."""
    print(f"\n{'='*60}")
    print(f"Test {test_case['id']}: {test_case['name']}")
    print(f"Query: {test_case['query'][:80]}...")
    print(f"{'='*60}")
    
    start = time.time()
    
    try:
        result = run_setu(test_case["query"])
        elapsed = time.time() - start
        
        # Extract key results
        intent = result.get("intent", "unknown")
        schemes = result.get("eligible_schemes", [])
        confidence = result.get("overall_confidence", 0)
        trace = result.get("agent_trace", [])
        response = result.get("final_response", "")[:300]
        
        # Check expectations
        issues = []
        
        # Check if expected schemes were found
        for expected in test_case.get("expected_schemes", []):
            found = any(expected.lower() in s.lower() for s in schemes)
            if not found and not test_case.get("expect_no_results"):
                issues.append(f"Expected scheme '{expected}' not found in results")
        
        # Check low confidence trigger
        if test_case.get("expect_low_confidence") and confidence > 0.7:
            issues.append(f"Expected low confidence but got {confidence:.2f}")
        
        # Print results
        print(f"\n  Time: {elapsed:.1f}s")
        print(f"  Intent: {intent}")
        print(f"  Schemes found: {len(schemes)}")
        for s in schemes:
            print(f"    - {s}")
        print(f"  Confidence: {confidence:.3f}")
        print(f"  Agent trace: {len(trace)} steps")
        for t in trace:
            print(f"    {t}")
        print(f"  Response preview: {response}...")
        
        if issues:
            print(f"\n  [!!] ISSUES:")
            for issue in issues:
                print(f"    - {issue}")
            status = "ISSUES"
        else:
            print(f"\n  [OK] PASSED")
            status = "PASSED"
        
        return {
            "id": test_case["id"],
            "name": test_case["name"],
            "status": status,
            "time": elapsed,
            "schemes_found": len(schemes),
            "confidence": confidence,
            "issues": issues,
            "intent": intent,
        }
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"\n  [XX] ERROR: {str(e)}")
        return {
            "id": test_case["id"],
            "name": test_case["name"],
            "status": "ERROR",
            "time": elapsed,
            "error": str(e),
            "issues": [str(e)],
        }


def main():
    print("=" * 60)
    print("SETU Phase 5 — Self-Test Suite")
    print("=" * 60)
    print(f"Running {len(TEST_QUERIES)} test queries...")
    
    results = []
    
    for test_case in TEST_QUERIES:
        result = run_test(test_case)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["status"] == "PASSED")
    issues = sum(1 for r in results if r["status"] == "ISSUES")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    
    for r in results:
        icon = {"PASSED": "[OK]", "ISSUES": "[!!]", "ERROR": "[XX]"}.get(r["status"], "??")
        conf = r.get("confidence", 0)
        print(f"  {icon} Test {r['id']}: {r['name']} ({r.get('time', 0):.1f}s, conf={conf:.2f})")
        for issue in r.get("issues", []):
            print(f"      -> {issue}")
    
    print(f"\n  Total: {passed} passed, {issues} issues, {errors} errors out of {len(results)}")
    total_time = sum(r.get("time", 0) for r in results)
    print(f"  Total time: {total_time:.1f}s")
    
    return results


if __name__ == "__main__":
    results = main()
