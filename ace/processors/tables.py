from bs4 import Tag

def convert_table(table_tag: Tag) -> str:
    """Convertit un tag table BS4 en Markdown GFM."""
    rows = table_tag.find_all('tr')
    if not rows:
        return ""

    md_rows = []
    
    # Extraction de l'entête
    header_row = rows[0]
    headers = [cell.get_text(strip=True) for cell in header_row.find_all(['th', 'td'])]
    
    md_rows.append("| " + " | ".join(headers) + " |")
    md_rows.append("| " + " | ".join(["---"] * len(headers)) + " |")
    
    # Données (en sautant l'entête)
    for row in rows[1:]:
        cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
        # Ajuster si le nombre de cellules diffère
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))
        md_rows.append("| " + " | ".join(cells[:len(headers)]) + " |")
        
    return "\n" + "\n".join(md_rows) + "\n"
