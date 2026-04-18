import cron from 'node-cron';
import fs from 'fs';
import path from 'path';
import { LeBonCoinScraper } from './scrapers/leboncoin';
import { MobileDeScraper } from './scrapers/mobile';
import { AutoScout24Scraper } from './scrapers/autoscout24';
import { LaCentraleScraper } from './scrapers/lacentrale';
import { ParuVenduScraper } from './scrapers/paruvendu';
import { isNewCar, saveCar } from './db';

const configPath = path.resolve(__dirname, '../config/filters.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

const scrapers = [
    new LeBonCoinScraper(),
    new MobileDeScraper(),
    new AutoScout24Scraper(),
    new LaCentraleScraper(),
    new ParuVenduScraper()
];

const runMonitor = async () => {
    console.log(`🚀 [MONITOR] Démarrage du scan : ${new Date().toLocaleString()}`);

    // Jules Optimization: Parallel execution of scrapers for all filters
    const tasks = config.filters.flatMap((filter: any) => 
        scrapers
            .filter(scraper => filter.sites.includes(scraper.siteName))
            .map(scraper => ({ scraper, filter }))
    );

    await Promise.all(tasks.map(async ({ scraper, filter }: any) => {
        try {
            const cars = await scraper.search(filter);
            for (const car of cars) {
                if (isNewCar(car.id)) {
                    console.log(`✨ [NEW] ${car.title} trouvé sur ${car.site}`);
                    saveCar(car);
                    await sendAlert(car);
                }
            }
        } catch (error) {
            console.error(`❌ Erreur critique pour ${scraper.siteName} [${filter.id}]:`, error);
        }
    }));
    
    console.log(`✅ [MONITOR] Scan terminé. Prochain passage dans 15 minutes.`);
};

// Exécuter immédiatement au démarrage
runMonitor();

// Programmer toutes les 15 minutes
cron.schedule('*/15 * * * *', runMonitor);

console.log('🤖 Auto-Alert Monitor est en ligne. Appuyez sur Ctrl+C pour arrêter.');