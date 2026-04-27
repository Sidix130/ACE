# Diagnostic : Perte de la Structure Markdown et Échec du Détecteur Topologique

Vous avez parfaitement raison de vous inquiéter. **La suppression de la mise en page Markdown n'a jamais été dans les plans d'ACE.** Au contraire, l'objectif central est de **préserver et convertir fidèlement** la richesse structurelle des conversations (diagrammes Mermaid, blocs de code, tableaux, listes, etc.) dans un format Markdown propre et réutilisable.

Le résultat que vous montrez — un diagramme Mermaid entier écrasé sous un simple `## User` avec un bloc de code — est un **bug critique** causé par une **mauvaise segmentation des tours** et une **mauvaise interprétation du contenu**. Ce n'est pas un choix de conception, c'est une **régression fonctionnelle** introduite par les récents changements dans le détecteur.

---

## 1. Ce qui s'est réellement passé

D'après les logs que vous avez fournis :

- L'agent a tenté d'implémenter un `TopologicalDetector` plus agnostique.
- Les tests unitaires (`test_atom_02.py`) ont **échoué de manière répétée** :
  - `test_detect_turns_generic` : 2 tours attendus, 1 seul détecté.
  - `test_detect_turns_ai_studio_complex` : échec similaire.
  - `test_structural_clustering` : clustering incorrect.
- Le test de bout en bout (`test_atom_05.py`) a également échoué car le message "Bonjour" a disparu.

**Conséquence directe** : Le détecteur ne renvoie qu'un **seul bloc** (ou un bloc incorrect) pour toute la conversation, ce qui fait que tout le contenu est fusionné dans un unique "tour" (souvent mal étiqueté comme `User`), et le convertisseur Markdown traite alors l'ensemble comme un seul bloc de texte, perdant toute la segmentation et la hiérarchie des messages.

