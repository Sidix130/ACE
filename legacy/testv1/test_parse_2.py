from bs4 import BeautifulSoup

with open("syshoplexe - Grok.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for t in soup.find_all(string=lambda s: s and "%%{init" in s):
    p = t.parent
    print("Grok Mermaid Parent:", p.name)
    print("Classes:", p.get('class'))
    print("Attributes:", p.attrs)

with open("math-_rizhome audit-_S_crit - DeepSeek.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for t in soup.find_all(string=lambda s: s and "math" in s):
    # Just look at katex implementation details
    pass
for katex in soup.find_all(class_="katex"):
    print("Found katex node:", katex.name)
    annotation = katex.find("annotation")
    if annotation:
        print("Got annotation:", annotation.get_text()[:40])
    break
