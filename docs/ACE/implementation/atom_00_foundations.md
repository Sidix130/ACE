# [Atome 0] Fondations & Environnement

## 1. Objectif
Poser le cadre technique (dépendances) et le cadre sémantique (modèles) pour s'assurer que tout le code futur parle la même langue.

## 2. Livrables Techniques

### `pyproject.toml`
```toml
[project]
name = "ace"
version = "0.1.0"
dependencies = [
    "beautifulsoup4",
]

[project.optional-dependencies]
dev = [
    "pytest",
]
```

### `ace/models/chat.py`
Définir les Enums `Role` et `ContentType`, et les Dataclasses `MessagePart`, `Turn`, `ChatSession`.
- **Règle** : Chaque classe doit supporter un dictionnaire `metadata`.

### `ace/utils/dom.py`
Fonctions utilitaires pour BeautifulSoup :
- `get_clean_text()`
- `is_ui_element()` (basé sur une liste de mots-clés)

## 3. Procédure d'Exécution
1. Création des répertoires `ace/models`, `ace/utils`, `ace/core`, `ace/engine`.
2. Écriture des fichiers.
3. Création de `tests/test_atom_00.py`.
4. Exécution de `pytest tests/test_atom_00.py`.

## 4. Points de Vigilance (Audit)
- Ne pas oublier d'installer les dépendances au début de la tâche réelle.
- S'assurer que les modèles de données sont riches (V_idéale section 2.6).
