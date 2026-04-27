# tests/test_atom_01a.py
import re
from bs4 import BeautifulSoup
from ace.core.sanctuary import SanctuaryManager

def test_extract_code_basic():
    html = """
    <div>
        <pre><code>print("Hello, world!")</code></pre>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    manager = SanctuaryManager()
    mapping = manager.extract(soup)

    # Vérifier qu'un UUID a été généré
    assert len(mapping) == 1
    uuid_placeholder = list(mapping.keys())[0]
    assert re.match(r'__ACE_CODE_[a-f0-9]{8}__', uuid_placeholder)

    # Vérifier que le contenu extrait est le code Python
    entry = mapping[uuid_placeholder]
    assert 'print("Hello, world!")' in entry.raw_content

    # Vérifier que le placeholder est dans le DOM
    assert uuid_placeholder in str(soup)

def test_restore_code():
    markdown_text = "Voici le code :\n__ACE_CODE_12345678__\nFin."
    mapping = {
        "__ACE_CODE_12345678__": type('Entry', (), {'formatted_content': '```python\nprint("Hello")\n```'})()
    }
    manager = SanctuaryManager()
    restored = manager.restore(markdown_text, mapping)
    assert "```python" in restored
    assert "print(\"Hello\")" in restored
    assert "__ACE_CODE_" not in restored
