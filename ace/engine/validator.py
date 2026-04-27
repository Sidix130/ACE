from bs4 import BeautifulSoup, Tag
from typing import List
from ace.engine.inferencer import RoleInferrer

class ExtractionValidator:
    """
    Validateur transverse chargé de s'assurer qu'un ensemble de blocs candidats 
    constitue véritablement une conversation extraite et non un faux positif.
    Ce validateur est la clé de voûte de l'architecture V1.2.0.
    """
    def __init__(self, min_coverage: float = 0.15):
        self.min_coverage = min_coverage
        self.inferrer = RoleInferrer()

    def _get_word_count(self, text: str) -> int:
        return len(text.split())

    def _get_depth(self, element: Tag) -> int:
        return len(list(element.parents))

    def is_valid(self, blocks: List[Tag], soup: BeautifulSoup) -> bool:
        """
        Évalue la validité algorithmique et structurelle d'une liste de blocs.
        Retourne True si c'est une conversation considérée valide, False sinon (autorisant un fallback).
        """
        if not blocks:
            return False
            
        body = soup.find('body')
        if not body:
            return False
            
        total_words = self._get_word_count(body.get_text(strip=True))
        if total_words == 0:
            return False # Pas de contenu texte dans la page
        
        # 1. Test du wrapper unique (Anti-wrapper massif)
        if len(blocks) == 1:
            block = blocks[0]
            depth = self._get_depth(block)
            block_words = self._get_word_count(block.get_text(strip=True))
            coverage = block_words / total_words
            
            # Rejet absolu du conteneur géant
            if depth < 3 and coverage > 0.7:
                return False
                
        # 2. Test de conversation minimale (Alternance des rôles)
        if len(blocks) >= 2:
            roles = set()
            for b in blocks:
                role, _ = self.inferrer.infer(b, context=[])
                roles.add(role)
            
            # Si on a plusieurs blocs mais qu'absolument tous sont du même type,
            # sans aucune alternance, on rejette (ex: menu de navigation fragmenté).
            if len(roles) == 1:
                # Cependant, certains exports courts peuvent n'avoir que le bot (prompt en titre)
                # Mais en général, s'il y a len >= 2 et tout est identique, c'est très suspect pour une conversation.
                # On valide le critère strict comme requis par l'audit.
                return False
                
        # 3. Test de couverture textuelle
        blocks_words = sum(self._get_word_count(b.get_text(strip=True)) for b in blocks)
        coverage = blocks_words / total_words
        
        if coverage < self.min_coverage:
            return False
            
        return True
