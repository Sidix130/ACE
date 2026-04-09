from bs4 import Tag, NavigableString
import re

def get_clean_text(tag: Tag) -> str:
    """Extrait le texte d'un tag en le nettoyant des espaces superflus."""
    return tag.get_text(separator=" ", strip=True)

def is_ui_element(tag: Tag) -> bool:
    """Détermine si un tag est probablement un élément d'interface (bouton, menu, etc.)."""
    ui_keywords = ["button", "nav", "footer", "header", "menu", "tooltip", "copy"]
    classes = tag.get("class", [])
    if isinstance(classes, str): classes = [classes]
    
    # Vérification par classe
    for cls in classes:
        if any(kw in cls.lower() for kw in ui_keywords):
            return True
            
    # Vérification par nom de tag
    if tag.name in ["button", "nav", "footer", "header"]:
        return True
        
    return False

def is_empty_node(tag: Tag) -> bool:
    """Vérifie si un nœud est vide ou ne contient que des espaces."""
    return not tag.get_text(strip=True)
