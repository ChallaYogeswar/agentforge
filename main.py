#!/usr/bin/env python3
"""
AgentForge Main Entry Point
Consolidated script combining CLI, testing, and smoke test functionality.

Author: challayogeswar
Repository: https://github.com/challayogeswar/agentforge
License: CC-BY-SA 4.0

Usage:
    python main.py              # Interactive CLI mode
    python main.py --test       # Run full E2E tests with metrics
    python main.py --smoke      # Run quick smoke tests
    python main.py --help       # Show help
"""

import sys
import json
import argparse
import traceback
import logging
import time
from pathlib import Path
from typing import Dict, List, Any

# Fix for Windows PowerShell encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("agentforge")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# ============================================================================
# METRICS COLLECTION
# ============================================================================

class TestMetricsCollector:
    """Collects comprehensive metrics from test runs"""
    
    def __init__(self):
        self.tests = []
        self.start_time = None
        self.end_time = None
    
    def start_test(self, module: str, test_name: str):
        """Start timing a test"""
        return {
            "module": module,
            "test_name": test_name,
            "start_time": time.time(),
            "status": None,
            "duration": None,
            "error": None
        }
    
    def end_test(self, test_data: Dict, status: str = "PASS", error: str = None, duration: float = None):
        """End timing a test and record result"""
        if duration is None:
            duration = time.time() - test_data["start_time"]
        
        test_data["status"] = status
        test_data["duration"] = duration
        test_data["error"] = error
        self.tests.append(test_data)
        return test_data
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        passed = sum(1 for t in self.tests if t["status"] == "PASS")
        failed = sum(1 for t in self.tests if t["status"] == "FAIL")
        total = len(self.tests)
        
        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": round((passed / total * 100) if total > 0 else 0, 2),
            "avg_duration": round(sum(t["duration"] for t in self.tests) / total if total > 0 else 0, 2),
            "total_duration": round(sum(t["duration"] for t in self.tests), 2)
        }
        
        # Per-module stats
        modules = {}
        for test in self.tests:
            mod = test["module"]
            if mod not in modules:
                modules[mod] = {"tests": 0, "passed": 0, "failed": 0}
            modules[mod]["tests"] += 1
            if test["status"] == "PASS":
                modules[mod]["passed"] += 1
            else:
                modules[mod]["failed"] += 1
        
        summary["by_module"] = modules
        return summary
    
    def export_results(self, filepath: Path):
        """Export results to JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "tests": self.tests,
            "summary": self.get_summary(),
            "timestamp": time.time()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Test results exported to {filepath}")


def build_agents(user_id: str = "agentforge_user"):
    """Build and return all 3 agents and the intent router."""
    from src.core.intent_router import IntentRouter
    from src.agents.prompt_optimizer import PromptOptimizerAgent
    from src.agents.content_optimizer import ContentRewriterAgent
    from src.agents.email_prioritizer import EmailPrioritizerAgent

    agents = {
        "PromptOptimizerAgent": PromptOptimizerAgent(user_id),
        "ContentRewriterAgent": ContentRewriterAgent(user_id),
        "EmailPrioritizerAgent": EmailPrioritizerAgent(user_id),
    }

    router = IntentRouter()
    return agents, router


# ============================================================================
# INTERACTIVE CLI MODE
# ============================================================================

def run_interactive_cli():
    """Run the interactive CLI for agent interaction."""
    print("\n" + "="*80)
    print("AgentForge Productivity Suite v1.0 - Interactive Mode")
    print("="*80)
    print("Type 'exit', 'quit', or 'bye' to stop\n")

    agents, router = build_agents()

    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nThank you for using AgentForge!")
                break

            target_agent_name = router.route(user_input)

            if target_agent_name not in agents:
                print(f"\nNo agent found for that request. Router said: {target_agent_name}\n")
                continue

            print(f"\nRouting to: {target_agent_name}")
            response = agents[target_agent_name].run(user_input)

            # Pretty print if JSON
            try:
                parsed = json.loads(response)
                print(json.dumps(parsed, indent=2))
            except:
                print(response)
            print("\n" + "-" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            logger.error(traceback.format_exc())


# ============================================================================
# SMOKE TEST MODE (Quick validation)
# ============================================================================

def run_smoke_test():
    """Quick smoke test: instantiate agents and call their run method."""
    print("\n" + "="*80)
    print("SMOKE TEST - Quick Validation")
    print("="*80)

    agents, router = build_agents(user_id="smoke_test_user")
    metrics = TestMetricsCollector()

    test_cases = {
        "PromptOptimizerAgent": "Improve this prompt: write a funny tweet about coffee",
        "ContentRewriterAgent": "Here is my resume: worked at company X. Improve bullets.",
        "EmailPrioritizerAgent": "Subject: Meeting\nFrom: boss@example.com\nBody: Can you prepare slides?",
    }

    results = {}
    
    for agent_name, test_input in test_cases.items():
        print(f"\n[TEST] {agent_name}...")
        test_data = metrics.start_test("smoke", agent_name)
        
        if agent_name not in agents:
            print(f"[FAIL] Agent not found: {agent_name}")
            metrics.end_test(test_data, status="FAIL", error="Agent not found")
            results[agent_name] = False
            continue

        try:
            agent = agents[agent_name]
            output = agent.run(test_input)
            duration = time.time() - test_data["start_time"]
            print(f"[PASS] Response received ({len(output)} chars in {duration:.2f}s)")
            metrics.end_test(test_data, status="PASS", duration=duration)
            results[agent_name] = True
        except Exception as e:
            duration = time.time() - test_data["start_time"]
            print(f"[FAIL] Error: {e}")
            metrics.end_test(test_data, status="FAIL", error=str(e), duration=duration)
            results[agent_name] = False

    # Summary
    print("\n" + "="*80)
    print("SMOKE TEST SUMMARY")
    print("="*80)
    
    summary = metrics.get_summary()
    for agent_name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status}: {agent_name}")
    
    print(f"\nResult: {summary['passed']}/{summary['total']} tests passed")
    print(f"Success Rate: {summary['success_rate']}%")
    
    # Export metrics
    metrics_file = project_root / "data" / "test_metrics_smoke.json"
    metrics.export_results(metrics_file)
    
    return all(results.values())


# ============================================================================
# FULL E2E TEST MODE (Comprehensive testing with metrics)
# ============================================================================

def run_full_test():
    """Run comprehensive end-to-end tests with detailed metrics."""
    print("\n" + "="*80)
    print("FULL E2E TEST - Comprehensive Validation with Metrics")
    print("="*80)

    agents, router = build_agents(user_id="e2e_test_user")
    metrics = TestMetricsCollector()

    test_suite = {
        "Prompt Optimizer": {
            "agent": "PromptOptimizerAgent",
            "input": "Optimize this prompt: a photo of a happy shiba inu puppy playing in autumn leaves, studio lighting, cinematic"
        },
        "Content Rewriter": {
            "agent": "ContentRewriterAgent",
            "input": """Here is my resume: Software Engineer with 5 years experience in Python and JavaScript, 
