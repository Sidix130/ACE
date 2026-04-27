# Contre-Audit d'Implémentation (ACE v1.2.0)

Suite à la proposition architecturale de l'Auditeur Expert (DeepSeek V4), voici mon analyse en tant que Développeur Exécutif/Constructeur, afin d'adapter ce noble paradigme algorithmique en **code Python réaliste, performant et anti-fragile**.

## 1. TopologicalDetector : Du "Clustering Strict" au "Voisinage par Fenêtre"

L'auditeur recommande un **graphe de similarité** et un relâchement contrôlé basé sur une **distance vectorielle**.
C'est conceptuellement parfait pour résoudre la **Fragmentation (Blocage A)**.

👉 **Le Défi d'Implémentation (Mon Audit) :** 
Calculer une distance matricielle `O(N^2)` sur tous les noeuds BeautifulSoup d'une page exportée (pouvant dépasser 30 000 balises) va provoquer des temps d'extraction inacceptables (plusieurs dizaines de secondes).

✅ **Ma Solution Technique (Le "Sliding Window Merging") :**
Plutôt qu'un graphe global, nous appliquerons une agrégation temporelle itérative (`O(N)`).
1. Isoler les nœuds primaires intéressants par densité (comme aujourd'hui).
2. Parcourir ces candidats séquentiellement en se basant sur leur ordre dom (`sourceline` ou parcours DFS).
3. Maintenir un `active_cluster`. Si le prochain candidat a une *distance sémantique* (différence de profondeur <= 2, et tags cousins/frères) suffisamment faible, l'assimiler dans le cluster. Sinon, clôturer le cluster et en commencer un nouveau.
**Bonus "Anti-Wrapper" (Blocage B)** : Appliquer la formule de l'auditeur (`Pénalité_Wrapper`) lors du scoring final des clusters scellés. Si un cluster possède une profondeur (depth) de 1 ou 2 et contient plus de 60% du texte du DOM, on divise purement et simplement son score par 10.

## 2. HeuristicDetector : Les Sondes (Probes) via Chain of Responsibility

L'auditeur propose un pattern génial : des `Probes` indépendantes (ARIA, Classes, Data Attributes, Séparateurs) qui émettent des "votes".

👉 **Le Défi d'Implémentation (Mon Audit) :**
La fusion des sondes peut devenir chaotique si l'une trouve des conteneurs massifs et une autre des sous-conteneurs. Le calcul du chevauchement (`> 80%`) est lourd.

✅ **Ma Solution Technique (Waterfall Probes) :**
Plutôt qu'une "fusion" anarchique, chaque `Probe` héritera d'une interface commune, mais elles seront exécutées dans un ordre strict de spécificité (Waterfall) :
1. `DataAttributeProbe` (Cherche `data-message-id`, `data-testid`). Spécificité absolue. Si elle trouve et scorabilise au dessus de 0.8 -> Arret et Retour.
2. `SemanticClassProbe` (Regex sur `user-message`, etc.). Si confiance > 0.8 -> Arret.
3. `StructuralSeparatorProbe` (Flux séparés par des `<hr>`). Dernier recours heuristique.

Cette approche est *deterministic* et évite les heuristiques floues de moyenne pondérée.

## 3. L'Orchestrateur (AutoStrategy)

L'auditeur propose une **Méta-Évaluation** comparative entre le Topologique et l’Heuristique.

✅ **Ma Solution Technique (Le Contrôleur d'Integrité) :**
Nous allons implémenter le composant `ExtractionValidator` dans `main.py`.
Le processus sera séquentiel par gain de temps (pas la peine de lancer la Topologie si l'Heuristique retourne 15 messages structurés tirés d'un ChatGPT avec `data-testid` évidents).

**Pipeline V1.2.0 (`process_html` sous capot "auto") :**
1. **Passe Heuristique**
   - Si les sondes retournent `len(blocks) >= 2` ET que le Validateur estime que ça couvre `> 30%` des tokens bruts de la page -> **SUCCÈS**.
2. **Passe Topologique**
   - Si l'Heuristique échoue, lancer le TopologicalDetector "Nouvelle Génération" (par Voisinage temporel).
   - Passer les clusters au Validateur. **Pour résoudre le Blocage C (faux positif unique)** : Le validateur rejettera tout résultat ayant `len == 1` sauf s'il contient au minimum un rôle "user" inféré, prouvant que ce n'est pas qu'un lien de navigation.
3. **Passe Brut (Fallback)**
   - Le classique `body` textuel si les deux premiers échouent.

---

**Conclusion** : L'audit de DeepSeek est de l'orfèvrerie algorithmique. Je l'ai purgé de sa complexité académique (calculs de chevauchement o(n^2), moyennes probabilistes floues) pour la rendre mathématiquement traitable et robuste sur l'AST de BeautifulSoup. Nous avons notre architecture V1.2.
