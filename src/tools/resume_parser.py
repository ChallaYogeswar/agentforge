# src/tools/resume_parser.py
import re

def extract_sections(resume_text: str) -> dict:
    sections = {
        "summary": "",
        "experience": [],
        "skills": [],
        "education": ""
    }
    
    lines = resume_text.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if line.lower().startswith(('summary', 'profile', 'objective')):
            current_section = "summary"
        elif line.lower().startswith(('experience', 'work history', 'employment')):
            current_section = "experience"
        elif line.lower().startswith(('skills', 'technical skills')):
            current_section = "skills"
        elif line.lower().startswith(('education', 'academic')):
            current_section = "education"
        else:
            if current_section == "experience" and line and len(line) > 10:
                sections["experience"].append(line)
            elif current_section == "skills" and line:
                sections["skills"].extend([s.strip() for s in line.split(',')])
            elif current_section:
                sections[current_section] += line + " "
    
    return sections