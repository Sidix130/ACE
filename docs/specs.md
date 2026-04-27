# Principes fondamentaux des spécifications OmegaEngine (ΩSpec)

Toute spécification – qu’elle soit rédigée en Markdown, Gherkin, P, TLA+, Dafny, Lean ou encapsulée dans MetaSpec – doit respecter les **sept principes** suivants. Ces principes garantissent que le système reste fiable, traçable et évolutif.

---

## 1. Séparation des préoccupations (Separation of Concerns)

**Principe** : Chaque couche de spécification (L0 à L5) a un rôle unique et non chevauchant.

| Couche | Rôle | Ce qu’elle ne doit **pas** faire |
|--------|------|----------------------------------|
| L0 (Markdown) | Capturer l’intention, le contexte, les décisions | Contenir du code exécutable ou des assertions formelles |
| L1 (Gherkin) | Décrire des comportements observables et des scénarios de test | Définir des invariants temporels ou des preuves |
| L2 (P) | Modéliser des machines à états concurrentes et des protocoles | Spécifier des propriétés globales sur de longs horizons |
| L3 (TLA+/Quint) | Exprimer des invariants temporels et des propriétés de sûreté/ vivacité | Décrire des tests unitaires |
| L4 (Dafny) | Prouver la correction de code algorithmique pur | Modéliser la concurrence |
| L5 (Lean) | Formaliser des structures mathématiques profondes | Remplacer les tests ou le model checking |

**Règle** : Si une propriété peut être exprimée à un niveau inférieur (plus concret), elle ne doit pas être dupliquée dans un niveau supérieur.

---

## 2. Traçabilité ascendante (Upward Traceability)

**Principe** : Tout énoncé dans une couche concrète (ex: Dafny) doit pouvoir être relié à un énoncé plus abstrait (ex: Gherkin) qui le justifie.

- Chaque `hyperConstraint` dans MetaSpec doit lier au moins une facette d’un niveau supérieur à une facette d’un niveau inférieur.
- Exemple : un invariant Dafny (`core.invariants`) doit être associé à un scénario Gherkin (`behavior.events`) via une hyper‑contrainte de type `semantic`.

**Règle** : Pas de code ou preuve orpheline. Toute spécification bas niveau a un parent dans la couche immédiatement supérieure.

---

## 3. Exécutabilité partielle (Partial Executability)

**Principe** : Au moins une facette de chaque module doit être exécutable ou vérifiable automatiquement.

- L1 (Gherkin) → exécutable par `behave` / `pytest-bdd`.
- L2 (P) → model checking.
- L3 (TLA+) → model checking (TLC, Apalache).
- L4 (Dafny) → preuve automatique.
- L5 (Lean) → preuve interactive (moins automatisée, mais acceptable).

**Règle** : Un module qui ne contient **aucune** facette exécutable est considéré comme une spécification incomplète et ne peut être intégré.

---

## 4. Non‑redondance (No Duplication)

**Principe** : Une même propriété ou contrainte n’est spécifiée qu’à un seul endroit, dans la couche la plus appropriée.

- Les invariants temporels sont dans TLA+, pas dans Dafny.
- Les scénarios d’acceptation sont dans Gherkin, pas dans les tests unitaires Python.

**Règle** : Avant d’ajouter une spécification, vérifier si la même information n’existe pas déjà dans une autre facette ou un autre module. La duplication entraîne des dérives de cohérence.

---

## 5. Cohérence transversale via hyper‑contraintes (Cross‑Layer Coherence)

**Principe** : Toute garantie apportée par une couche doit être compatible avec les garanties des autres couches.

- Les `hyperConstraints` de MetaSpec sont l’outil unique pour exprimer ces relations.
- Une hyper‑contrainte de type `coherence` vérifie que deux facettes (ex: un invariant TLA+ et un scénario Gherkin) ne se contredisent pas.

**Règle** : Pour chaque paire de facettes potentiellement contradictoires, il doit exister une hyper‑contrainte (ou une justification documentée de l’absence de contradiction).

---

## 6. Versionnement et immutabilité (Versioning & Immutability)

**Principe** : Une fois qu’une spécification (ou un module) a été validée et figée (via le Spec Commit Gate), elle ne peut plus être modifiée ; on crée une nouvelle version.

- Chaque module contient un champ `core.version` (suivant semver).
- Le `bootstrapCore.version` est la version du méta‑modèle.
- Toute modification d’une spécification existante doit aboutir à une nouvelle version (incrémentation).

**Règle** : Les fichiers de spécification sont immuables après validation. Les modifications passent par un fork ou un nouveau module.

---

## 7. Minimalisme (Keep It Specified, Stupid – KISS)

**Principe** : Une spécification ne doit contenir que ce qui est **nécessaire** pour garantir la confiance dans le composant.

- Ne pas spécifier des comportements triviaux (ex: “une variable entière ne devient pas négative” si le type le garantit déjà).
- Ne pas sur‑spécifier : laisser des degrés de liberté à l’implémentation sauf s’ils sont critiques.

**Règle** : Avant d’ajouter une règle, se demander : “Cette règle peut‑elle être violée sans que le système perde sa fiabilité ?” Si oui, ne pas la spécifier.

---

## 8. Auditabilité (Auditability) – principe additionnel

**Principe** : Chaque décision de conception, chaque modification de spécification doit être enregistrée avec un hash, un auteur, une date et un lien vers une justification.

- Le champ `core.dependencies` liste les modules et versions dont dépend ce module.
- `bootstrapCore` contient un `contentHash` (SHA‑256) du fichier.
- Les hyper‑contraintes sont horodatées (ajouter `timestamp` dans le schéma).

**Règle** : Pas de spécification sans hash, pas de changement sans traçabilité.

---

## Application dans MetaSpec

Ces principes sont traduits dans le schéma MetaSpec par :

- **Séparation** : les quatre facettes (`core`, `behavior`, `execution`, `semantics`).
- **Traçabilité** : les `hyperConstraints` avec `premises` et `target` pointant vers des facettes.
- **Exécutabilité** : les champs `execution.tests`, `execution.codegen`, `behavior.stateMachine`.
- **Non‑redondance** : à vérifier manuellement (pas de contrainte automatique, mais une règle de revue).
- **Cohérence** : les hyper‑contraintes de type `coherence`, `dependency`, etc.
- **Versionnement** : champs `version` dans `core` et `bootstrapCore`.
- **Minimalisme** : à vérifier en revue (pas de validation automatique).
- **Auditabilité** : `contentHash`, `timestamp` (à ajouter), `dependencies`.

---

## Conclusion

Ces principes ne sont pas négociables. Toute spécification – qu’elle soit écrite par un humain ou générée par une IA – doit y satisfaire. Le validateur d’hyper‑contraintes (que tu vas implémenter) devra vérifier au moins les principes 1, 2, 5 et 6 automatiquement. Les principes 3, 4, 7 et 8 relèvent de la revue humaine (ou d’une vérification statique avancée).

Si tu es d’accord, j’intègre ces principes dans le fichier `docs/00_architecture.md` et dans la documentation du schéma MetaSpec.
