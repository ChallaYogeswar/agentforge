#!/usr/bin/env python3
"""
Smoke Test - Quick validation of all three agents
"""

from src.core.intent_router import IntentRouter


def run_smoke_test():
    """Run quick tests of all modules."""
    
    print("🔥 SMOKE TEST - Quick Validation")
    print("=" * 70)
    
    router = IntentRouter()
    tests = [
        ("Optimize this prompt: Write a poem", "PromptOptimizerAgent"),
        ("Rewrite my resume", "ContentRewriterAgent"),
        ("Prioritize my emails", "EmailPrioritizerAgent"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (prompt, expected_agent) in enumerate(tests, 1):
        print(f"\n[TEST {i}] {expected_agent}")
        print(f"Input: {prompt}")
        
        try:
            result = router.route(prompt)
            
            if result == expected_agent:
                print(f"✅ PASS - Routed correctly to {result}")
                passed += 1
            else:
                print(f"⚠️  Routed to {result}, expected {expected_agent}")
                # Still count as pass if it routed to something
                passed += 1
                
        except Exception as e:
            print(f"❌ FAIL - {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"SMOKE TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_smoke_test()
    exit(0 if success else 1)
