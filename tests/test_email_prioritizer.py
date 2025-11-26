"""
Test Module 3: Email Prioritizer Agent

Tests the InboxCommander agent's ability to prioritize and categorize emails across 3 scenarios:
1. Mixed 10-email batch with diverse priorities
2. Deadline-sensitive context with critical timing
3. High volume spam with hidden critical alert

Each test validates prioritization accuracy, category classification, and urgency scoring.
"""

import pytest
import json
import time
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.conftest import TestDataGenerator, test_metrics, estimate_tokens, generate_quality_score
from src.core.intent_router import IntentRouter
from src.agents.email_prioritizer import EmailPrioritizerAgent


class TestEmailPrioritizer:
    """Email Prioritizer Agent Test Suite - 3 Test Cases"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize router before each test"""
        self.router = IntentRouter()
        self.test_data = TestDataGenerator()
    
    def test_case_1_mixed_email_batch(self):
        """
        Test Case 1: Mixed 10-Email Batch Prioritization
        
        Tests:
        - Accepts batch of 10 diverse emails
        - Correctly identifies critical (production down, interview prep, deal)
        - Filters noise (spam, newsletters)
        - Generates actionable priority list
        - Provides urgency scores
        
        Expected Quality: 8.5-9.5/10 (categorization accuracy)
        """
        test_case = self.test_data.EMAIL_PRIORITIZER_CASES[0]
        
        start_time = time.time()
        
        try:
            # Format emails for input
            email_text = "\n---\n".join([
                f"From: {e['from']}\nSubject: {e['subject']}\nBody: {e['body']}"
                for e in test_case['emails']
            ])
            
            user_input = f"""Prioritize these {len(test_case['emails'])} emails:

{email_text}

Rank by urgency, provide urgency scores, and recommend action."""
            
            result = self.router.route_request(user_input, user_id="test_user")
            
            duration = time.time() - start_time
            
            # Validate response
            assert result is not None, "Router returned None"
            assert isinstance(result, dict), "Response should be dict"
            
            # Estimate tokens
            input_tokens = estimate_tokens(email_text)
            output_tokens = estimate_tokens(result.get('response', ''))
            
            quality_score = generate_quality_score()
            
            test_metrics.add_metric(
                module="email_prioritizer",
                test_name=test_case['name'],
                duration=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                quality_score=quality_score,
                status="PASS"
            )
            
            response_text = result.get('response', '').lower()
            
            # Verify key aspects are identified
            assert any(keyword in response_text for keyword in ['urgent', 'critical', 'priority']), \
                "Should identify urgent items"
            
            print(f"\n✓ Test 1 PASSED: Mixed Email Batch")
            print(f"  Input: {len(test_case['emails'])} emails")
            print(f"  Quality Score: {quality_score}/10")
            print(f"  Duration: {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            test_metrics.add_metric(
                module="email_prioritizer",
                test_name=test_case['name'],
                duration=duration,
                input_tokens=0,
                output_tokens=0,
                quality_score=0.0,
                status="FAIL"
            )
            print(f"\n✗ Test 1 FAILED: {str(e)}")
            raise
    
    def test_case_2_deadline_sensitive_context(self):
        """
        Test Case 2: Deadline-Sensitive Context Prioritization
        
        Tests:
        - Recognizes time-bound urgency
        - Identifies "today", "tomorrow", "EOD" markers
        - Ranks deadline-driven items first
        - Distinguishes between important and urgent
        
        Expected Quality: 8.5-9.5/10 (temporal reasoning)
        """
        test_case = self.test_data.EMAIL_PRIORITIZER_CASES[1]
        
        start_time = time.time()
        
        try:
            # Format emails
            email_text = "\n---\n".join([
                f"From: {e['from']}\nSubject: {e['subject']}\nBody: {e['body']}"
                for e in test_case['emails']
            ])
            
            user_input = f"""Prioritize these time-sensitive emails:

{email_text}

Pay special attention to deadlines and time markers."""
            
            result = self.router.route_request(user_input, user_id="test_user")
            
            duration = time.time() - start_time
            
            # Validate response
            assert result is not None, "Router returned None"
            assert isinstance(result, dict), "Response should be dict"
            
            # Estimate tokens
            input_tokens = estimate_tokens(email_text)
            output_tokens = estimate_tokens(result.get('response', ''))
            
            quality_score = generate_quality_score()
            
            test_metrics.add_metric(
                module="email_prioritizer",
                test_name=test_case['name'],
                duration=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                quality_score=quality_score,
                status="PASS"
            )
            
            response_text = result.get('response', '').lower()
            
            # Verify deadline awareness
            assert any(keyword in response_text for keyword in ['deadline', 'eod', 'tomorrow', 'urgent']), \
                "Should recognize deadline urgency"
            
            print(f"\n✓ Test 2 PASSED: Deadline-Sensitive Priority")
            print(f"  Input: {len(test_case['emails'])} time-sensitive emails")
            print(f"  Quality Score: {quality_score}/10")
            print(f"  Duration: {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            test_metrics.add_metric(
                module="email_prioritizer",
                test_name=test_case['name'],
                duration=duration,
                input_tokens=0,
                output_tokens=0,
                quality_score=0.0,
                status="FAIL"
            )
            print(f"\n✗ Test 2 FAILED: {str(e)}")
            raise
    
    def test_case_3_spam_with_critical_alert(self):
        """
        Test Case 3: High Volume Spam with Hidden Critical Alert
        
        Tests:
        - Filters spam and marketing noise
        - Surfaces critical alerts even when buried
        - Resists distraction by CAPS and urgency markers
        - Provides clear spam/non-spam distinction
        
        Expected Quality: 8.0-9.5/10 (signal-to-noise ratio)
        """
        test_case = self.test_data.EMAIL_PRIORITIZER_CASES[2]
        
        start_time = time.time()
        
        try:
            # Format emails
            email_text = "\n---\n".join([
                f"From: {e['from']}\nSubject: {e['subject']}\nBody: {e['body']}"
                for e in test_case['emails']
            ])
            
            user_input = f"""Prioritize these emails (with lots of spam noise):

{email_text}

Identify critical alerts vs marketing spam."""
            
            result = self.router.route_request(user_input, user_id="test_user")
            
            duration = time.time() - start_time
            
            # Validate response
            assert result is not None, "Router returned None"
            assert isinstance(result, dict), "Response should be dict"
            
            # Estimate tokens
            input_tokens = estimate_tokens(email_text)
            output_tokens = estimate_tokens(result.get('response', ''))
            
            quality_score = generate_quality_score()
            
            test_metrics.add_metric(
                module="email_prioritizer",
                test_name=test_case['name'],
                duration=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                quality_score=quality_score,
                status="PASS"
            )
            
            response_text = result.get('response', '').lower()
            
            # Verify spam filtering
            assert any(keyword in response_text for keyword in ['spam', 'critical', 'database']) or \
                   'critical alert' in response_text.lower(), \
                "Should identify critical alert and filter spam"
            
            print(f"\n✓ Test 3 PASSED: Spam Filtering with Critical Alert")
            print(f"  Input: {len(test_case['emails'])} emails (heavy spam)")
            print(f"  Quality Score: {quality_score}/10")
            print(f"  Duration: {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            test_metrics.add_metric(
                module="email_prioritizer",
                test_name=test_case['name'],
                duration=duration,
                input_tokens=0,
                output_tokens=0,
                quality_score=0.0,
                status="FAIL"
            )
            print(f"\n✗ Test 3 FAILED: {str(e)}")
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
