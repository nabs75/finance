# 🏎️ Auto-Alert Monitor

Système de surveillance automobile multi-sites (France & Europe) avec alertes temps réel et Dashboard.

## 🌟 Fonctionnalités
- **Multi-sites** : LeBonCoin, LaCentrale, ParuVendu (FR) + Mobile.de, AutoScout24 (EU).
- **Anti-Bot** : Utilisation de Playwright Stealth & Rotation de Proxies.
- **Alertes** : Notifications instantanées via Telegram.
- **Dashboard** : Interface web moderne pour visualiser les trouvailles.
- **Anti-doublon** : Base de données SQLite pour ne jamais recevoir deux fois la même alerte.

## 🛠 Installation

1. Accédez au dossier : `cd auto-alert-monitor`
2. Installez les dépendances : `npm install`
3. Compilez le projet : `npx tsc`

## ⚙️ Configuration

### 1. Filtres (`config/filters.json`)
Définissez vos critères de recherche :
```json
{
  "filters": [
    {
      "id": "ma-recherche",
      "sites": ["leboncoin", "lacentrale", "mobile.de", "autoscout24", "paruvendu"],
      "brand": "Porsche",
      "model": "911",
      "price_max": 90000,
      "year_min": 2018
    }
  ]
}
```

### 2. Notifications Telegram (`.env`)
Créez un fichier `.env` à la racine :
```env
TELEGRAM_BOT_TOKEN=votre_token
TELEGRAM_CHAT_ID=votre_id
```

### 3. Proxies (`config/proxies.json`)
Si vous avez des proxies, ajoutez-les ici et passez `use_proxies` à `true`.

## 🚀 Lancement

### Lancer le bot de surveillance (Scraping) :
```bash
node dist/index.js
```

### Lancer le Dashboard (Interface Web) :
```bash
node src/server.js
```
Accédez ensuite à : `http://localhost:3000`

## ⚖️ Avertissement
Utilisez ce logiciel de manière responsable. Une fréquence de scan trop élevée peut entraîner un bannissement de votre adresse IP par les sites cibles.