expertise in distributed systems and cloud infrastructure. 

And here is the job I want: We're looking for a Senior Backend Engineer with 
strong experience in Python, REST APIs, and cloud deployment. 
Tailor my resume to this job perfectly."""
        },
        "Email Prioritizer": {
            "agent": "EmailPrioritizerAgent",
            "input": """--- Email 1 ---
From: boss@company.com
Subject: URGENT - Client demo tomorrow

--- Email 2 ---
From: newsletter@medium.com
Subject: Daily Digest

--- Email 3 ---
From: hr@google.com
Subject: Interview next week - preparation materials"""
        }
    }

    results = {}

    for test_name, test_config in test_suite.items():
        print(f"\n{'='*80}")
        print(f"TEST: {test_name}")
        print(f"{'='*80}")

        agent_name = test_config["agent"]
        test_input = test_config["input"]
        test_data = metrics.start_test(agent_name, test_name)

        if agent_name not in agents:
            print(f"[FAIL] Agent not found: {agent_name}")
            metrics.end_test(test_data, status="FAIL", error="Agent not found")
            results[test_name] = False
            continue

        try:
            agent = agents[agent_name]
            logger.info(f"Running {agent_name}...")
            
            response = agent.run(test_input)
            duration = time.time() - test_data["start_time"]
            
            print(f"[PASS] {test_name} completed successfully")
            print(f"Response: {len(response)} chars in {duration:.2f}s")
            print(f"Preview: {response[:200]}...\n")
            
            metrics.end_test(test_data, status="PASS", duration=duration)
            results[test_name] = True
            
        except Exception as e:
            duration = time.time() - test_data["start_time"]
            print(f"[FAIL] {test_name} failed:")
            print(traceback.format_exc())
            metrics.end_test(test_data, status="FAIL", error=str(e), duration=duration)
            results[test_name] = False

    # Final Summary
    print("\n" + "="*80)
    print("FULL TEST SUMMARY")
    print("="*80)
    
    summary = metrics.get_summary()
    for test_name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {summary['passed']}/{summary['total']} tests passed")
    print(f"Success Rate: {summary['success_rate']}%")
    print(f"Total Duration: {summary['total_duration']}s")
    print(f"Average Duration per Test: {summary['avg_duration']}s")
    
    # Module breakdown
    if summary['by_module']:
        print("\nBy Module:")
        for module, stats in summary['by_module'].items():
            print(f"  {module}: {stats['passed']}/{stats['tests']} passed")
    
    # Export metrics
    metrics_file = project_root / "data" / "test_metrics_full.json"
    metrics.export_results(metrics_file)
    print(f"\n📊 Metrics exported to: {metrics_file}")
    
    return all(results.values())


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="AgentForge - Multi-Agent Productivity Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Interactive CLI mode
  python main.py --test       # Full E2E tests with metrics
  python main.py --smoke      # Quick smoke tests
  python main.py --help       # Show this help
        """
    )
    
    parser.add_argument(
        '--test', 
        action='store_true', 
        help='Run full end-to-end tests with metrics collection'
    )
    
    parser.add_argument(
        '--smoke', 
        action='store_true', 
        help='Run quick smoke tests'
    )

    args = parser.parse_args()

    try:
        if args.test:
            success = run_full_test()
            sys.exit(0 if success else 1)
        elif args.smoke:
            success = run_smoke_test()
            sys.exit(0 if success else 1)
        else:
            # Default: Interactive mode
            run_interactive_cli()
            sys.exit(0)
            
    except Exception as e:
        print(f"\nFatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
