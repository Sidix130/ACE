# ACE - Adaptive Chat Extractor (v1.1.0)

ACE est un outil en ligne de commande (CLI) professionnel conçu pour extraire et convertir des conversations HTML (issues d'exports ChatGPT, Claude, Gemini, etc.) en formats structurés (**Markdown**, **JSON**, **YAML**) avec une fidélité maximale.

## 🚀 Installation

ACE s'installe facilement avec `uv` ou `pip` :

```zsh
# Installation en mode éditable avec uv
uv pip install -e .

# Ou via pip
pip install .
```

## 🧪 Tests

ACE dispose d'une suite de tests complète (Unitaires et Intégration) :

```zsh
# Installer les dépendances de test
uv pip install -e ".[dev]"

# Exécuter tous les tests
uv run pytest tests/
```

## 🛠 Usage

La commande de base est `ace` :

```zsh
ace [ENTRÉE] [SORTIE] [OPTIONS]
```


### Arguments de base

- `input` : Fichier HTML source ou `-` pour lire depuis `stdin`.
- `output_arg` : Fichier de sortie. Déduit automatiquement si omis.

### Options Principales

- `-f, --format {md,json,yaml}` : Force le format de sortie.
- `-j, --json` : Raccourci pour `--format json`.
- `-d, --debug` : Active le mode diagnostic (crée un dossier `debug/` avec les artefacts).
- `-q, --quiet` : Désactive les sorties console (sauf erreurs).
- `--no-table` : Désactive le traitement avancé des tableaux (utile pour le contenu brut).

### Stratégies de Détection

Utilisez `--help-strategies` pour voir les détails :

- `topo` (défaut) : Analyse topologique universelle.
- `heuristic` : Basé sur des motifs CSS/classes.
- `flux` : Pour les pages sans conteneurs explicites (ex: Grok).

## ✨ Fonctionnalités Avancées

- **Sanctuaire de Contenu** : Protection automatique des blocs complexes (Mermaid, LaTeX/Math, Code) pour éviter toute altération durant la conversion.
- **Restauration Intégrale** : Réinjection des contenus protégés dans tous les formats d'export.
- **Induction Intelligente** : ACE devine le nom du fichier de sortie et le format basé sur l'extension (ex: `ace chat.html` -> `chat.json` si `-j` est présent).
- **Format Markdown Premium** : Support des liens, images, citations, et tableaux (Gfm).

## 📊 Exemples

```zsh
# Conversion simple (crée chat_export.md)
ace chat_export.html

# Export JSON vers un pipe
cat export.html | ace -j - - | jq .session.turns[0]

# Diagnostic complet pour une structure récalcitrante
ace -d debug_me.html
```

## 📜 Audit et Conformité

ACE respecte les protocoles de l'audit **Lithos** pour la réversibilité et le diagnostic rigoureux des données.
