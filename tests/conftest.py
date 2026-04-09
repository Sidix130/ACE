# tests/conftest.py
import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture
def grok_mermaid_html():
    """Fragment HTML contenant un diagramme Mermaid avec préfixe }}%% (style Grok)."""
    return (FIXTURES_DIR / "grok_mermaid_sample.html").read_text(encoding="utf-8")

@pytest.fixture
def deepseek_latex_html():
    """Fragment HTML contenant du KaTeX/LaTeX (style DeepSeek)."""
    return (FIXTURES_DIR / "deepseek_latex_sample.html").read_text(encoding="utf-8")

@pytest.fixture
def generic_chat_html():
    """Structure de chat simple avec deux messages (User/Assistant)."""
    return (FIXTURES_DIR / "generic_chat_sample.html").read_text(encoding="utf-8")

@pytest.fixture
def ai_studio_complex_html():
    """Export AI Studio avec conteneurs complexes (multi-paragraphes)."""
    return (FIXTURES_DIR / "complex_ai_studio_sample.html").read_text(encoding="utf-8")
