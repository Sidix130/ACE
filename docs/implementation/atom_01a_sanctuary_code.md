# [Atome 1a] Sanctuaire Basique (Code)

## 1. Objectif
Isoler les balises `<pre>` et `<code>` avant toute conversion pour éviter que le Markdown ou le nettoyage ne corrompe le code utilisateur.

## 2. Spécification Algorithmique
1. `extract_code(soup)`:
   - Parcourir tous les éléments `pre`.
   - Extraire le texte brut.
   - Générer un UUID : `__ACE_CODE_<hash>__`.
   - Remplacer le nœud par l'UUID.
2. `restore_code(markdown_text, mapping)`:
   - Chercher les UUID et réinjecter le texte entouré de ` ``` `.

## 3. Livrable
`ace/core/sanctuary.py` (Base + Code).

## 4. Test (Mandatoire)
`tests/test_atom_01a.py` :
- Vérifier qu'un HTML avec un bloc `pre` est transformé en Markdown contenant l'UUID.
- Vérifier que la restauration redonne le bloc de code intact.
