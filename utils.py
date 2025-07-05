# utils.py
import unicodedata
import re

def normalize(text):
    """
    Normaliseert tekst voor vergelijking: lowercase, verwijdert accenten,
    vereenvoudigt spaties en vervangt variaties op apostrof.
    """
    text = unicodedata.normalize("NFKD", text).lower().strip()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = re.sub(r"\s*'\s*", "'", text)
    text = re.sub(r"[^a-zàèéìòù' ]", "", text)
    return text