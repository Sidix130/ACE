# tests/test_atom_02.py
from bs4 import BeautifulSoup
from ace.engine.detector import TopologicalDetector

def test_detect_turns_generic(generic_chat_html):
    """Vérifie que les conteneurs de messages sont correctement identifiés."""
    soup = BeautifulSoup(generic_chat_html, 'html.parser')
    detector = TopologicalDetector()
    blocks = detector.detect(soup)

    # La fixture contient 2 messages (User + Assistant)
    assert len(blocks) == 2, f"Expected 2 turns, got {len(blocks)}"

def test_detect_turns_ai_studio_complex(ai_studio_complex_html):
    """Teste sur un export AI Studio avec de nombreux wrappers."""
    soup = BeautifulSoup(ai_studio_complex_html, 'html.parser')
    detector = TopologicalDetector()
    blocks = detector.detect(soup)

    # On attend au moins 2 tours
    assert len(blocks) >= 2, "Pas assez de tours détectés dans l'export complexe"

    # Vérification basique : chaque bloc doit contenir du texte
    for block in blocks:
        assert len(block.get_text(strip=True)) > 5, "Bloc détecté presque vide"

def test_structural_clustering():
    """Vérifie que le clustering regroupe les éléments de même signature."""
    html = """
    <div id="parent">
        <div class="msg">Hello</div>
        <div class="msg">Hi there</div>
        <div class="other">Sidebar</div>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    detector = TopologicalDetector(min_density=1)
    # On force la détection
    blocks = detector.detect(soup)
    # Devrait regrouper les deux 'msg' car ils ont la même signature
    assert len(blocks) == 2
    assert all('msg' in str(b) for b in blocks)
