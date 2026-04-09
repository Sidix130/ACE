# [Atome 4] Le Dispatcher de Conversion

## 1. Objectif
Convertir le DOM en Markdown sans polluer la logique par des conditions infinies.

## 2. Implémentation
- Utiliser un dictionnaire `HANDLERS`.
- Pour chaque tag, appeler le handler correspondant.
- **Règle d'Or** : Si un nœud contient un UUID de type `__ACE_UUID__`, il doit être retourné tel quel.

## 3. Livrables
- `ace/engine/converter.py`
- `ace/processors/tables.py` (Helper pour les tables Markdown).

## 4. Test
`tests/test_atom_04.py`.
- Vérifier qu'une table HTML est convertie en table Markdown.
- Vérifier que les UUID sont préservés.
