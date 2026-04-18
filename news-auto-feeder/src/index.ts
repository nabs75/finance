import Parser from 'rss-parser';
import fs from 'fs';
import path from 'path';
import cron from 'node-cron';
import { isAlreadyProcessed, markAsProcessed } from './db';
import { rewriteArticle } from './ai-rewriter';
import { publishToWordPress } from './wp-publisher';
import { postToSocialMedia } from './social-poster';
import { getDailyTrends, isTrending } from './trend-watcher';

const parser = new Parser();
const configPath = path.resolve(__dirname, '../config/sources.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

const runAutoFeeder = async () => {
    console.log(`\n🚀 [AUTO-FEEDER] Démarrage du cycle : ${new Date().toLocaleString()}`);

    const trends = await getDailyTrends();
    let allItems: any[] = [];

    // Collecte de tous les items
    for (const source of config.sources) {
        try {
            const feed = await parser.parseURL(source.url);
            feed.items.forEach(item => {
                allItems.push({ ...item, sourceName: source.name });
            });
        } catch (error) {
            console.error(`❌ Erreur sur la source ${source.name}:`, error);
        }
    }

    // Jules Optimization: Prioriser les articles qui matchent les tendances
    allItems.sort((a, b) => {
        const aTrend = isTrending(a.title || '', trends) ? 1 : 0;
        const bTrend = isTrending(b.title || '', trends) ? 1 : 0;
        return bTrend - aTrend;
    });

    console.log(`📊 Articles collectés : ${allItems.length}. Traitement des plus pertinents...`);

    // Traitement des 10 meilleurs articles (priorisés par trends)
    for (const item of allItems.slice(0, 10)) {
        const guid = item.guid || item.link || '';
        
        if (isAlreadyProcessed(guid)) continue;

        const originalArticle = {
            title: item.title || '',
            content: item.contentSnippet || item.content || '',
            source: item.sourceName,
            url: item.link || ''
        };

        const rewrittenArticle = await rewriteArticle(originalArticle);
        
        if (rewrittenArticle) {
            const success = await publishToWordPress(rewrittenArticle);
            
            if (success) {
                markAsProcessed(guid, originalArticle.title, item.sourceName);
                // Lancement de la publication sociale
                await postToSocialMedia(rewrittenArticle);
            }
        }
    }

    console.log(`\n✅ [AUTO-FEEDER] Cycle terminé. Prochain scan dans 1 heure.`);
};

// Lancement immédiat au démarrage
runAutoFeeder();

// Planification toutes les heures
cron.schedule('0 * * * *', runAutoFeeder);

console.log('🤖 News Auto-Feeder est en ligne. Appuyez sur Ctrl+C pour arrêter.');