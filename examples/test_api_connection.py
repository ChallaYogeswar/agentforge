#!/usr/bin/env python3
"""
API Connection Test
Verifies that Gemini API is properly configured and working.
"""

import os
from src.core.llm import get_llm


def test_api_connection():
    """Test Gemini API connection."""
    
    print("🔗 Testing Gemini API Connection")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not found")
        print("\nTo set it:")
        print("  Windows: set GEMINI_API_KEY=your_key")
        print("  Linux/Mac: export GEMINI_API_KEY='your_key'")
        return False
    
    print("✅ API Key found")
    
    # Test connection
    try:
        print("✅ Initializing LLM...")
        llm = get_llm()
        
        print("✅ Testing API call...")
        response = llm.invoke("Explain what AgentForge is in one sentence.")
        
        print("✅ API connection successful!")
        print(f"\n📝 Response preview:")
        print(f"{response.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API key is correct")
        print("2. Verify internet connection")
        print("3. Check Gemini API quota at https://aistudio.google.com/app/apikey")
        return False


if __name__ == "__main__":
    success = test_api_connection()
    exit(0 if success else 1)
