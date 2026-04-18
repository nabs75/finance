const express = require('express');
const helmet = require('helmet');
const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');
const app = express();
const port = 3000;

// Jules Security Directive: Use helmet for basic security headers
app.use(helmet({
    contentSecurityPolicy: false, // Désactivé pour simplifier le chargement des scripts locaux
}));

const db = new Database(path.resolve(__dirname, '../data/cars.db'));
const configPath = path.resolve(__dirname, '../config/filters.json');

app.use(express.static(path.resolve(__dirname, '../dashboard')));

app.get('/api/cars', (req, res) => {
    try {
        // Sélection chirurgicale des champs pour la performance et la confidentialité
        const cars = db.prepare('SELECT site, title, price, url, seen_at FROM cars ORDER BY seen_at DESC LIMIT 50').all();
        res.json(cars);
    } catch (error) {
        console.error('API Error:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/api/filters', (req, res) => {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    res.json(config.filters);
});

app.listen(port, () => {
    console.log(`📊 Dashboard disponible sur http://localhost:${port}`);
});