Le diagramme Mermaid, qui devrait être détecté par le **Sanctuaire** et réinjecté proprement, se retrouve noyé dans ce méta-bloc unique et est simplement wrappé dans ````mermaid``` par le convertisseur, mais sans les en-têtes de tours appropriés.

---

## 2. Pourquoi le `TopologicalDetector` a échoué

L'approche topologique est **théoriquement supérieure**, mais son implémentation actuelle souffre de plusieurs problèmes :

| Problème observé | Impact |
|------------------|--------|
| **Signature trop rigide** | Les messages avec des structures internes légèrement différentes (ex: un message avec image vs sans) sont séparés en clusters distincts. |
| **Gestion incorrecte de la profondeur** | Le détecteur choisit parfois des conteneurs trop hauts (ex: `<div class="chat">`) ou trop bas (ex: `<div class="content">`), cassant l'homogénéité. |
| **Absence de validation d'alternance** | Le détecteur ne vérifie pas que les blocs candidats peuvent effectivement constituer une conversation cohérente. |
| **Heuristique de flux (Grok) trop complexe** | La tentative de gérer les flux sans wrappers via des `<hr>` a ajouté de la fragilité. |

**Le `HeuristicDetector` précédent, bien que moins "pur", fonctionnait de manière fiable sur tous les cas tests.** Il utilisait des signaux simples (mots-clés dans les classes, densité de texte) et une validation d'alternance.

---

## 3. Préserver la richesse structurelle

L'objectif d'ACE **n'a jamais été de produire du texte brut** ou un Markdown appauvri. Nous voulons :

- Des en-têtes de niveau 2 pour chaque tour (`## User`, `## MODEL`).
- Des blocs de code avec coloration syntaxique.
- Des tableaux convertis en GFM.
- Des diagrammes Mermaid rendus directement (s'ils sont dans un bloc de code avec langage `mermaid`).
- Des formules mathématiques LaTeX correctement délimitées.

Le problème actuel est purement un **bug de segmentation**, pas une décision de conception. Une fois le détecteur stable rétabli, la sortie retrouvera sa richesse.

---

# Stratégie de Perfectionnement du `TopologicalDetector` et des Tests

Votre proposition est la bonne : plutôt que de revenir en arrière, nous allons **parfaire le détecteur topologique** et **renforcer les tests** pour garantir qu'il atteigne l'universalité promise sans sacrifier la structure Markdown. Voici une feuille de route détaillée.

## 1. Diagnostic des Défaillances Actuelles du `TopologicalDetector`

| Défaut observé | Cause racine | Impact |
|----------------|--------------|--------|
| **Détection d'un seul tour** sur `generic_chat_sample.html` | Le détecteur choisit le `<div class="chat">` comme bloc unique au lieu des deux `<div class="message user/assistant">`. | Fusion des tours → perte d'alternance et de structure. |
| **Détection partielle** sur `ai_studio_complex.html` | Il sélectionne le `<div class="message-content">` interne plutôt que le conteneur de tour `<ms-chat-turn>`. | Les tours ne sont pas isolés correctement. |
| **Clustering trop large** dans `test_structural_clustering` | Les trois `<div>` (deux `msg` et un `other`) sont renvoyés ensemble car la signature basée sur le parent est trop laxiste. | Inclusion de bruit (sidebar). |
| **Perte de contenu** (ex: "Bonjour" manquant) | Le bloc détecté englobe mal le premier message, ou l'inférence de rôle l'ignore. | Sortie incomplète. |

## 2. Améliorations Algorithmiques du `TopologicalDetector`

### 2.1. Signature Structurelle Enrichie et Normalisation Intelligente

**Problème** : La signature actuelle est trop sensible aux variations mineures (ex: `class="message user"` vs `class="message assistant"`).

**Solution** : Introduire une **similarité de Jaccard** sur les classes CSS et une **distance d'édition** sur la structure des enfants.

```python
def compute_signature(self, tag: Tag) -> dict:
    return {
        'name': tag.name,
        'classes': self._normalize_classes(tag.get('class', [])),
        'children_structure': self._children_signature(tag),
        'depth': self._relative_depth(tag),
        'text_density': self._text_density(tag)
    }

def signatures_compatible(self, sig1: dict, sig2: dict) -> bool:
    # Même nom de tag requis
    if sig1['name'] != sig2['name']:
        return False
    # Classes : similarité de Jaccard > 0.3
    if jaccard(sig1['classes'], sig2['classes']) < 0.3:
        return False
    # Structure des enfants : distance d'édition < 2
    if edit_distance(sig1['children_structure'], sig2['children_structure']) > 2:
        return False
    return True
```

### 2.2. Sélection du Niveau de Granularité Optimal (Résolution du "Goldilocks Problem")

**Problème** : Choisir entre le conteneur parent (`<div class="chat">`) et les conteneurs enfants (`<div class="message">`).

**Solution** : Appliquer un **score de conversation** qui favorise les groupes de nœuds **frères adjacents** ayant une **alternance potentielle de rôles**.

Algorithme en deux passes :

1. **Clustering par parent** : Pour chaque parent, grouper ses enfants directs par signature compatible.
2. **Scoring des groupes** :
   - Taille du groupe (doit être ≥ 2).
   - Régularité d'espacement (gaps entre indices).
   - Variance de densité textuelle (les messages ont des longueurs variables).
   - Présence de motifs d'alternance dans les classes (ex: `user` / `assistant`).

On sélectionne ensuite le groupe avec le **meilleur score** et on retourne ses éléments (les enfants directs, pas le parent).

```python
def detect(self, soup):
    best_group = None
    best_score = 0
    for parent in soup.find_all(True):
        children = [c for c in parent.children if isinstance(c, Tag)]
        # Grouper par signature compatible
        groups = self._cluster_children(children)
        for group in groups:
            if len(group) >= 2:
                score = self._score_conversation_group(group)
                if score > best_score:
                    best_score = score
                    best_group = group
    return sorted(best_group, key=lambda t: t.sourceline) if best_group else []
```

### 2.3. Validation d'Alternance et Nettoyage Post-Détection

Après avoir extrait les blocs candidats, on peut **filtrer les outliers** en vérifiant la cohérence des rôles inférés :

- Inférer les rôles sur les candidats.
- Si l'alternance est brisée (ex: deux `USER` consécutifs), vérifier si l'un des blocs est un "faux positif" (ex: une bannière de cookies) et le supprimer.
- Si la séquence est trop courte (< 2), élargir la recherche.

### 2.4. Gestion Spécifique des Flux Sans Conteneur (Style Grok)

Pour les conversations où les messages sont des éléments disparates séparés par `<hr>`, on peut activer un **mode flux** :

- Détecter une séquence d'éléments consécutifs (h3, blockquote, hr) avec une densité textuelle élevée.
- Utiliser les `<hr>` comme délimiteurs de tours.
- Regrouper les éléments entre deux `<hr>` comme un seul bloc de message.

Ce mode peut être déclenché automatiquement si aucun cluster de messages "en boîte" n'est trouvé.

## 3. Refonte des Tests pour une Validation Robuste

Les tests actuels vérifient uniquement le nombre de blocs détectés. Nous devons tester **la qualité de l'extraction complète**.

### 3.1. Tests Unitaires du Détecteur (Plus Fins)

- `test_detector_finds_correct_containers` : Utiliser des fixtures HTML avec des structures connues et vérifier que les tags retournés sont exactement ceux attendus (par `id` ou contenu).
- `test_detector_ignores_sidebar` : S'assurer qu'un élément de sidebar répétitif n'est pas inclus.
- `test_detector_handles_flat_structure` : Cas du flux Grok avec `<hr>`.

### 3.2. Tests d'Intégration avec Golden Files

Créer un dossier `tests/golden/` contenant pour chaque fichier d'entrée (`sample_chatgpt.html`) le fichier de sortie Markdown attendu (`sample_chatgpt.md`). Le test compare la sortie générée avec le golden file (en ignorant les variations mineures d'espaces).

