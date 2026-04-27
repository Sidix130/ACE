# tests/test_v1_1_0.py
from bs4 import BeautifulSoup
from ace.engine.converter import MarkdownDispatcher
from ace.main import process_html

def test_convert_blockquote():
    html = "<blockquote>Citation</blockquote>"
    soup = BeautifulSoup(html, 'html.parser')
    dispatcher = MarkdownDispatcher()
    md = dispatcher.convert(soup.find('blockquote'))
    assert md.strip() == "> Citation"

def test_convert_link():
    html = '<a href="https://example.com">Lien</a>'
    soup = BeautifulSoup(html, 'html.parser')
    dispatcher = MarkdownDispatcher()
    md = dispatcher.convert(soup.find('a'))
    assert md.strip() == "[Lien](https://example.com)"

def test_convert_image():
    html = '<img src="img.png" alt="Alt">'
    soup = BeautifulSoup(html, 'html.parser')
    dispatcher = MarkdownDispatcher()
    md = dispatcher.convert(soup.find('img'))
    assert md.strip() == "![Alt](img.png)"

def test_v1_1_0_pipeline_fidelity():
    """Vérifie que le pipeline complet traite correctement les nouveaux éléments."""
    html = """
    <div class="message">
        <blockquote>Expert ACE.</blockquote>
        <p>Visitez <a href="https://ace.ai">notre site</a> et voyez <img src="icon.png" alt="Logo"></p>
    </div>
    """
    result = process_html(html)
    content = result.content
    
    assert "> Expert ACE." in content
    assert "[notre site](https://ace.ai)" in content
    assert "![Logo](icon.png)" in content
    assert "Expert ACE." in result.session.turns[0].content[0].content
