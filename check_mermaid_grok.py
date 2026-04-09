from bs4 import BeautifulSoup
import re
with open("syshoplexe - Grok.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")
for text_node in soup.find_all(string=re.compile(r"graph TD")):
    parent = text_node.parent
    print(f"Parent: {parent.name}, Classes: {parent.get('class', [])}")
    print(f"Content start: {parent.get_text()[:50].replace('\n', ' ')}")
    print("-" * 20)
