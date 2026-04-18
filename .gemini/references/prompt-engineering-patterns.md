# Patterns de Prompt Engineering Avancé

## 1. Chain-of-Thought (CoT)
Force l'IA à décomposer son raisonnement avant de donner une réponse.
*Pattern:* "Analysons cela étape par étape : 1. ... 2. ... 3. Donc, la conclusion est..."

## 2. Few-Shot Prompting
Fournit des exemples de entrées/sorties pour "calibrer" le format de réponse.
*Pattern:* "Voici des exemples de transformation : A -> B, C -> D. Maintenant, transforme E -> ?"

## 3. Role-Based Orchestration
Définit une hiérarchie entre les agents.
- **Manager** : Planifie et révise.
- **Worker** : Exécute de manière chirurgicale.
- **Reviewer** : Critique et valide.

## 4. Reflexion Framework
Demande à l'IA de critiquer sa propre première ébauche avant de finaliser.
*Pattern:* "Génère une solution. Maintenant, trouve 3 défauts potentiels dans cette solution. Corrige ces défauts dans la version finale."