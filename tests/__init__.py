"""
AgentForge Test Suite

Comprehensive testing for all three core modules:
- Prompt Optimizer Agent
- Content Rewriter Agent  
- Email Prioritizer Agent

Each module includes 3 test cases = 9 total test cases
"""

import logging
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger("agentforge.tests")
