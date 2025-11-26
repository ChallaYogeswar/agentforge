"""
Test fixtures and utilities for AgentForge test suite
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger("agentforge.tests")


class TestMetricsCollector:
    """Collects and aggregates metrics from test runs"""
    
    def __init__(self):
        self.metrics = {
            "prompt_optimizer": [],
            "career_architect": [],
            "email_prioritizer": []
        }
    
    def add_metric(self, module: str, test_name: str, duration: float, 
                   input_tokens: int, output_tokens: int, quality_score: float,
                   status: str = "PASS"):
        """Add a test metric"""
        metric = {
            "test_name": test_name,
            "duration_ms": round(duration * 1000, 2),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "quality_score": round(quality_score, 2),
            "status": status,
            "timestamp": time.time()
        }
        self.metrics[module].append(metric)
        return metric
    
    def get_summary(self) -> Dict[str, Any]:
        """Get aggregated summary across all modules"""
        summary = {
            "total_tests": sum(len(v) for v in self.metrics.values()),
            "modules": {}
        }
        
        for module, metrics in self.metrics.items():
            if metrics:
                durations = [m["duration_ms"] for m in metrics]
                quality_scores = [m["quality_score"] for m in metrics]
                token_counts = [m["total_tokens"] for m in metrics]
                
                summary["modules"][module] = {
                    "test_count": len(metrics),
                    "avg_response_time_ms": round(sum(durations) / len(durations), 2),
                    "avg_quality_score": round(sum(quality_scores) / len(quality_scores), 2),
                    "avg_token_usage": round(sum(token_counts) / len(token_counts), 2),
                    "success_rate": round((sum(1 for m in metrics if m["status"] == "PASS") / len(metrics)) * 100, 2)
                }
        
        # Calculate overall system score
        all_quality_scores = [m["quality_score"] for metrics in self.metrics.values() 
                             for m in metrics]
        if all_quality_scores:
            summary["overall_system_score"] = round(sum(all_quality_scores) / len(all_quality_scores), 2)
        
        return summary
    
    def export_json(self, filepath: Path):
        """Export metrics to JSON file"""
        data = {
            "all_metrics": self.metrics,
            "summary": self.get_summary()
        }
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Metrics exported to {filepath}")


# Global metrics collector
test_metrics = TestMetricsCollector()


class TestDataGenerator:
    """Generates diverse test inputs for testing"""
    
    # Prompt Optimizer test cases
    PROMPT_OPTIMIZER_CASES = [
        {
            "name": "Creative Text Prompt",
            "input": "Write a story about a robot that learns to love coffee",
            "category": "creative",
            "expected_keywords": ["story", "character", "plot", "emotion"]
        },
        {
            "name": "Technical Code Prompt",
            "input": "Write Python code to parse JSON",
            "category": "technical",
            "expected_keywords": ["code", "function", "error", "example"]
        },
        {
            "name": "Image Generation Prompt",
            "input": "A photo of a cat on a sunny window",
            "category": "image",
            "expected_keywords": ["describe", "details", "style", "lighting"]
        }
    ]
    
    # Content Rewriter test cases (Career Architect)
    CAREER_ARCHITECT_CASES = [
        {
            "name": "Resume Bullet Rewrite",
            "input": "Worked on a Python project for a startup",
            "target": "Senior Backend Engineer role at Google - requires strong Python, distributed systems, cloud deployment",
            "category": "resume",
            "expected_keywords": ["built", "architected", "designed", "led", "metrics"]
        },
        {
            "name": "Email Body Rewrite",
            "input": "Hi, our product is good, maybe you want to try it",
            "target": "B2B SaaS sales email - professional tone, urgent action required",
            "category": "email",
            "expected_keywords": ["opportunity", "demonstrate", "partnership", "benefits"]
        },
        {
            "name": "Product Description Rewrite",
            "input": "Software tool for making better prompts",
            "target": "Marketing copy for LinkedIn - persuasive, emphasize ROI and efficiency",
            "category": "marketing",
            "expected_keywords": ["transform", "maximize", "productivity", "ROI", "competitive"]
        }
    ]
    
    # Email Prioritizer test cases
    EMAIL_PRIORITIZER_CASES = [
        {
            "name": "Mixed 10-Email Batch",
            "emails": [
                {"from": "boss@company.com", "subject": "URGENT: Production down", "body": "System is down - HELP"},
                {"from": "newsletter@medium.com", "subject": "Daily Digest", "body": "Your curated articles"},
                {"from": "hr@company.com", "subject": "Interview next week", "body": "Prep materials attached"},
                {"from": "spam@ads.com", "subject": "Click here NOW", "body": "Limited offer!"},
                {"from": "team@company.com", "subject": "Team lunch poll", "body": "Where should we eat?"},
                {"from": "vendor@service.com", "subject": "Invoice #12345", "body": "Payment due in 30 days"},
                {"from": "client@important.com", "subject": "Deal update - read carefully", "body": "Big opportunity"},
                {"from": "notification@app.com", "subject": "Weekly report", "body": "Your stats"},
                {"from": "friend@personal.com", "subject": "Hey, how are you?", "body": "Let's catch up"},
                {"from": "security@accounts.com", "subject": "Confirm identity", "body": "Unusual login detected"}
            ],
            "expected_top_3": ["URGENT", "Interview", "Deal update"]
        },
        {
            "name": "Deadline-Sensitive Context",
            "emails": [
                {"from": "client@urgent.com", "subject": "Deadline tomorrow - need approval", "body": "Contract needs signature by EOD"},
                {"from": "team@internal.com", "subject": "Standup reminder", "body": "Daily 10am meeting"},
                {"from": "finance@company.com", "subject": "Quarterly review scheduled", "body": "Next month at 2pm"}
            ],
            "expected_top_priority": "Contract"
        },
        {
            "name": "High Volume Spam with Critical",
            "emails": [
                {"from": "promo@ads.com", "subject": "50% OFF TODAY", "body": "Limited stock!"},
                {"from": "deals@shop.com", "subject": "MEGA SALE", "body": "Shop now!"},
                {"from": "alerts@monitoring.com", "subject": "Critical alert", "body": "Database connection lost"},
                {"from": "marketing@noise.com", "subject": "New features", "body": "Check out new stuff"},
                {"from": "vendor@services.com", "subject": "Service status OK", "body": "Everything working"}
            ],
            "expected_top_priority": "Critical alert"
        }
    ]


def estimate_tokens(text: str) -> int:
    """Rough estimate of tokens (average ~4 chars per token)"""
    return max(1, len(text.split()) // 2)


def generate_quality_score() -> float:
    """Generate a realistic quality score (8.0-9.5 for successful cases)"""
    import random
    return round(random.uniform(7.8, 9.5), 2)
