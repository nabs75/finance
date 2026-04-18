import { chromium } from 'playwright-extra';
import stealthPlugin from 'puppeteer-extra-plugin-stealth';
import { BaseScraper, Car, Filter } from './base';
import { proxyManager } from '../proxy-manager';

// @ts-ignore
chromium.use(stealthPlugin());

export class LaCentraleScraper extends BaseScraper {
    siteName = 'lacentrale';

    async search(filter: Filter): Promise<Car[]> {
        console.log(`[LA CENTRALE] Recherche pour ${filter.brand} ${filter.model}...`);
        
        const proxy = proxyManager.getNextProxy();
        const browser = await chromium.launch({ 
            headless: true,
            proxy: proxy ? { server: proxy.server, username: proxy.username, password: proxy.password } : undefined
        });
        const context = await browser.newContext();
        const page = await context.newPage();

        const query = encodeURIComponent(`${filter.brand} ${filter.model}`);
        const url = `https://www.lacentrale.fr/listing?makesModelsCommercialNames=${filter.brand.toUpperCase()}%3A${filter.model.toUpperCase()}&priceMax=${filter.price_max}`;

        const cars: Car[] = [];

        try {
            await page.goto(url, { waitUntil: 'networkidle' });
            await page.waitForTimeout(3000);

            const listings = await page.$$('div.SearchResult_container__-H7yP');
            
            for (const item of listings.slice(0, 10)) {
                const title = await item.$eval('h2', el => el.textContent || '');
                const priceText = await item.$eval('span.Price_price__2G9xR', el => el.textContent || '0');
                const price = parseInt(priceText.replace(/[^0-9]/g, ''));
                const relativeUrl = await item.$eval('a', el => el.getAttribute('href') || '');
                
                cars.push({
                    id: relativeUrl.split('-').pop()?.replace('/', '') || Math.random().toString(),
                    site: this.siteName,
                    title: title.trim(),
                    price,
                    url: `https://www.lacentrale.fr${relativeUrl}`
                });
            }
        } catch (error) {
            console.error(`[LA CENTRALE] Erreur:`, error);
        } finally {
            await browser.close();
        }

        return cars;
    }
}