import { chromium } from 'playwright-extra';
import stealthPlugin from 'puppeteer-extra-plugin-stealth';
import { BaseScraper, Car, Filter } from './base';
import { proxyManager } from '../proxy-manager';

// @ts-ignore
chromium.use(stealthPlugin());

export class MobileDeScraper extends BaseScraper {
    siteName = 'mobile.de';

    async search(filter: Filter): Promise<Car[]> {
        console.log(`[MOBILE.DE] Recherche pour ${filter.brand} ${filter.model} en Europe...`);
        
        const proxy = proxyManager.getNextProxy();
        const browser = await chromium.launch({ 
            headless: true,
            proxy: proxy ? { server: proxy.server, username: proxy.username, password: proxy.password } : undefined
        });
        const context = await browser.newContext({
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            viewport: { width: 1280, height: 720 }
        });
        const page = await context.newPage();

        // Construction de l'URL Mobile.de (Simplifiée pour l'exemple)
        // Note: Mobile.de utilise des IDs de marque/modèle dans l'URL réelle, 
        // ici on utilise la recherche textuelle pour la flexibilité.
        const query = encodeURIComponent(`${filter.brand} ${filter.model}`);
        const url = `https://www.mobile.de/ru/auto/${filter.brand.toLowerCase()}-${filter.model.toLowerCase()}/vhc:car,pgn:1,pgs:10,prx:${filter.price_max},frn:${filter.year_min || ''}`;

        const cars: Car[] = [];

        try {
            await page.goto(url, { waitUntil: 'networkidle' });
            
            // Attendre le sélecteur d'annonces
            await page.waitForTimeout(4000);

            // Extraction (Sélecteurs basés sur la structure actuelle de Mobile.de)
            const listings = await page.$$('a.cBox-body--article');
            
            for (const item of listings.slice(0, 10)) {
                const title = await item.$eval('h3.h3', el => el.textContent || '');
                const priceText = await item.$eval('span.h3', el => el.textContent || '0');
                const price = parseInt(priceText.replace(/[^0-9]/g, ''));
                const url = await item.getAttribute('href') || '';
                const id = url.split('id=')[1]?.split('&')[0] || Math.random().toString();
                
                cars.push({
                    id,
                    site: this.siteName,
                    title: title.trim(),
                    price,
                    url: url.startsWith('http') ? url : `https://www.mobile.de${url}`
                });
            }
        } catch (error) {
            console.error(`[MOBILE.DE] Erreur lors du scraping:`, error);
        } finally {
            await browser.close();
        }

        return cars;
    }
}