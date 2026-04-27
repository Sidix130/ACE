# Journal de Bord : Blocages d'Extraction (Forensic Log) réalisez par l'agent vs code - CHMS

Ce journal documente les points de rupture identifiés lors de l'extraction du fichier `CHMS_Causal-Hybrid-Mapping-System.html`. Chaque point est sourcé par des données de log et pondéré par un indice de confiance (IC).

---

## 🛑 Blocage A : Fragmentation par Incompatibilité de Signature
Le détecteur isole les éléments au lieu de les voir comme un flux continu.

- **Preuve Objective** : 
    - Le nœud `li[kery7j]` possède la signature `li[](p:1)`.
    - Le nœud `h1[fhiouf]` possède la signature `h1[](None)`.
    - Ces deux nœuds appartiennent au même flux sémantique mais sont placés dans des clusters différents par `TopologicalDetector:L145`.
- **Analyse du Score** : Cluster 186 (contenant `li[v2xdrv]`) a un score de **18.00**, tandis que le bruit structurel (Cluster 160) a un score de **11508.75**.
- **Indice de Confiance (IC)** : **1.0 (Certain)**
    - *Justification* : Observé directement dans le dump de signatures du script `diagnose_chms.py`. La condition de stricte compatibilité des signatures empêche le regroupement des éléments hétérogènes (titres, listes, paragraphes).

---

## 🛑 Blocage B : Domination du Wrapper Global (Sur-Scoring)
Le détecteur préfère le conteneur global au contenu granulaire.

- **Preuve Objective** : 
    - Cluster 160 : `main[flex-1+min-h-0](div:1)` -> Score: **11508.75**.
    - Cluster 161 : `div[flex+flex-col+group/thread+min-h-full](div:1)` -> Score: **11508.75**.
- **Analyse du Score** : La densité textuelle de ces nœuds ( > 15 000 mots) écrase les micro-signaux des messages individuels. L'algorithme sélectionne ces wrappers comme étant "le meilleur cluster" car ils contiennent mathématiquement tout le texte.
- **Indice de Confiance (IC)** : **0.95 (Très élevé)**
    - *Justification* : Le `max(final_clusters, key=self._score_cluster)` sélectionne fatalement le nœud le plus haut dans l'arbre qui respecte la répétition minimale. Le "Winner-takes-all" est ici toxique pour la granularité.

---

## 🛑 Blocage C : Échec de la Détection de Flux (Missing Fallback)
Le format "flat" (ChatGPT modern) n'active pas le fallback Lithos.

- **Preuve Objective** : L'algorithme détecte **1 tour** (le lien de navigation). Puisque `len(blocks) > 0`, la condition `if not blocks` (`main.py:51`) ne se déclenche jamais.
- **Analyse du Score** : Un seul "faux positif" suffit à désactiver la protection par fallback sur le body.
- **Indice de Confiance (IC)** : **0.90 (Élevé)**
    - *Justification* : Observé dans `report.md`. Le système se croit victorieux en trouvant un lien, ignorant les 2500 autres candidats potentiels.

---

## 🧪 Tests de Vérification Objective
Pour chaque point ci-dessus, le test suivant est réalisable :
1. **Test A** : Modifier `_are_signatures_compatible` pour autoriser `p` et `li` contigus -> Vérifier si le score du cluster augmente.
2. **Test B** : Appliquer un plafond (cap) de score sur la densité textuelle brute dans `_score_cluster`.
3. **Test C** : Introduire un `Coverage Ratio` (Texte Cluster / Texte Total) ; si < 10%, forcer la détection multi-cluster ou `flux`.
