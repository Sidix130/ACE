# Chat HTML to Markdown Converter

Un outil en ligne de commande permettant d'extraire des conversations (chats) à partir de fichiers HTML exportés (comme ceux de ChatGPT ou Google AI Studio) vers un format Markdown propre et lisible.

L'outil fonctionne **sans présets spécifiques**. Il analyse la structure du DOM, détecte la topologie des messages et l'alternance des rôles de façon agnostique, ce qui le rend résilient aux mises à jour des interfaces utilisateur.

## Usage
`python clean.py <fichier_entree.html> [fichier_sortie.md]`
