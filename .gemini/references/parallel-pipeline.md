# Guide d'Exécution Parallèle et Batch

## 1. Principe de Concurrence
Pour accélérer le traitement, utilisez des appels d'outils en parallèle.
- **Règle** : Si deux tâches ne modifient pas le même fichier, `wait_for_previous` doit être à `false`.
- **Exemple** : Lire 3 fichiers en même temps pour analyse.

## 2. Le Pipeline Hyper-Parallèle
Chaque fichier doit passer par ces 5 états :
1. **[A] ANALYSE** : Compréhension du rôle du fichier.
2. **[T] TEST** : Vérification de la couverture de tests.
3. **[S] SÉCURITÉ** : Recherche de vulnérabilités (secrets, injections).
4. **[C] CORRECTION** : Application des correctifs basés sur A, T et S.
5. **[U] UPDATE** : Mise à jour des imports et optimisation.

## 3. Matrice d'État (Template)
| Fichier | Analyse | Test | Sécu | Fix | Update |
| :--- | :---: | :---: | :---: | :---: | :---: |
| file1.ts | ✅ | ✅ | ⚠️ | 🛠 | ⏳ |
| file2.ts | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |

## 4. Stratégie de Batch
Ne traitez pas tout le projet d'un coup.
- **Taille de lot recommandée** : 3 à 5 fichiers.
- **Validation** : Lancez le linter/compiler après chaque lot.