# 🚀 Alpha-5 : Trading Bot & Dashboard

Ce projet est un agent de trading autonome conçu pour surveiller un portefeuille d'actions et sécuriser les profits à +5%.

## 🛠 Architecture
- **bot.py** : Moteur de surveillance en temps réel (WebSockets) et exécution des ordres via Alpaca.
- **app.py** : Interface utilisateur (Streamlit) pour visualiser les profits et les positions.
- **requirements.txt** : Dépendances Python nécessaires.

## 🤖 Instructions pour l'Agent (Jules)
1. **Setup** : Installer les dépendances via `pip install -r requirements.txt`.
2. **Variables d'Environnement** : L'agent doit configurer les secrets suivants :
   - `ALPACA_API_KEY`
   - `ALPACA_SECRET_KEY`
   - `ALPACA_BASE_URL` (https://paper-api.alpaca.markets pour test ou https://api.alpaca.markets pour live)
3. **Exécution** :
   - Lancer le bot : `python bot.py`
   - Lancer le Dashboard : `streamlit run app.py`

## 📈 Stratégie de Trading
- **Signal** : Hausse de l'action de ≥ 5.0% par rapport au prix de revient moyen.
- **Action** : Vente immédiate au prix du marché (Market Order).
- **Virement** : Transfert des profits vers Revolut chaque vendredi à 22h00 (heure de New York).

## ⚠️ Sécurité
- Ne jamais engager plus de 20% du capital total sur une seule position.
- En cas d'erreur de connexion API répétée (3 fois), l'agent doit stopper les ordres et alerter l'utilisateur.