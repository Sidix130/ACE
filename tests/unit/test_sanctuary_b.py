# tests/test_atom_01b.py
import re
from bs4 import BeautifulSoup
from ace.core.sanctuary import SanctuaryManager

def test_extract_mermaid_grok(grok_mermaid_html):
    """Teste l'extraction d'un diagramme Mermaid avec préfixe }}%% (export Grok)."""
    soup = BeautifulSoup(grok_mermaid_html, 'html.parser')
    manager = SanctuaryManager()
    mapping = manager.extract(soup)

    # Au moins une entrée Mermaid doit être trouvée
    mermaid_uuids = [uid for uid, entry in mapping.items() if entry.type == "mermaid"]
    assert len(mermaid_uuids) == 1, "Aucun diagramme Mermaid extrait"

    entry = mapping[mermaid_uuids[0]]
    # Vérifier que le contenu commence par un mot-clé Mermaid (après nettoyage)
    cleaned = re.sub(r'^(}}%%|%%{.*?}%%)', '', entry.raw_content).strip()
    assert cleaned.startswith(('graph', 'flowchart', 'sequenceDiagram')), \
        f"Contenu extrait: {entry.raw_content[:100]}"

def test_extract_latex_deepseek(deepseek_latex_html):
    """Teste l'extraction de LaTeX (KaTeX) dans un export DeepSeek."""
    soup = BeautifulSoup(deepseek_latex_html, 'html.parser')
    manager = SanctuaryManager()
    mapping = manager.extract(soup)

    math_uuids = [uid for uid, entry in mapping.items() if entry.type == "math"]
    assert len(math_uuids) >= 1, "Aucune formule mathématique extraite"

    # Vérifier que le contenu contient des délimiteurs LaTeX
    entry = mapping[math_uuids[0]]
    assert '$' in entry.formatted_content or '\\(' in entry.raw_content

def test_restore_mermaid():
    markdown = "Avant\n__ACE_MERM_abcdef12__\nAprès"
    mapping = {
        "__ACE_MERM_abcdef12__": type('Entry', (), {
            'type': 'mermaid',
            'formatted_content': '```mermaid\ngraph TD\nA-->B\n```'
        })()
    }
    manager = SanctuaryManager()
    restored = manager.restore(markdown, mapping)
    assert "```mermaid" in restored
    assert "graph TD" in restored
