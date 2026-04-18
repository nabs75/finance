# Standards de Qualité - Méthodologie "Jules" (Google-Inspired)

## 1. Principes SRE (Site Reliability Engineering)
- **Error Budgets** : Ne sacrifiez jamais la stabilité pour la vitesse.
- **Monitoring** : Chaque nouveau module doit être "observable".
- **Simplicité** : Si le code est trop complexe pour être expliqué en 3 phrases, rejetez-le.

## 2. Style de Code (Exigences)
- **Documentation** : Pas de fonctions "magiques". Chaque export doit être documenté.
- **Tests** : Couverture minimale de 80% exigée pour toute approbation par Jules.
- **Sécurité** : Audit systématique des dépendances tierces.

## 3. Protocole de Supervision
Lorsqu'un agent propose une modification :
1. **Validation de l'Intention** : Est-ce nécessaire ?
2. **Revue de l'Impact** : Quels sont les effets de bord ?
3. **Optimisation** : Peut-on faire plus propre / plus rapide ?
4. **Décision** : `APPROVED`, `REQUEST_CHANGES`, ou `BLOCKED`.