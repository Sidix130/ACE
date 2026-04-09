# [Atome 1b] Sanctuaire Expert (Mermaid & LaTeX)

## 1. Objectif
Gérer les cas complexes identifiés comme défaillants dans `clean.py` : Mermaid avec préfixes (`}}%%`) et LaTeX varié.

## 2. Spécification Algorithmique

### Mermaid (Grok/DeepSeek)
- **Cible** : Divs/Spans/P contenant `graph`, `flowchart`, `sequenceDiagram`, etc.
- **Regex de détection** : `(?:^|\n)(?:}}%%|%%{.*?\}%%)?\s*(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt|pie|gitGraph|journey|C4Context|mindmap|timeline)\b`
- **Action** : Extraire, nettoyer les préfixes, UUID `__ACE_MERM_<hash>__`.

### LaTeX (DeepSeek/Standard)
- **Cible 1** : Balises `<annotation encoding="application/x-tex">`.
- **Cible 2** : Attributs `data-latex` ou délimiteurs `\(` `\)`.
- **Action** : Normaliser en `$` ou `$$`, UUID `__ACE_MATH_<hash>__`.

## 3. Livrable
Mise à jour de `ace/core/sanctuary.py`.

## 4. Test (Critique)
`tests/test_atom_01b.py` :
- Utiliser un fragment de `syshoplexe - Grok.html` (avec `}}%% graph TD`).
- Utiliser un fragment de `DeepSeek.html` (avec KaTeX).
- Assertions sur le contenu réinjecté.
