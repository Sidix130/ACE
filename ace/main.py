import sys
import argparse
from bs4 import BeautifulSoup
from pathlib import Path

from ace.core.sanctuary import SanctuaryManager
from ace.engine.detector import HeuristicDetector
from ace.engine.inferencer import RoleInferrer
from ace.engine.converter import MarkdownDispatcher
from ace.models.chat import Role, Turn, ChatSession, MessagePart, ContentType

def process_html(html_content: str) -> str:
    """Orchestre le pipeline complet d'extraction et de conversion."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Sanctuaire (Extraction & Protection)
    sanctuary = SanctuaryManager()
    mapping = sanctuary.extract(soup)
    
    # 2. Détection des tours
    detector = HeuristicDetector()
    blocks = detector.detect(soup)
    
    # 3. Traitement des tours
    inferrer = RoleInferrer()
    dispatcher = MarkdownDispatcher()
    
    session = ChatSession()
    session.turns = []
    
    for i, block in enumerate(blocks):
        # Inférence du rôle
        role, confidence = inferrer.infer(block, context=session.turns)
        
        # Conversion Markdown (les UUID sont préservés)
        md_content = dispatcher.convert(block)
        
        # Création du tour
        # Dans ACE Light, on stocke tout le contenu du bloc comme une seule MessagePart TEXT
        part = MessagePart(type=ContentType.TEXT, content=md_content)
        turn = Turn(index=i, role=role, content=[part], confidence=confidence)
        session.turns.append(turn)
        
    # 4. Génération du Markdown final
    full_md = ""
    for turn in session.turns:
        role_label = "User" if turn.role == Role.USER else "MODEL"
        full_md += f"## {role_label}\n\n"
        for part in turn.content:
            full_md += part.content + "\n"
        full_md += "\n---\n\n"
        
    # 5. Restauration des UUID
    final_md = sanctuary.restore(full_md, mapping)
    
    # Nettoyage final des espaces superflus (Optionnel)
    final_md = final_md.replace('\n\n\n', '\n\n')
    
    return final_md

def main():
    parser = argparse.ArgumentParser(description="ACE - Adaptive Chat Extractor")
    parser.add_argument("input", help="Fichier HTML source")
    parser.add_argument("output", help="Fichier Markdown de sortie")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Erreur : Le fichier {args.input} n'existe pas.")
        sys.exit(1)
        
    html = input_path.read_text(encoding="utf-8")
    result = process_html(html)
    
    Path(args.output).write_text(result, encoding="utf-8")
    print(f"Conversion terminée : {args.output}")

if __name__ == "__main__":
    main()
