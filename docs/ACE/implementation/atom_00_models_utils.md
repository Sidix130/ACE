# [Atome 0] Fondations & Modèles

## 1. Objectif
Définir le contrat de données universel qui servira de pivot entre l'extraction (DOM) et le rendu (Markdown). Cela évite que les données ne se "diluent" dans des dictionnaires non typés.

## 2. Fichiers à créer

### `ace/models/chat.py`
Utiliser des `dataclasses` pour :
- `Role` (Enum: USER, MODEL, SYSTEM)
- `ContentType` (Enum: TEXT, CODE, MERMAID, MATH, TABLE)
- `MessagePart` : Bloc de contenu élémentaire.
- `Turn` : Un message complet (index, rôle, liste de MessagePart, confiance).
- `ChatSession` : Titre, source, liste de Turn.

### `ace/utils/dom.py`
- Helpers pour BeautifulSoup (ex: `get_clean_text`, `is_empty_node`).
- Abstraction de la profondeur relative (pour la topologie).

### `ace/utils/regex.py`
- Centraliser les patterns (UI noise, labels, Mermaid detection).

## 3. Critères de succès (Petit Modèle)
- [ ] Le fichier `chat.py` est importable sans erreur.
- [ ] Je peux créer un objet `Turn` manuellement et le sérialiser (ou le convertir en dict).
- [ ] Les Regex sont compilées avec les flags appropriés (`MULTILINE`, `IGNORECASE`).

## 4. Alignement V-Idéale
- Utilise les noms de classes définit dans `docs/V_idéale.md` section 2.6.
- Prévoir un champ `metadata: Dict` sur chaque objet pour l'extensibilité future.
