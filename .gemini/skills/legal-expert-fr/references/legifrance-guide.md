# Guide de Navigation Légifrance pour l'IA

## 1. Structure des URLs
Pour accéder directement aux ressources, privilégiez ces formats :
- **Codes** : `https://www.legifrance.gouv.fr/codes/texte_lc/[ID_DU_CODE]`
- **Jurisprudence** : `https://www.legifrance.gouv.fr/juri/id/[ID_ARRET]`
- **Journal Officiel** : `https://www.legifrance.gouv.fr/jorf/id/[ID_TEXTE]`

## 2. Recherche Ciblée
Lors de l'utilisation de `google_web_search`, utilisez les opérateurs suivants :
- `site:legifrance.gouv.fr "Code civil" article 1101`
- `site:legifrance.gouv.fr jurisprudence "licenciement sans cause réelle et sérieuse"`

## 3. Extraction de Données
- Utilisez `web_fetch` sur les pages de résultats pour extraire le texte intégral des articles.
- Attention : Légifrance peut avoir des structures HTML complexes. Priorisez l'extraction du bloc `<div class="content">` ou des balises d'articles.

## 4. Codes Majeurs (IDs)
- Code Civil : `LEGITEXT000006070721`
- Code du Travail : `LEGITEXT000006072050`
- Code de Commerce : `LEGITEXT000005634379`
- Code Pénal : `LEGITEXT000006070719`