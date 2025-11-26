# src/tools/keyword_extractor.py
from rake_nltk import Rake
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

rake = Rake()

def extract_keywords(text: str, top_k: int = 10) -> list[str]:
    rake.extract_keywords_from_text(text)
    return rake.get_ranked_phrases()[:top_k]