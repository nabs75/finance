import { chromium } from 'playwright-extra';
import stealthPlugin from 'puppeteer-extra-plugin-stealth';
import { BaseScraper, Car, Filter } from './base';
import { proxyManager } from '../proxy-manager';

// @ts-ignore
chromium.use(stealthPlugin());

export class LeBonCoinScraper extends BaseScraper {
    siteName = 'leboncoin';

    async search(filter: Filter): Promise<Car[]> {
        console.log(`[LBC] Recherche pour ${filter.brand} ${filter.model}...`);
        
        const proxy = proxyManager.getNextProxy();
        const browser = await chromium.launch({ 
            headless: true,
            proxy: proxy ? { server: proxy.server, username: proxy.username, password: proxy.password } : undefined
        });
        const context = await browser.newContext({
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        });
        const page = await context.newPage();

        // Construction de l'URL de recherche (simplifiée pour l'exemple)
        const query = encodeURIComponent(`${filter.brand} ${filter.model} ${filter.version || ''}`);
        const url = `https://www.leboncoin.fr/recherche?category=2&text=${query}&price=min-${filter.price_max}`;

        const cars: Car[] = [];

        try {
            await page.goto(url, { waitUntil: 'networkidle' });
            
            // Attendre que les annonces chargent
            await page.waitForTimeout(3000);

            // Extraction des données (Sélecteurs à adapter selon le DOM actuel de LBC)
            const listings = await page.$$('div[data-qa-id="aditem_container"]');
            
            for (const item of listings.slice(0, 10)) {
                const title = await item.$eval('p[data-qa-id="aditem_title"]', el => el.textContent || '');
                const priceText = await item.$eval('span[data-qa-id="aditem_price"]', el => el.textContent || '0');
                const price = parseInt(priceText.replace(/[^0-9]/g, ''));
                const relativeUrl = await item.$eval('a', el => el.getAttribute('href') || '');
                const id = relativeUrl.split('/').pop()?.split('.')[0] || Math.random().toString();
                
                cars.push({
                    id,
                    site: this.siteName,
                    title,
                    price,
                    url: `https://www.leboncoin.fr${relativeUrl}`
                });
            }
        } catch (error) {
            console.error(`[LBC] Erreur lors du scraping:`, error);
        } finally {
            await browser.close();
        }

        return cars;
    }
}