import { chromium } from 'playwright-extra';
import stealthPlugin from 'puppeteer-extra-plugin-stealth';
import { BaseScraper, Car, Filter } from './base';
import { proxyManager } from '../proxy-manager';

// @ts-ignore
chromium.use(stealthPlugin());

export class ParuVenduScraper extends BaseScraper {
    siteName = 'paruvendu';

    async search(filter: Filter): Promise<Car[]> {
        console.log(`[PARU VENDU] Recherche pour ${filter.brand} ${filter.model}...`);
        
        const proxy = proxyManager.getNextProxy();
        const browser = await chromium.launch({ 
            headless: true,
            proxy: proxy ? { server: proxy.server, username: proxy.username, password: proxy.password } : undefined
        });
        const context = await browser.newContext();
        const page = await context.newPage();

        const query = encodeURIComponent(`${filter.brand} ${filter.model}`);
        const url = `https://www.paruvendu.fr/auto-moto/listefo/default/default?pxmax=${filter.price_max}&r=${filter.brand}&m=${filter.model}`;

        const cars: Car[] = [];

        try {
            await page.goto(url, { waitUntil: 'networkidle' });
            await page.waitForTimeout(3000);

            const listings = await page.$$('div.ergov3-annonce');
            
            for (const item of listings.slice(0, 10)) {
                const title = await item.$eval('h3', el => el.textContent || '');
                const priceText = await item.$eval('div.ergov3-prixanno', el => el.textContent || '0');
                const price = parseInt(priceText.replace(/[^0-9]/g, ''));
                const url = await item.$eval('a', el => el.getAttribute('href') || '');
                
                cars.push({
                    id: url.split('-').pop()?.split('.')[0] || Math.random().toString(),
                    site: this.siteName,
                    title: title.trim().replace(/\s+/g, ' '),
                    price,
                    url: url
                });
            }
        } catch (error) {
            console.error(`[PARU VENDU] Erreur:`, error);
        } finally {
            await browser.close();
        }

        return cars;
    }
}