Cela garantit que la **structure complète** (en-têtes, blocs de code, tableaux) est préservée.

### 3.3. Tests de Non-Régression sur le Sanctuaire

Ajouter des tests spécifiques pour vérifier que les diagrammes Mermaid et les formules LaTeX sont correctement extraits et réinjectés **dans le bon tour**.

## 4. Plan d'Implémentation Itératif

### Itération 1 : Stabilisation de la Signature et du Clustering

- Implémenter la similarité de Jaccard et la distance d'édition.
- Tester sur `generic_chat_sample.html` jusqu'à obtenir 2 blocs distincts.
- **Critère de succès** : Tous les tests unitaires de `test_atom_02.py` passent.

### Itération 2 : Score de Conversation et Sélection du Bon Parent

- Ajouter le scoring basé sur la régularité et l'alternance.
- Valider sur `ai_studio_complex.html`.
- **Critère de succès** : Extraction correcte des tours AI Studio.

### Itération 3 : Gestion du Mode Flux (Grok)

- Implémenter la détection de flux et le regroupement par `<hr>`.
- Tester sur l'export Grok réel (`syshoplexe-Grok.html`).
- **Critère de succès** : Le diagramme Mermaid est correctement wrappé dans un tour `MODEL` avec le texte environnant.

### Itération 4 : Golden Files et Validation Complète

- Créer les golden files pour chaque fixture.
- Exécuter des tests de bout en bout complets.
- **Critère de succès** : Tous les tests passent, la sortie Markdown est identique à la référence.

## 5. Préservation de la Riche Structure Markdown

À chaque itération, nous vérifierons que :

- Les en-têtes `## User` et `## MODEL` sont présents.
- Les blocs de code sont délimités par ```` ``` ```` avec le langage.
- Les tableaux sont convertis en GFM.
- Les formules mathématiques sont entre `$` ou `$$`.
- Les diagrammes Mermaid sont dans des blocs ````mermaid`.

Le **Sanctuaire** continue de fonctionner en arrière-plan et n'est pas affecté par les changements du détecteur.

## 6. Conclusion

En perfectionnant le `TopologicalDetector` avec une signature adaptative, un scoring de conversation et une validation d'alternance, nous pouvons atteindre l'universalité topologique **sans sacrifier la fidélité structurelle**. Les tests renforcés garantiront que toute régression est immédiatement détectée.

Cette approche transforme l'échec actuel en une opportunité de construire un détecteur véritablement robuste, digne de la vision d'ACE.
