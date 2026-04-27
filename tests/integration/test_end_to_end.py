# tests/test_atom_05.py
from ace.main import process_html
from ace.models.chat import ChatSession

def test_end_to_end_generic(generic_chat_html):
    """Test complet de l'extraction jusqu'au Markdown."""
    result = process_html(generic_chat_html)
    content = result.content
    assert "## User" in content or "## MODEL" in content
    assert "Bonjour" in content

def test_end_to_end_preserves_mermaid(grok_mermaid_html):
    """Vérifie que le diagramme Mermaid est intact en sortie."""
    result = process_html(grok_mermaid_html)
    content = result.content
    assert "```mermaid" in content
    assert "graph TD" in content
