# Stratégie Séquentielle ACE Révisée (V2)

## 0. Pré-requis : Le Kit de Test
Chaque atome est validé par un script `pytest` situé dans `tests/`. **Je m'interdis de passer à l'atome suivant si les tests ne sont pas au vert.**

## 1. Roadmap des Atomes

### [Atome 0] Fondations & Environnement
- **Cible** : `pyproject.toml`, `ace/models/chat.py`, `ace/utils/dom.py`.
- **Test** : `tests/test_atom_00.py` (vérifie importabilité et typage).
- **Note** : Installer `beautifulsoup4` et `pytest`.

### [Atome 1a] Sanctuaire Basique (Code)
- **Cible** : `ace/core/sanctuary.py` (Structure de base + gestion Code).
- **Test** : `tests/test_atom_01a.py` (Vérifie l'extraction des balises `<pre>` et `<code>`).

### [Atome 1b] Sanctuaire Expert (Mermaid & LaTeX)
- **Cible** : `ace/core/sanctuary.py` (Extension Mermaid Grok `}}%%` et LaTeX DeepSeek `data-latex`).
- **Test** : `tests/test_atom_01b.py` (Assertions sur des chaînes complexes réelles).

### [Atome 2] L'Engin de Topologie
- **Cible** : `ace/engine/detector.py`.
- **Algorithme** : Scoring simplifié, seuil densité = 3 mots, suppression des pénalités `<p>`.
- **Test** : `tests/test_atom_02.py` (Vérifie le découpage de conversations réelles).

### [Atome 3] L'Intelligence de Rôle
- **Cible** : `ace/engine/inferencer.py`.
- **Amélioration** : Fallback basé sur l'alternance confirmée.
- **Test** : `tests/test_atom_03.py` (Vérifie l'attribution des rôles).

### [Atome 4] Le Dispatcher de Conversion
- **Cible** : `ace/engine/converter.py`, `ace/processors/`.
- **Contrainte** : Les UUID du sanctuaire doivent survivre à la conversion.
- **Test** : `tests/test_atom_04.py`.

### [Atome 5] Orchestration finale
- **Cible** : `ace/main.py`.
- **Test** : `tests/test_atom_05.py` (Test bout-en-bout).

---

## 2. Guide d'Exécution pour moi-même (Gemini)
1. **Initialiser** le repo ACE.
2. **Écrire le test** de l'atome (en utilisant les fixtures existantes si possible).
3. **Implémenter** l'atome.
4. **Lancer** `pytest`.
5. **Ajuster** jusqu'au succès.
