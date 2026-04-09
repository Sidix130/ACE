from bs4 import BeautifulSoup
import re
with open("syshoplexe - Grok.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")
for node in soup.find_all(string=re.compile(r"graph", re.I)):
    if "graph TD" in node or "graph LR" in node:
        p = node.parent
        print(f"Parent: {p.name}, Classes: {p.get('class', [])}")
        print(f"Grand-parent: {p.parent.name}, GP Classes: {p.parent.get('class', [])}")
        print("-" * 20)
