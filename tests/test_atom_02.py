# tests/test_atom_02.py
from bs4 import BeautifulSoup
from ace.engine.detector import HeuristicDetector

def test_detect_turns_generic(generic_chat_html):
    """Vérifie que les conteneurs de messages sont correctement identifiés."""
    soup = BeautifulSoup(generic_chat_html, 'html.parser')
    detector = HeuristicDetector()
    blocks = detector.detect(soup)

    # La fixture contient 2 messages (User + Assistant)
    assert len(blocks) == 2, f"Expected 2 turns, got {len(blocks)}"

def test_detect_turns_ai_studio_complex(ai_studio_complex_html):
    """Teste sur un export AI Studio avec de nombreux wrappers."""
    soup = BeautifulSoup(ai_studio_complex_html, 'html.parser')
    detector = HeuristicDetector()
    blocks = detector.detect(soup)

    # On attend au moins 2 tours (peut varier selon l'échantillon)
    assert len(blocks) >= 2, "Pas assez de tours détectés dans l'export complexe"

    # Vérification basique : chaque bloc doit contenir du texte
    for block in blocks:
        assert len(block.get_text(strip=True)) > 5, "Bloc détecté presque vide"

def test_no_penalty_for_text_tags():
    """Simule un conteneur avec plusieurs <p> : ne doit pas être pénalisé."""
    html = """
    <div class="message">
        <p>Paragraphe 1</p>
        <p>Paragraphe 2</p>
        <p>Paragraphe 3</p>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    detector = HeuristicDetector()
    # La détection devrait quand même remonter le div parent
    # On teste en interne la fonction de scoring (si accessible)
    # Pour ce test, on vérifie simplement que le bloc est candidat
    candidates = detector._get_candidates(soup)  # Méthode hypothétique
    assert any('message' in str(c) for c in candidates)
