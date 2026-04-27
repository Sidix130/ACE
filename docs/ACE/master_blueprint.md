# ACE (Adaptive Chat Extractor) – Référence Complète du Projet

**Version** : 1.0 (ACE Light)
**Date** : 2026-04-12
**Auteur** : Projet collaboratif initié par Sidix

---

## 1. Introduction et Vision

### 1.1 Problème Résolu

Les interfaces de chat des grands modèles de langage (ChatGPT, Claude, DeepSeek, Grok, AI Studio, etc.) produisent des exports HTML contenant des conversations riches (texte, code, diagrammes Mermaid, formules LaTeX). Les outils d'extraction existants reposent sur des règles spécifiques à chaque plateforme (sélecteurs CSS codés en dur) et deviennent obsolètes à chaque changement d'interface.

**ACE (Adaptive Chat Extractor)** résout ce problème de manière **agnostique et pérenne** en analysant la **topologie du DOM** plutôt que des marqueurs sémantiques fragiles.

### 1.2 Vision

> Extraire **universellement** toute conversation de chat LLM depuis un export HTML, en préservant **fidèlement** sa richesse structurelle (Markdown, code, diagrammes, mathématiques), sans aucune règle spécifique à une plateforme.

ACE est conçu pour être le **squelette évolutif** d'une version idéale (**OCE**), capable d'intégrer de nouveaux algorithmes de détection sans réécriture majeure.

### 1.3 Ce qui rend ACE unique

| Approche traditionnelle | Approche ACE |
|------------------------|--------------|
| Sélecteurs CSS spécifiques à un site | Analyse **topologique** du DOM |
| Maintenance constante à chaque mise à jour d'interface | Résilience naturelle aux changements de structure |
| Fonctionne pour une liste fermée de sites | Universel pour tout export de chat LLM |
| Sortie texte brut ou Markdown basique | Préservation des blocs complexes (Mermaid, LaTeX, tableaux) |

---

## 2. Principes Fondateurs

### 2.1 Agnostique par Conception

ACE ne fait **aucune hypothèse** sur les noms de classes, les IDs, ou les mots-clés. Tout est inféré dynamiquement à partir de la **structure répétitive** inhérente aux conversations (une liste de messages partageant une signature structurelle commune).

### 2.2 Résilience par Couches

Le pipeline d'extraction est modulaire et chaque composant peut être amélioré ou remplacé indépendamment :

- **Sanctuaire** : Protège les contenus complexes (code, Mermaid, LaTeX) avant toute transformation.
- **Détecteur topologique** : Identifie les conteneurs de messages par clustering structurel.
- **Inférence de rôle** : Détermine qui parle (User/Model) via une combinaison de signaux légers et d'alternance.
- **Convertisseur Markdown** : Transforme le HTML nettoyé en Markdown enrichi.

### 2.3 Évolutivité vers OCE

ACE Light est intentionnellement architecturé pour accueillir la version idéale **OCE (OmniChat Extractor)** sans refonte. Les interfaces (classes abstraites, dataclasses) sont déjà en place. Les futurs algorithmes (clustering avancé, inférence bayésienne) pourront être injectés comme de nouvelles stratégies.

---

## 3. Architecture Globale

```
ace/
├── core/                   # Composants métier critiques
│   └── sanctuary.py        # Protection des contenus complexes
├── engine/                 # Moteurs d'extraction et de conversion
│   ├── detector.py         # Détection des tours (TopologicalDetector)
│   ├── inferencer.py       # Inférence des rôles (User/Model)
│   └── converter.py        # Conversion HTML → Markdown
├── models/                 # Modèles de données (dataclasses)
│   └── chat.py             # Role, ContentType, Turn, ChatSession
├── processors/             # Processeurs spécialisés
│   └── tables.py           # Conversion de tableaux HTML → GFM
├── utils/                  # Utilitaires transverses
│   ├── dom.py              # Helpers BeautifulSoup
│   └── regex.py            # Patterns centralisés (Mermaid, UI)
├── main.py                 # Orchestrateur et CLI
└── pyproject.toml          # Dépendances et métadonnées
```

