import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';

const dbPath = path.resolve(__dirname, '../data/news.db');

if (!fs.existsSync(path.dirname(dbPath))) {
    fs.mkdirSync(path.dirname(dbPath), { recursive: true });
}

const db = new Database(dbPath);

db.exec(`
  CREATE TABLE IF NOT EXISTS processed_news (
    guid TEXT PRIMARY KEY,
    title TEXT,
    source TEXT,
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

export const isAlreadyProcessed = (guid: string): boolean => {
    const row = db.prepare('SELECT guid FROM processed_news WHERE guid = ?').get(guid);
    return !!row;
};

export const markAsProcessed = (guid: string, title: string, source: string) => {
    const stmt = db.prepare('INSERT INTO processed_news (guid, title, source) VALUES (?, ?, ?)');
    stmt.run(guid, title, source);
};

export default db;