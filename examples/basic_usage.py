#!/usr/bin/env python3
"""
Basic usage example for AgentForge.
Demonstrates how to use the Intent Router with all three modules.
"""

import os
from src.core.intent_router import IntentRouter


def main():
    """Run basic usage examples."""
    
    print("🎯 AgentForge - Basic Usage Examples")
    print("=" * 60)
    
    # Initialize router
    router = IntentRouter()
    
    # Example 1: Prompt Optimizer
    print("\n📝 Example 1: Prompt Optimizer")
    print("-" * 60)
    prompt1 = "Optimize this prompt: Write a story about a robot"
    print(f"Input: {prompt1}\n")
    
    try:
        result1 = router.route(prompt1)
        print(f"Routed to: {result1}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Career Architect (Content Rewriter)
    print("\n📄 Example 2: Career Architect (Content Rewriter)")
    print("-" * 60)
    prompt2 = "Rewrite this resume bullet for a senior engineer role: Worked on Python projects"
    print(f"Input: {prompt2}\n")
    
    try:
        result2 = router.route(prompt2)
        print(f"Routed to: {result2}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Email Prioritizer
    print("\n📧 Example 3: Email Prioritizer")
    print("-" * 60)
    prompt3 = "Prioritize these emails: URGENT: Server down, Meeting reminder, Newsletter"
    print(f"Input: {prompt3}\n")
    
    try:
        result3 = router.route(prompt3)
        print(f"Routed to: {result3}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
