"""
Comprehensive Test Suite for AgentForge
Includes new test cases for all 3 modules with detailed verification
"""

import pytest
import json
import time
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.prompt_optimizer import PromptOptimizerAgent
from src.agents.content_optimizer import ContentRewriterAgent
from src.agents.email_prioritizer import EmailPrioritizerAgent
from src.core.intent_router import IntentRouter


class TestPromptOptimizer:
    """Test Suite: Prompt Optimizer Agent"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize agent"""
        self.agent = PromptOptimizerAgent()
    
    def test_basic_prompt_optimization(self):
        """Test 1: Basic prompt optimization"""
        test_prompt = "Write a story about an AI"
        result = self.agent.run(test_prompt)
        
        assert result is not None, "Result should not be None"
        assert isinstance(result, str), "Result should be string"
        assert len(result) > 0, "Result should not be empty"
        print("✅ Test 1.1 passed: Basic optimization works")
    
    def test_technical_prompt_optimization(self):
        """Test 2: Technical prompt optimization"""
        test_prompt = "Write Python code to parse JSON files"
        result = self.agent.run(test_prompt)
        
        assert result is not None, "Result should not be None"
        assert len(result) > len(test_prompt), "Optimized should be more detailed"
        print("✅ Test 1.2 passed: Technical prompt optimization")
    
    def test_creative_prompt_optimization(self):
        """Test 3: Creative prompt optimization"""
        test_prompt = "Generate a funny poem about coffee"
        result = self.agent.run(test_prompt)
        
        assert result is not None, "Result should not be None"
        assert "poem" in result.lower() or "humor" in result.lower() or len(result) > 50
        print("✅ Test 1.3 passed: Creative prompt optimization")
    
    def test_performance_timing(self):
        """Test 4: Performance - response time"""
        test_prompt = "Optimize this prompt: hello world"
        
        start_time = time.time()
        result = self.agent.run(test_prompt)
        duration = time.time() - start_time
        
        assert result is not None, "Result should not be None"
        assert duration < 60, f"Response should complete within 60s, took {duration:.2f}s"
        print(f"✅ Test 1.4 passed: Performance OK ({duration:.2f}s)")


class TestCareerArchitect:
    """Test Suite: Career Architect (Content Rewriter) Agent"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize agent"""
        self.agent = ContentRewriterAgent()
    
    def test_resume_bullet_rewriting(self):
        """Test 2.1: Resume bullet point rewriting"""
        resume_bullet = "Worked on a project using Python"
        target = "Senior Backend Engineer role"
        
        prompt = f"Rewrite this resume bullet for {target}: {resume_bullet}"
        result = self.agent.run(prompt)
        
        assert result is not None, "Result should not be None"
        assert len(result) > 0, "Result should not be empty"
        assert len(result) > len(resume_bullet), "Should be more detailed than original"
        print("✅ Test 2.1 passed: Resume bullet rewriting")
    
    def test_email_body_rewriting(self):
        """Test 2.2: Email body transformation"""
        casual_email = "Hi, we have a great product. Maybe you want to try it?"
        target = "Professional B2B sales email"
        
        prompt = f"Transform this email into {target}: {casual_email}"
        result = self.agent.run(prompt)
        
        assert result is not None, "Result should not be None"
        assert len(result) > 0, "Result should not be empty"
        print("✅ Test 2.2 passed: Email body transformation")
    
    def test_marketing_copy_rewriting(self):
        """Test 2.3: Marketing copy rewriting"""
        basic_copy = "Software tool for making prompts"
        target = "Persuasive marketing for LinkedIn"
        
        prompt = f"Rewrite this for {target}: {basic_copy}"
        result = self.agent.run(prompt)
        
        assert result is not None, "Result should not be None"
        assert len(result) > len(basic_copy), "Should be more detailed"
        print("✅ Test 2.3 passed: Marketing copy rewriting")
    
    def test_job_matching(self):
        """Test 2.4: Resume tailoring to job description"""
        resume = "5 years Python experience, built web apps, managed teams"
        job_desc = "Looking for Senior Backend Engineer: Python, REST APIs, distributed systems, 5+ years"
        
        prompt = f"Tailor this resume to job: Resume: {resume}. Job: {job_desc}"
        result = self.agent.run(prompt)
        
        assert result is not None, "Result should not be None"
        print("✅ Test 2.4 passed: Job matching rewrite")
    
    def test_performance_timing(self):
        """Test 2.5: Performance - response time"""
        resume = "Worked on projects"
        prompt = f"Improve this: {resume}"
        
        start_time = time.time()
        result = self.agent.run(prompt)
        duration = time.time() - start_time
        
        assert result is not None, "Result should not be None"
        assert duration < 60, f"Response should complete within 60s, took {duration:.2f}s"
        print(f"✅ Test 2.5 passed: Performance OK ({duration:.2f}s)")


