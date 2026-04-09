# Auto-Audit : Biais et Limites de l'Agent (Antigravity/Gemini)

## 1. Biais Identifiés

| Biais | Manifestation | Stratégie de Mitigation |
|-------|---------------|-------------------------|
| **Biais de Complétude** | Tendance à vouloir coder tout le système (`OCE` complet) en une seule fois, au risque de dilution. | Fragmentation stricte en **Atomes** (modules <100 lignes). |
| **Biais d'Optimisme Algorithmique** | Croire qu'une regex "améliorée" couvrira 100% des cas d'un site (ex: Grok). | Utilisation systématique de la **Sanctuarisation** (extraction préemptive) plutôt que de la réparation post-conversion. |
| **Biais de Contexte** | Oubli des contraintes d'architecture `OCE` lors de l'implémentation de la version "Light". | Référencer systématiquement `docs/V_idéale.md` avant chaque modification de structure. |

## 2. Limites Cognitives & Cognition Distribuée

- **Saturation par la Taille** : Les fichiers HTML de chat font souvent +1MB. L'analyse directe par `BeautifulSoup` dans une seule fonction sature ma fenêtre d'attention.
  - *Solution* : Opérer uniquement sur les **fragments** identifiés.
- **Dilution par Dispersion** : Si je gère en même temps le nettoyage UI, la détection des tours et la conversion LaTeX, je perds en précision sur chacun.
  - *Solution* : Un tour d'outil = Une responsabilité atomique.
- **Amnésie Structurelle** : Sans typage fort, je risque de manipuler des dictionnaires "souples" qui cassent lors de l'évolution vers `OCE`.
  - *Solution* : Imposer des `dataclasses` (Atome 0) dès le départ.

## 3. Posture Critique

Le script `clean.py` actuel est un "miracle technique" qui tient par des heuristiques fragiles. Ma tendance naturelle sera de les "maquiller" par un meilleur code. **Je m'interdis cela.**
Chaque heuristique doit être encapsulée dans une **Stratégie** (pattern Strategy) pour pouvoir être remplacée par le clustering structurel d'OCE sans douleur.