**Flux de données** :

1. Chargement du HTML → `BeautifulSoup`
2. **Sanctuaire** : extraction des blocs complexes, remplacement par UUID
3. **Détecteur** : identification des conteneurs de messages → `List[Tag]`
4. **Pour chaque bloc** :
   - **Inférence** : rôle (User/Model)
   - **Conversion** : Markdown (avec préservation des UUID)
5. **Restauration** : réinjection des contenus protégés
6. **Sortie** : fichier Markdown structuré

---

## 4. Composants Détaillés

### 4.1 Modèles de Données (`models/chat.py`)

Définit les structures immuables pour représenter une conversation :

- **`Role`** : Enum (`USER`, `MODEL`, `SYSTEM`)
- **`ContentType`** : Enum (`TEXT`, `CODE`, `MERMAID`, `MATH_INLINE`, `MATH_BLOCK`, `TABLE`, `IMAGE`)
- **`MessagePart`** : Un fragment de contenu typé
- **`Turn`** : Un message complet (index, rôle, liste de `MessagePart`, confiance)
- **`ChatSession`** : Conversation complète avec métadonnées

**Pourquoi des dataclasses ?** Elles garantissent un typage fort et permettent une sérialisation aisée (JSON, YAML). Le champ `metadata: Dict` offre une extensibilité sans rupture.

### 4.2 Sanctuaire (`core/sanctuary.py`)

**Objectif** : Protéger les contenus à syntaxe fragile (code, Mermaid, LaTeX) de toute altération pendant la conversion Markdown.

**Principe** :

1. Parcourir le DOM pour identifier les nœuds complexes (`<pre>`, `<annotation>`, textes contenant des mots-clés Mermaid).
2. Extraire le contenu brut, générer un UUID unique (`__ACE_<TYPE>_<hash>__`).
3. Remplacer le nœud original par cet UUID (chaîne de caractères).
4. Après conversion Markdown, remplacer les UUID par leur contenu formaté (ex: ` ```mermaid\n...\n``` `).

**Cas spéciaux gérés** :

- **Mermaid Grok** : préfixes `}}%%` ou `%%{init}%%`
- **LaTeX DeepSeek** : balises `<annotation encoding="application/x-tex">`

### 4.3 Détecteur Topologique (`engine/detector.py`)

C'est le cœur de l'approche agnostique. Le `TopologicalDetector` identifie les messages **sans aucun a priori sémantique**.

#### 4.3.1 Algorithme

1. **Extraction des candidats** : Tous les éléments ayant une densité textuelle ≥ 3 mots (ou contenant un UUID du Sanctuaire).
2. **Signature structurelle** : Pour chaque candidat, on calcule une signature normalisée :
   - Nom du tag
   - Classes CSS épurées (suffixes hexadécimaux supprimés)
   - Structure des enfants directs (compteurs par type)
   - Attributs sémantiques (`role`, `data-testid`)
