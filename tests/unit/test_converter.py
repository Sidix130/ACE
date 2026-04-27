# tests/test_atom_04.py
from bs4 import BeautifulSoup
from ace.engine.converter import MarkdownDispatcher

def test_convert_paragraph():
    html = "<p>Un simple paragraphe.</p>"
    soup = BeautifulSoup(html, 'html.parser')
    dispatcher = MarkdownDispatcher()
    md = dispatcher.convert(soup.find('p'))
    assert md.strip() == "Un simple paragraphe."

def test_convert_table():
    html = """
    <table>
        <tr><th>A</th><th>B</th></tr>
        <tr><td>1</td><td>2</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, 'html.parser')
    dispatcher = MarkdownDispatcher()
    md = dispatcher.convert(soup.find('table'))
    assert "| A | B |" in md
    assert "| 1 | 2 |" in md

def test_preserve_sanctuary_uuids():
    """Les placeholders UUID ne doivent pas être modifiés."""
    html = "<p>Texte avec __ACE_CODE_12345678__ intégré.</p>"
    soup = BeautifulSoup(html, 'html.parser')
    dispatcher = MarkdownDispatcher()
    md = dispatcher.convert(soup.find('p'))
    assert "__ACE_CODE_12345678__" in md
