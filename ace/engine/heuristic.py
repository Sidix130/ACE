from bs4 import BeautifulSoup, Tag
from typing import List, Tuple
import re
from abc import ABC, abstractmethod

class BaseProbe(ABC):
    """Sonde de base pour le HeuristicDetector."""
    
    @abstractmethod
    def probe(self, soup: BeautifulSoup) -> Tuple[List[Tag], float]:
        """
        Analyse l'arbre DOM et retourne une agrégation candidate.
        Retour :
            - Liste des balises (tours de conversation)
            - Score de confiance absolu (0.0 à 1.0)
        """
        pass

class DataAttributeProbe(BaseProbe):
    """Recherche des attributs de données conversationnels stricts (ex: data-message-id). Confiance absolue."""
    def probe(self, soup: BeautifulSoup) -> Tuple[List[Tag], float]:
        # 1. Essai sur les data-testid type "conversation-turn-*"
        candidates = soup.find_all(attrs={"data-testid": re.compile(r"conversation|message|turn", re.I)})
        
        # 2. Essai sur data-message-author-role
        if not candidates:
            candidates = soup.find_all(attrs={"data-message-author-role": True})
            
        # 3. Essai sur attributs génériques data-message*
        if not candidates:
            candidates = []
            for tag in soup.find_all(True):
                if any(attr.startswith('data-message') for attr in tag.attrs):
                    candidates.append(tag)

        if len(candidates) >= 2:
            # Filtre terminal : exclure le bruit UI
            candidates = [c for c in candidates if c.name not in ['button', 'svg', 'path', 'script', 'form', 'nav']]
            return candidates, 0.95
        return [], 0.0

class SemanticClassProbe(BaseProbe):
    """Recherche des classes sémantiques récurrentes liées aux LLMs."""
    def probe(self, soup: BeautifulSoup) -> Tuple[List[Tag], float]:
        user_pattern = re.compile(r'\b(user|human|you)(-|_)?message\b', re.I)
        bot_pattern = re.compile(r'\b(assistant|model|ai|bot|agent)(-|_)?(message|turn)\b', re.I)
        
        candidates = []
        for tag in soup.find_all(True):
            classes = tag.get('class', [])
            if isinstance(classes, str): 
                classes = [classes]
            class_str = " ".join(classes)
            if user_pattern.search(class_str) or bot_pattern.search(class_str):
                candidates.append(tag)
                
        # Fallback pour des classes simples type "message"
        if not candidates:
            msg_candidates = soup.find_all(class_=re.compile(r'^message$', re.I))
            if len(msg_candidates) >= 2:
                # Filtrer souvent il y a un container "message-list"
                msg_candidates = [m for m in msg_candidates if 'list' not in " ".join(m.get('class', [])).lower()]
                candidates = msg_candidates
                
        if len(candidates) >= 2:
            return candidates, 0.8
        return [], 0.0

class StructuralSeparatorProbe(BaseProbe):
    """Recherche des conteneurs séparés par <hr>."""
    def probe(self, soup: BeautifulSoup) -> Tuple[List[Tag], float]:
        hrs = soup.find_all('hr')
        if len(hrs) >= 1:
            parents_with_hrs = set(hr.parent for hr in hrs if hr.parent)
            best_parent = None
            max_hrs = 0
            for p in parents_with_hrs:
                count = len(p.find_all('hr', recursive=False))
                if count > max_hrs:
                    max_hrs = count
                    best_parent = p
                    
            if best_parent:
                blocks = [c for c in best_parent.find_all(recursive=False) 
                          if isinstance(c, Tag) and c.name not in ['hr', 'script', 'style']]
                if len(blocks) >= 2:
                    return blocks, 0.7
        return [], 0.0

class FallbackStructuralRepetitionProbe(BaseProbe):
    """Dernier recours: Cherche le motif structurel le plus répété au sein du document."""
    def probe(self, soup: BeautifulSoup) -> Tuple[List[Tag], float]:
        # Logique simplifiée en O(N) :
        # On regroupe les balises par leur paire (Nom + Parent_Nom)
        from collections import defaultdict
        patterns = defaultdict(list)
        
        for tag in soup.find_all(['div', 'article', 'section']):
            if tag.parent:
                sig = f"{tag.parent.name}>{tag.name}"
                patterns[sig].append(tag)
                
        if not patterns:
            return [], 0.0
            
        best_sig = max(patterns.keys(), key=lambda k: len(patterns[k]))
        candidates = patterns[best_sig]
        
        # Filtre anti-densité pour ne pas prendre des petits paragraphes nav
        valid = [c for c in candidates if len(c.get_text(strip=True).split()) > 5]
        
        if len(valid) >= 4:
            return valid, 0.4
        return [], 0.0

class HeuristicDetector:
    """
    Système de détection basé sur un pattern Chain of Responsibility "Waterfall".
    Les sondes sont organisées de la plus spécifique à la plus générique.
    """
    def __init__(self):
        self.probes = [
            DataAttributeProbe(),
            SemanticClassProbe(),
            StructuralSeparatorProbe(),
            FallbackStructuralRepetitionProbe()
        ]

    def detect(self, soup: BeautifulSoup) -> List[Tag]:
        """
        Exécute la chaîne d'évaluation et retourne les blocs de la première sonde validee.
        La gestion du faux positif sera gérée a un niveau transverse par l'ExtractionValidator.
        """
        for probe in self.probes:
            blocks, confidence = probe.probe(soup)
            # Threshold de 0.4 minimal pour valider un effort heuristique
            if confidence >= 0.4 and len(blocks) >= 1:
                return blocks
                
        return []