class TestEmailPrioritizer:
    """Test Suite: Email Prioritizer Agent"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize agent"""
        self.agent = EmailPrioritizerAgent()
    
    def test_single_email_prioritization(self):
        """Test 3.1: Single email prioritization"""
        email = "From: boss@company.com - URGENT: Production down"
        result = self.agent.run(email)
        
        assert result is not None, "Result should not be None"
        assert len(result) > 0, "Result should not be empty"
        print("✅ Test 3.1 passed: Single email prioritization")
    
    def test_multiple_emails_batch(self):
        """Test 3.2: Batch email prioritization"""
        emails = [
            "Email 1: From boss - URGENT: System down",
            "Email 2: From newsletter - Today's digest",
            "Email 3: From HR - Interview next week",
            "Email 4: From client - Contract due Friday",
            "Email 5: From spam - 50% off today"
        ]
        
        email_text = "Prioritize these emails:\n" + "\n".join(emails)
        result = self.agent.run(email_text)
        
        assert result is not None, "Result should not be None"
        assert len(result) > 0, "Result should not be empty"
        print("✅ Test 3.2 passed: Batch email prioritization")
    
    def test_deadline_sensitivity(self):
        """Test 3.3: Deadline-sensitive email detection"""
        emails = [
            "Contract needs signature by EOD today",
            "Team lunch poll - where should we eat?",
            "Weekly report - check your metrics"
        ]
        
        email_text = "Which emails are most time-sensitive:\n" + "\n".join(emails)
        result = self.agent.run(email_text)
        
        assert result is not None, "Result should not be None"
        assert any(
            keyword in result.lower() 
            for keyword in ["urgent", "eod", "today", "priority", "critical", "high"]
        ), "Should identify deadline-sensitive email"
        print("✅ Test 3.3 passed: Deadline sensitivity detection")
    
    def test_spam_filtering(self):
        """Test 3.4: Spam vs legitimate email distinction"""
        emails = [
            "CLICK HERE NOW!!! 50% OFF LIMITED TIME",
            "Your quarterly performance review is scheduled",
            "MEGA SALE - BUY MORE!!! LIMITED STOCK",
            "Meeting request: Q4 planning session"
        ]
        
        email_text = "Filter these emails:\n" + "\n".join(emails)
        result = self.agent.run(email_text)
        
        assert result is not None, "Result should not be None"
        print("✅ Test 3.4 passed: Spam filtering capability")
    
    def test_performance_timing(self):
        """Test 3.5: Performance - response time"""
        email = "From boss - Need this urgently"
        
        start_time = time.time()
        result = self.agent.run(email)
        duration = time.time() - start_time
        
        assert result is not None, "Result should not be None"
        assert duration < 60, f"Response should complete within 60s, took {duration:.2f}s"
        print(f"✅ Test 3.5 passed: Performance OK ({duration:.2f}s)")


class TestIntentRouter:
    """Test Suite: Intent Router"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize router"""
        self.router = IntentRouter()
    
    def test_prompt_optimizer_routing(self):
        """Test routing to Prompt Optimizer"""
        queries = [
            "Optimize my prompt",
            "Improve this writing prompt",
            "How do I prompt engineer better?"
        ]
        
        for query in queries:
            routed = self.router.route(query)
            assert routed == "PromptOptimizerAgent", f"Should route to PromptOptimizerAgent, got {routed}"
        
        print("✅ Intent Router Test 1 passed: Prompt Optimizer routing")
    
    def test_career_architect_routing(self):
        """Test routing to Career Architect"""
        queries = [
            "Help me rewrite my resume content",
            "I need to tailor my resume to a job description",
            "Improve my LinkedIn profile - it needs work"
        ]
        
        for query in queries:
            routed = self.router.route(query)
            assert routed == "ContentRewriterAgent", f"Should route to ContentRewriterAgent, got {routed}"
        
        print("✅ Intent Router Test 2 passed: Career Architect routing")
    
    def test_email_prioritizer_routing(self):
        """Test routing to Email Prioritizer"""
        queries = [
            "Prioritize my emails",
            "Which email is most urgent?",
            "Help me organize my inbox"
        ]
        
        for query in queries:
            routed = self.router.route(query)
            assert routed == "EmailPrioritizerAgent", f"Should route to EmailPrioritizerAgent, got {routed}"
        
        print("✅ Intent Router Test 3 passed: Email Prioritizer routing")


class TestSystemIntegration:
    """Integration Tests: Full System"""
    
    def test_complete_workflow_prompt_optimization(self):
        """Test: Complete workflow for prompt optimization"""
        router = IntentRouter()
        query = "Optimize this prompt: write a story"
        
        agent_id = router.route(query)
        assert agent_id == "PromptOptimizerAgent", "Should route correctly"
        
        agent = PromptOptimizerAgent()
        result = agent.run(query)
        
        assert result is not None, "Should return result"
        assert len(result) > 0, "Result should not be empty"
        
        print("✅ Integration Test 1 passed: Complete prompt optimization workflow")
    
    def test_complete_workflow_resume_rewriting(self):
        """Test: Complete workflow for resume rewriting"""
        router = IntentRouter()
        query = "Rewrite my resume for a tech job"
        
        agent_id = router.route(query)
        assert agent_id == "ContentRewriterAgent", "Should route correctly"
        
        agent = ContentRewriterAgent()
        result = agent.run(query)
        
        assert result is not None, "Should return result"
        
        print("✅ Integration Test 2 passed: Complete resume rewriting workflow")
    
    def test_complete_workflow_email_prioritization(self):
        """Test: Complete workflow for email prioritization"""
        router = IntentRouter()
        query = "Prioritize my emails by urgency"
        
        agent_id = router.route(query)
        assert agent_id == "EmailPrioritizerAgent", "Should route correctly"
        
        agent = EmailPrioritizerAgent()
        result = agent.run(query)
        
        assert result is not None, "Should return result"
        
        print("✅ Integration Test 3 passed: Complete email prioritization workflow")


def run_all_tests():
    """Run all tests with summary"""
    print("\n" + "=" * 80)
    print("AGENTFORGE COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    pytest.main([__file__, "-v", "-s", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
