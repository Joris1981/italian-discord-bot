# utils.py
import unicodedata
import re

def normalize(text):
    """
    Normaliseert tekst voor vergelijking:
    - lowercase
    - verwijdert accenten
    - standaardiseert apostroffen
    - verwijdert apostrof voor vergelijking (bv. dov'è == dove e)
    - verwijdert spaties voor leestekens
    - vereenvoudigt spaties
    - laat alleen letters en spaties toe
    """
    # lowercase + accenten strippen
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')  # verwijder accenten

    # apostrof-variaties uniformiseren
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")

    # verwijder apostrof volledig (zodat dov'è ≈ dove e)
    text = text.replace("'", "")

    # spaties voor leestekens verwijderen
    text = re.sub(r'\s+([?.!,;:])', r'\1', text)

    # dubbele spaties -> enkele spatie
    text = re.sub(r'\s+', ' ', text)

    # enkel letters en spaties behouden
    text = re.sub(r'[^a-z ]', '', text)

    return text.strip()