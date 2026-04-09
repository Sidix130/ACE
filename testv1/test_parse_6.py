from bs4 import BeautifulSoup
from clean import detect_turn_blocks

def main():
    with open("math-_rizhome audit-_S_crit - DeepSeek.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    blocks = detect_turn_blocks(soup)
    print(f"Detected {len(blocks)} blocks")
    for i, b in enumerate(blocks[:5]):
        classes = b.get('class', [])
        print(f"Block {i}: {b.name}.{'.'.join(classes)} -> len text: {len(b.get_text())}")

if __name__ == "__main__":
    main()
