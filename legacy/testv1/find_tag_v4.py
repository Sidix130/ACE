from bs4 import BeautifulSoup
import re

with open("syshoplexe - Grok.html", "r", encoding="utf-8") as f:
    content = f.read()
    print(f"File length: {len(content)}")
    soup = BeautifulSoup(content, "html.parser")

for text in soup.find_all(string=True):
    if "PENSEUR" in text:
        print(f"Found in {text.parent.name}")
        print(f"Classes: {text.parent.get('class')}")
        print(f"Text content: {text[:50].replace('\n', ' ')}")