3. **Clustering par parent** : Au sein de chaque parent, on regroupe les enfants dont les signatures sont **compatibles** (similarité de Jaccard sur les classes, distance d'édition faible sur la structure).
4. **Scoring des clusters** : Chaque groupe candidat reçoit un score composite basé sur :
   - Taille du groupe (≥ 2)
   - Régularité d'espacement (gaps entre indices)
   - Densité textuelle moyenne
   - Richesse du contenu (présence de code, tableaux)
   - Pénalité pour motifs UI (bannières, modales)
5. **Sélection** : Le groupe avec le meilleur score est choisi comme la liste des messages.
6. **Gestion du mode flux** : Pour les conversations sans conteneurs (style Grok avec `<hr>`), un mode spécial regroupe les éléments entre séparateurs.

#### 4.3.2 Évolution vers OCE

Le `TopologicalDetector` est conçu pour être remplacé ou complété par des stratégies plus avancées (clustering hiérarchique, modèles entraînés) sans changer son interface publique (`detect(soup) -> List[Tag]`).

### 4.4 Inférence de Rôle (`engine/inferencer.py`)

**Principe** : Déterminer pour chaque bloc si l'émetteur est `USER` ou `MODEL`.

**Méthode** : Vote pondéré de signaux :

| Signal | Poids | Exemple |
|--------|-------|---------|
| Classe CSS contient `user`/`human`/`you` | +5 | `class="user-message"` |
| Classe CSS contient `assistant`/`model`/`ai`/`thought` | +5 | `class="assistant-message"` |
| Présence de code ou LaTeX | +2 (MODEL) | `<pre><code>` |
| Longueur du texte (>300 caractères) | +1 (MODEL) | – |

**Fallback** : En cas d'égalité, l'alternance avec le tour précédent est utilisée. Pour le premier message, le rôle par défaut est `USER`.

**Évolution OCE** : Remplacer ce vote heuristique par un classifieur Bayésien naïf entraîné sur un corpus annoté.

### 4.5 Convertisseur Markdown (`engine/converter.py`)

**Pattern Dispatcher** : Un dictionnaire associe chaque nom de balise HTML à une fonction de conversion.

```python
handlers = {
    'p': handle_paragraph,
    'h1'..'h6': handle_header,
    'ul', 'ol': handle_list,
    'li': handle_list_item,
    'table': handle_table,
    'pre': handle_code_block,
    # ...
}
```

**Règle critique** : Les UUID du Sanctuaire (`__ACE_...__`) doivent être **préservés intégralement** et jamais modifiés par les handlers.

### 4.6 Orchestrateur (`main.py`)

**CLI** :

```bash
ace input.html output.md
```

**Pipeline** :

```python
def process_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    sanctuary = SanctuaryManager()
    mapping = sanctuary.extract(soup)

    detector = TopologicalDetector()
    blocks = detector.detect(soup)

    inferrer = RoleInferrer()
    dispatcher = MarkdownDispatcher()
    turns = []
    for i, block in enumerate(blocks):
        role, conf = inferrer.infer(block, turns)
        md = dispatcher.convert(block)
        turns.append(Turn(index=i, role=role, content=[...], confidence=conf))

    full_md = build_markdown(turns)
    final_md = sanctuary.restore(full_md, mapping)
    return final_md
```

---

## 5. Philosophie de Test

ACE suit une approche **TDD (Test-Driven Development)** rigoureuse :

### 5.1 Types de Tests

| Type | Emplacement | Objectif |
|------|-------------|----------|
| **Unitaires** | `tests/test_detector_unit.py` | Valider les fonctions internes (signature, clustering, scoring) |
| **Intégration** | `tests/test_detector_integration.py` | Valider l'extraction sur des fixtures HTML réelles |
| **Golden** | `tests/test_golden.py` | Comparer la sortie Markdown complète avec une référence |

### 5.2 Golden Files

Les golden files (`tests/golden/*.md`) sont la **source unique de vérité** pour la sortie attendue. Toute modification du code ne peut être fusionnée que si les tests golden passent (aucune régression).

Pour générer les golden files initiaux :

```bash
python scripts/generate_golden.py
```

### 5.3 Workflow de Développement avec un Agent

1. **Écrire les tests d'abord** (unitaires ou golden).
2. Lancer l'agent avec pour instruction de faire passer les tests un par un.
3. Valider que les tests d'intégration et golden restent verts.
4. Itérer jusqu'à ce que tous les tests soient au vert.

---

## 6. Guide de Contribution

### 6.1 Ajouter le Support d'une Nouvelle Plateforme

ACE étant agnostique, **aucune modification n'est normalement nécessaire**. Si un export spécifique pose problème :

1. Ajouter un fichier de test dans `tests/fixtures/` avec un échantillon minimal reproduisant le problème.
2. Ajouter un test golden correspondant.
3. Améliorer le `TopologicalDetector` ou le `Sanctuary` pour traiter ce cas, en veillant à ne pas régresser sur les autres tests.

### 6.2 Améliorer le Détecteur

Les améliorations doivent être faites dans `engine/detector.py`, en préservant l'interface `detect(soup) -> List[Tag]`. Toute nouvelle stratégie peut être ajoutée comme une classe séparée (ex: `ClusteringDetector`) et sélectionnée via un paramètre.

### 6.3 Étendre les Capacités de Conversion

Pour ajouter un nouveau type de contenu (ex: diagrammes PlantUML) :

1. Ajouter un nouveau type dans `ContentType`.
2. Implémenter l'extraction dans `SanctuaryManager.extract()`.
3. Ajouter le handler de conversion approprié.

---

## 7. Critique et Auto-Audit

### 7.1 Forces

- **Universalité** : Fonctionne sur tous les exports de chats LLM testés sans configuration.
- **Robustesse** : Insensible aux changements de classes ou d'IDs.
- **Préservation** : Les contenus complexes (Mermaid, LaTeX) sont intacts.
- **Testabilité** : Couverture de tests élevée grâce aux golden files.

### 7.2 Faiblesses Actuelles

- **Messages courts** : Un message très court ("Ok.") peut être ignoré si la densité textuelle est inférieure au seuil (3 mots).
- **Conversations multi-fils** : Ne gère pas les fils de discussion imbriqués (hors périmètre des chats LLM).
- **Performances** : L'analyse de tout le DOM peut être lente sur de très gros fichiers (> 5 Mo).

### 7.3 Axes d'Amélioration pour OCE

- **Détection** : Intégrer un clustering hiérarchique pour mieux gérer les variantes structurelles.
- **Inférence** : Remplacer le vote heuristique par un modèle Bayésien entraîné.
- **Sortie** : Produire un JSON structuré en plus du Markdown.
- **Profils** : Permettre une fine personnalisation via des fichiers YAML (bien que l'approche agnostique reste la valeur par défaut).

---

## 8. Feuille de Route vers OCE (OmniChat Extractor)

| Phase | Objectif | Livrables |
|-------|----------|-----------|
| **Phase 1 (actuelle)** | ACE Light stable | Détecteur topologique fonctionnel, tests golden, CLI |
| **Phase 2** | Amélioration du clustering | Signature adaptative (Jaccard, edit distance), mode flux robuste |
| **Phase 3** | Inférence Bayésienne | Modèle léger entraîné, confiance calibrée |
| **Phase 4** | Sortie enrichie | JSON avec métadonnées, frontmatter YAML |
| **Phase 5** | Profils déclaratifs | Détection auto de la source, personnalisation YAML |
| **Phase 6** | Packaging et distribution | Publication PyPI, documentation Sphinx |

---

## 9. Annexes

### 9.1 Glossaire

- **Sanctuaire** : Mécanisme d'extraction et de protection des contenus complexes.
- **Topologique** : Relatif à la structure du DOM (profondeur, relations parent-enfant, répétitivité).
- **Golden File** : Fichier de référence utilisé pour les tests de non-régression.
- **UUID** : Identifiant unique utilisé comme placeholder dans le Sanctuaire.

### 9.2 Dépendances

- `beautifulsoup4` : Parsing HTML
- `pytest` : Framework de test (développement)
- Python ≥ 3.9

### 9.3 Références

- [ACE Light Implementation Plan](./docs/implementation/)
- [Audit du script original](./docs/audit_Vmonolithique+proposition.md)
- [Vision OCE](./docs/V_idéale.md)

---

**Ce document est la référence canonique du projet ACE. Toute contribution, audit ou critique doit s'y référer sans s'y cloisonée, toutes contribution innovente et pertinente a la résolution du but profond est le bienvenue (humain et ia) .**
