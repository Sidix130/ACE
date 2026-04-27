# [Atome 2] L'Engin de Topologie (Detection)

## 1. Objectif
Détecter les conteneurs de messages en évitant les heuristiques fragiles de `clean.py`.

## 2. Algorithme de Détection Amélioré (V-Light)
1. **Extraction des candidats** : Tous les tags `div` ou `article` ayant une densité textuelle > 3 mots.
2. **Scoring des parents** :
   - +5 points par enfant ayant un "Role Signal" (classe contenant 'user', 'assistant', 'message').
   - +2 points pour l'alternance de classes chez les enfants.
   - **Supprimé** : Pénalité des balises texte (`p`, `li`).
   - **Supprimé** : Bonus de profondeur relative arbitraire.
3. **Sélection** : Choisir le premier parent qui englobe au moins 2 enfants à fort score.

## 3. Livrable
`ace/engine/detector.py`.

## 4. Test
`tests/test_atom_02.py` :
- Tester avec un export "complexe" (AI Studio).
- Vérifier que le nombre de tours détectés correspond à la réalité.
