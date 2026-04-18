import Database from 'better-sqlite3';
import path from 'path';

const dbPath = path.resolve(__dirname, '../data/cars.db');

// Assurer que le dossier data existe
import fs from 'fs';
if (!fs.existsSync(path.dirname(dbPath))) {
    fs.mkdirSync(path.dirname(dbPath), { recursive: true });
}

const db = new Database(dbPath);

// Initialisation de la table
db.exec(`
  CREATE TABLE IF NOT EXISTS cars (
    id TEXT PRIMARY KEY,
    site TEXT,
    title TEXT,
    price INTEGER,
    url TEXT,
    seen_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

export const isNewCar = (id: string): boolean => {
    const row = db.prepare('SELECT id FROM cars WHERE id = ?').get(id);
    return !row;
};

export const saveCar = (car: { id: string, site: string, title: string, price: number, url: string }) => {
    const stmt = db.prepare('INSERT INTO cars (id, site, title, price, url) VALUES (?, ?, ?, ?, ?)');
    stmt.run(car.id, car.site, car.title, car.price, car.url);
};

export default db;