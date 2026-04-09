from bs4 import BeautifulSoup
with open("math-_rizhome audit-_S_crit - DeepSeek.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")
nodes = list(soup.find_all(string=lambda s: s and ("```mermaid" in s)))
for t in nodes:
    curr = t
    path = []
    while curr.parent:
        p = curr.parent
        classes = p.get('class', []) if p.name else []
        path.append(f"{p.name}.{'.'.join(classes)}")
        curr = p
    print("Path to mermaid:", " > ".join(path[:10]))
