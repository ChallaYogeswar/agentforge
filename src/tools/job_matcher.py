# src/tools/job_matcher.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2))

def match_score(resume_text: str, job_description: str) -> float:
    vectors = vectorizer.fit_transform([resume_text, job_description])
    return float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])