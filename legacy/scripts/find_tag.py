from bs4 import BeautifulSoup
import re

with open("syshoplexe - Grok.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for text in soup.find_all(string=re.compile(r"graph TD")):
    curr = text.parent
    path = []
    while curr:
        classes = ".".join(curr.get('class', [])) if curr.get('class') else ""
        path.append(f"{curr.name}.{classes}" if classes else curr.name)
        curr = curr.parent
    print(" -> ".join(reversed(path)))
