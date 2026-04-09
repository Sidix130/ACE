from bs4 import BeautifulSoup
import re

print("==== DEEPSEEK MATH/MERMAID ====")
with open("math-_rizhome audit-_S_crit - DeepSeek.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for t in soup.find_all(string=lambda s: s and ("```mermaid" in s or "math" in s)):
    if "```" in t:
        print("Mermaid Parent classes:", t.parent.name, t.parent.get('class'))

print("\n==== GROK MERMAID ====")
with open("syshoplexe - Grok.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

found = False
for p in soup.find_all():
    if "}}%%" in p.get_text():
        if not found:
            print("Grok Mermaid Container:", p.name, p.get('class'))
            print("Snippet:", repr(p.get_text()[:40]))
        found = True
