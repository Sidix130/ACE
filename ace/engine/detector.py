from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional
import re
from collections import defaultdict

class TopologicalDetector:
    """
    Détecteur topologique V1.2.0.
    Utilise 'Sliding Window Merging' en O(N) pour agglomérer les flux contigus, 
    résolvant la fragmentation tout en évitant le (O(N^2)).
    """
    def __init__(self, min_density: int = 3):
        self.min_density = min_density
        self.uuid_pattern = re.compile(r'__ACE_[A-Z]+_[a-f0-9]{8}__')

    def _text_density(self, tag: Tag) -> int:
        return len(tag.get_text(strip=True).split())

    def _compute_fast_signature(self, tag: Tag) -> str:
        """Génère une empreinte rapide basée sur le tag et ses styles globaux."""
        classes = tag.get('class', [])
        if isinstance(classes, str): classes = [classes]
        
        # On ne garde que les classes stables (pas d'ID auto générés)
        stable = [c for c in classes if not re.search(r'\d{4,}|[a-f0-9]{6,}', c)]
        
        # On hash la structure basique (le tag et ses classes)
        # On préfixe par la profondeur pour décourager les fusions verticales illogiques.
        depth = len(list(tag.parents))
        return f"d{depth}|{tag.name}|{'+'.join(sorted(stable[:3]))}" 

    def _are_compatible_for_merge(self, cand1: Tag, cand2: Tag) -> bool:
        """
        Vérifie si deux candidats peuvent fusionner.
        Critères V1.2 : Parent commun OU oncle/neveu, avec vérification de similarité
        allégée pour empêcher la fusion de conteneurs structurellement orthogonaux.
        """
        if cand1 in cand2.parents or cand2 in cand1.parents:
            return False
            
        distance_ok = False
        if cand1.parent == cand2.parent:
            distance_ok = True
        elif cand1.parent and cand2.parent:
            parent1 = getattr(cand1, 'parent', None)
            parent2 = getattr(cand2, 'parent', None)
            if parent2 == getattr(parent1, 'parent', None) or parent1 == getattr(parent2, 'parent', None):
                distance_ok = True
            elif getattr(parent1, 'parent', None) == getattr(parent2, 'parent', None) and getattr(parent1, 'parent', None) is not None:
                distance_ok = True
                
        if not distance_ok:
            return False
            
        # Similarité de signature (Seuil allégé)
        classes1 = set(c for c in cand1.get('class', []) if not re.search(r'\d{4,}', c))
        classes2 = set(c for c in cand2.get('class', []) if not re.search(r'\d{4,}', c))
        
        if classes1 and classes2:
            # S'ils ont tous les deux des classes, ils doivent en partager au moins une
            if not classes1.intersection(classes2):
                return False
                
        # Rejet des fusions de tags orthogonaux 
        text_tags = {'p', 'li', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'span', 'strong', 'em', 'code', 'pre'}
        if cand1.name != cand2.name:
            if cand1.name not in text_tags or cand2.name not in text_tags:
                return False
                
        return True

    def _score_cluster(self, cluster: List[Tag], total_document_words: int) -> float:
        """
        Calcule un score basé sur : Cohésion * Granularité * Richesse - Pénalité Wrapper.
        """
        n = len(cluster)
        if n == 0: return 0.0
        
        # Richesse
        richness = 1.0
        for t in cluster:
            if t.find(['pre', 'code', 'table', 'blockquote', 'li', 'h1', 'h2']):
                richness += 0.5
        richness = min(richness, 3.0) 

        # Granularité (inverse de la profondeur moyenne)
        avg_depth = sum(len(list(t.parents)) for t in cluster) / n
        granularity = avg_depth / 10.0 # Plus c'est profond, plus le facteur grandi (favorise les feuilles)

        # Cohésion (texte brut)
        avg_density = sum(self._text_density(t) for t in cluster) / n
        
        base_score = n * avg_density * granularity * richness
        
        # Bonus UUID pour protéger le code restoré de Sanctuary
        if any(self.uuid_pattern.search(t.get_text()) for t in cluster):
            base_score *= 1.5
            
        # Pénalité Anti-Wrapper : si un seul cluster monopolise le document
        if len(cluster) == 1 and total_document_words > 50:
            cluster_words = sum(self._text_density(t) for t in cluster)
            if cluster_words / total_document_words > 0.8:
                base_score /= 10.0
                
        return base_score

    def _merge_sequential_candidates(self, candidates: List[Tag]) -> List[List[Tag]]:
        """
        Glisse sur la liste séquentielle et fusionne les éléments contigus (ou quasi-contigus) 
        compatibles en gardant les 3 derniers clusters ouverts pour tolérer l'imbrication DOM.
        Complexité : O(N).
        """
        if not candidates:
            return []
            
        # sourceline permet d'assurer un tri parfait dans l'ordre d'apparition
        candidates = sorted(candidates, key=lambda t: t.sourceline or 0)
        
        clusters = []
        
        for current in candidates:
            merged = False
            # Recherche d'un cluster compatible parmi les 3 plus récents
            for cluster in reversed(clusters[-3:]):
                if self._are_compatible_for_merge(cluster[-1], current):
                    cluster.append(current)
                    merged = True
                    break
            
            if not merged:
                clusters.append([current])
                
        return clusters

    def detect(self, soup: BeautifulSoup) -> List[Tag]:
        """Détecte les blocs via Sliding Window Temporel et Scoring intelligent."""
        body = soup.find('body')
        total_words = self._text_density(body) if body else self._text_density(soup)
        
        # 0. Nettoyage du bruit UI
        for noise in soup.find_all(attrs={"role": ["dialog", "banner", "navigation"]}):
            noise.decompose()
        for noise in soup.find_all(class_=re.compile(r'cookie|modal|overlay|popup', re.I)):
            if noise.name != 'body':
                noise.decompose()
                
        # 1. Sélection candiats purs
        candidates = []
        for tag in soup.find_all(True):
            if tag.name in ['html', 'body', 'script', 'style', 'head', 'header', 'footer', 'nav']: 
                continue
            if self._text_density(tag) >= self.min_density or self.uuid_pattern.search(tag.get_text()):
                candidates.append(tag)
                
        if not candidates: 
            return []
            
        # 2. V1.2.0 Sliding Window Merging
        clusters = self._merge_sequential_candidates(candidates)
        
        # 3. Élimination des clusters parents (Dédoublonnage vertical)
        final_clusters = []
        for c1 in clusters:
            is_redundant = False
            for c2 in clusters:
                if c1 is c2: continue
                # Si tous les noeuds de c1 ont pour ancêtres un noeud de c2
                if all(any(node is ancestor or node in getattr(ancestor, 'descendants', []) for ancestor in c2) for node in c1):
                    # Comparaison via Scoring V1.2
                    if self._score_cluster(c2, total_words) > self._score_cluster(c1, total_words):
                        is_redundant = True
                        break
            if not is_redundant:
                final_clusters.append(c1)

        if not final_clusters:
            return []
            
        # 4. Champion absolu
        best_cluster = max(final_clusters, key=lambda c: self._score_cluster(c, total_words))
        
        return best_cluster
