# [Atome 1] Le Sanctuaire (Protection des données)

## 1. Objectif
Le "Sanctuaire" est le composant le plus critique pour la robustesse. Il extrait les contenus complexes (qui ont leur propre syntaxe fragile comme Python, LaTeX ou Mermaid) AVANT que la conversion Markdown ne commence.

## 2. Logique Séquentielle (Algorithme)
1. Parcourir le DOM.
2. Pour chaque bloc suspect (pre, div.mermaid, annotation katex) :
   - Extraire le contenu brut.
   - Générer un UUID unique.
   - Remplacer le nœud dans le DOM par une chaîne de placeholder `__ACE_UUID__`.
   - Stocker l'UUID dans un mapping.

## 3. Fichiers à créer

### `ace/core/sanctuary.py`
- Classe `SanctuaryEntry` (UUID, Type, RawContent).
- Classe `SanctuaryManager` :
  - `extract_all(soup) -> Dict[str, SanctuaryEntry]`
  - `restore_all(text, mapping) -> str`

## 4. Cas critiques à gérer (Petit Modèle)
- **Mermaid Grok** : Chercher spécifiquement les textes commençant par `}}%%` ou `graph`.
- **LaTeX DeepSeek** : Extraire depuis `<annotation>` OU depuis les spans `data-latex`.
- **Code Multi-tours** : S'assurer que les UUID sont globaux à la session pour éviter les collisions.

## 5. Critères de succès
- [ ] Passage du test : Un HTML contenant Mermaid et LaTeX est transformé en un texte contenant uniquement des UUID.
- [ ] La restauration remet les bons blocs avec les clôtures ` ```mermaid ` ou `$$`.
