from bs4 import BeautifulSoup
with open("math-_rizhome audit-_S_crit - DeepSeek.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")
for d in soup.find_all('div', class_='ds-message')[:3]:
    print("ds-message content:", getattr(d, 'text', '')[:100].replace('\n', ' '))
