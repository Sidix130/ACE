# tests/test_atom_05.py
from ace.main import process_html
from ace.models.chat import ChatSession

def test_end_to_end_generic(generic_chat_html):
    """Test complet de l'extraction jusqu'au Markdown."""
    result = process_html(generic_chat_html)  # Retourne une ChatSession ou un str Markdown ?
    # Selon l'implémentation, process_html peut retourner le Markdown final
    # Adaptez selon votre interface.
    assert "## User" in result or "## MODEL" in result
    assert "Bonjour" in result

def test_end_to_end_preserves_mermaid(grok_mermaid_html):
    """Vérifie que le diagramme Mermaid est intact en sortie."""
    result = process_html(grok_mermaid_html)
    assert "```mermaid" in result
    assert "graph TD" in result
