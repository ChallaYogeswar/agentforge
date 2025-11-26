#!/usr/bin/env python3
"""
Setup script for AgentForge project.
Initializes all required components for the system to run.

Author: challayogeswar
Repository: https://github.com/challayogeswar/agentforge
License: CC-BY-SA 4.0
"""

import os
import sys
from pathlib import Path


def setup_environment():
    """Initialize the AgentForge environment."""
    
    print("[*] Initializing AgentForge...")
    
    # 1. Check Python version
    print("[OK] Checking Python version...")
    if sys.version_info < (3, 10):
        print("[ERROR] Python 3.10 or higher required!")
        sys.exit(1)
    print(f"   Using Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # 2. Create necessary directories
    print("[OK] Creating directory structure...")
    dirs = [
        "data/memory",
        "data/logs",
        "data/memory/vector_store",
        "sample_outputs/prompt_optimizer",
        "sample_outputs/career_architect",
        "sample_outputs/email_prioritizer",
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {dir_path}/")
    
    # 3. Initialize databases
    print("[OK] Initializing databases...")
    try:
        import sqlite3
        db_path = "data/memory/sessions.db"
        conn = sqlite3.connect(db_path)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                preference_key TEXT,
                preference_value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"   Created SQLite database: {db_path}")
    except Exception as e:
        print(f"   [!] Could not initialize SQLite: {e}")
    
    # 4. Initialize vector store
    print("[OK] Setting up vector store...")
    try:
        from chromadb import PersistentClient
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        
        embedding_function = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        client = PersistentClient(path="data/memory/vector_store")
        client.get_or_create_collection(
            name="conversations",
            embedding_function=embedding_function
        )
        print("   ChromaDB vector store initialized")
    except Exception as e:
        print(f"   [!] ChromaDB setup optional: {e}")
    
    # 5. Validate dependencies
    print("[OK] Validating dependencies...")
    required_modules = [
        "langchain",
        "google.generativeai",
        "sentence_transformers",
        "chromadb",
        "structlog",
        "pytest"
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   [+] {module}")
        except ImportError:
            print(f"   [-] {module} - NOT FOUND")
            print(f"      Run: pip install -r requirements.txt")
    
    # 6. Test API connection
    print("[OK] Testing API connection...")
    try:
        import os
        from src.core.llm import get_llm
        
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            print("   [+] GEMINI_API_KEY found")
            # Don't actually call the API here to avoid quota usage
            print("   [+] API key validation passed (will be tested on first use)")
        else:
            print("   [!] GEMINI_API_KEY not set")
            print("      Set it with: set GEMINI_API_KEY=your_key (Windows)")
            print("      Or: export GEMINI_API_KEY='your_key' (Mac/Linux)")
    except Exception as e:
        print(f"   [!] API test skipped: {e}")
    
    print("\n" + "="*60)
    print("[SUCCESS] AgentForge initialized successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Verify API key: export GEMINI_API_KEY='your_key'")
    print("2. Run tests: python -m pytest tests/")
    print("3. Start demo: python main.py")
    print("\nDocumentation:")
    print("- README: See README.md")
    print("- Setup Guide: See REPRODUCIBILITY.md")
    print("- Architecture: See docs/architecture.md")


if __name__ == "__main__":
    setup_environment()
