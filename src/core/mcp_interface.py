# src/core/mcp_interface.py
from langchain.tools import StructuredTool
from src.tools.keyword_extractor import extract_keywords
from src.tools.job_matcher import match_score

tools = [
    StructuredTool.from_function(
        func=extract_keywords,
        name="extract_keywords",
        description="Extract top keywords/phrases from any text. Use before rewriting content."
    ),
    StructuredTool.from_function(
        func=match_score,
        name="job_match_score",
        description="Returns cosine similarity score between resume and job description (0.0 to 1.0)"
    )
]

tool_map = {tool.name: tool for tool in tools}