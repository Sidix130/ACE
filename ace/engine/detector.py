from bs4 import BeautifulSoup, Tag
from typing import List, Optional
import re

class HeuristicDetector:
    def __init__(self):
        self.role_keywords = ['user', 'assistant', 'model', 'human', 'message', 'chat', 'bubble', 'content']
        self.uuid_pattern = re.compile(r'__ACE_[A-Z]+_[a-f0-9]{8}__')

    def _get_candidates(self, soup: BeautifulSoup) -> List[Tag]:
        """Identifie les conteneurs potentiels ayant une densité textuelle minimale ou un UUID."""
        candidates = []
        for tag in soup.find_all(['div', 'article', 'section', 'ms-chat-message']):
            text = tag.get_text(strip=True)
            # Accepter si au moins 2 mots OU si contient un UUID ACE
            if len(text.split()) >= 2 or self.uuid_pattern.search(text):
                candidates.append(tag)
        return candidates

    def _score_tag(self, tag: Tag) -> float:
        """Calcule un score de probabilité qu'un tag soit un message."""
        score = 0.0
        classes = tag.get('class', [])
        if isinstance(classes, str): classes = [classes]
        
        # Signal de rôle ou de contenu dans les classes (Signal Fort)
        class_str = " ".join(classes).lower()
        if any(kw in class_str for kw in self.role_keywords):
            score += 5.0
            
        # Signal par nom de tag (spécifique à certains exports comme AI Studio)
        if tag.name in ['ms-chat-message', 'article']:
            score += 4.0
                
        # Signal structurel (enfants typiques de messages ou UUID)
        text = tag.get_text(strip=True)
        if tag.find(['p', 'code', 'pre', 'table']) or self.uuid_pattern.search(text):
            score += 2.0
            
        return score

    def detect(self, soup: BeautifulSoup) -> List[Tag]:
        """Détecte les blocs de message dans le DOM."""
        candidates = self._get_candidates(soup)
        scored_candidates = []
        
        for cand in candidates:
            score = self._score_tag(cand)
            if score >= 5.0:
                scored_candidates.append((cand, score))
        
        # Stratégie Bottom-Up : On garde les nœuds qui n'ont pas de DESCENDANTS eux-mêmes candidats.
        final_blocks = []
        all_candidate_tags = [c[0] for c in scored_candidates]
        
        for tag, score in scored_candidates:
            has_candidate_descendant = False
            for descendant in tag.descendants:
                if descendant in all_candidate_tags:
                    has_candidate_descendant = True
                    break
            
            if not has_candidate_descendant:
                final_blocks.append(tag)
                
        return final_blocks
