from bs4 import BeautifulSoup
import re

with open("syshoplexe - Grok.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for tag in soup.find_all(True):
    if tag.string and "graph" in tag.string:
        print(f"Found in {tag.name}: {tag.string[:20]}")
    elif tag.get_text() and "graph TD" in tag.get_text():
        # print(f"Found in text of {tag.name}")
        pass

# Rechercher specifiquement les balises script
for s in soup.find_all('script'):
    if s.string and "graph TD" in s.string:
        print(f"Found in SCRIPT: {s.string[:50].replace('\n', ' ')}")
