# [Atome 3] L'Intelligence de Rôle (Inference)

## 1. Objectif
Déduire le rôle de l'intervenant pour chaque bloc de message.

## 2. Système de Vote Amélioré
- **Signaux Forts** :
  - Classe CSS contient `user`, `thought`, `assistant`, `model`, `human`.
  - Iconographie (balise `img` ou `svg` avec label alt).
- **Signaux Faibles** :
  - Longueur (plus long = souvent Model).
  - Présence de code (souvent Model).
- **Correction Audit : Alternance Intelligente**
  - Si le score est nul ou égal :
    - Regarder le tour précédent.
    - Si tour précédent = USER, alors MODEL.
    - Si aucun tour précédent, par défaut USER.

## 3. Livrable
`ace/engine/inferencer.py`.

## 4. Test
`tests/test_atom_03.py`.
- Vérifier l'alternance automatique sur un cas ambigu.
