# Kit de Test ACE

## 1. Pourquoi des tests ?
En tant qu'IA, je suis sujet à l'optimisme (croire que ma regex est parfaite). Les tests sont mes **garde-fous**.

## 2. Fixtures (Échantillons)
Pour chaque atome, je dois créer un dossier `tests/fixtures/` contenant :
- `grok_sample.html` : Un morceau de code avec Mermaid.
- `deepseek_sample.html` : Un morceau avec KaTeX.
- `generic_sample.html` : Une structure de chat classique.

## 3. Workflow de Validation
```bash
# Avant l'implémentation
# Je réfléchis au test
touch tests/test_atom_XX.py

# Après l'implémentation
pytest tests/test_atom_XX.py
```

## 4. Règle d'or
Si un test échoue, je n'essaie pas de le "contourner" en changeant le test. Je corrige l'implémentation pour qu'elle réponde à la spécification technique.
