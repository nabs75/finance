import { chromium } from 'playwright-extra';
import stealthPlugin from 'puppeteer-extra-plugin-stealth';
import { BaseScraper, Car, Filter } from './base';
import { proxyManager } from '../proxy-manager';

// @ts-ignore
chromium.use(stealthPlugin());

export class AutoScout24Scraper extends BaseScraper {
    siteName = 'autoscout24';

    async search(filter: Filter): Promise<Car[]> {
        console.log(`[AUTOSCOUT24] Recherche pour ${filter.brand} ${filter.model} en Europe...`);
        
        const proxy = proxyManager.getNextProxy();
        const browser = await chromium.launch({ 
            headless: true,
            proxy: proxy ? { server: proxy.server, username: proxy.username, password: proxy.password } : undefined
        });
        const context = await browser.newContext({
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        });
        const page = await context.newPage();

        // URL de recherche AutoScout24 (Exemple pour l'Europe entière)
        // Construction dynamique simplifiée
        const brand = filter.brand.toLowerCase();
        const model = filter.model.toLowerCase();
        const url = `https://www.autoscout24.fr/lst/${brand}/${model}?sort=age&desc=1&cy=D%2CA%2CB%2CE%2CF%2CI%2CL%2CNL&priceto=${filter.price_max}&fregfrom=${filter.year_min || ''}&ustate=N%2CU`;

        const cars: Car[] = [];

        try {
            await page.goto(url, { waitUntil: 'networkidle' });
            await page.waitForTimeout(3000);

            // Extraction des annonces
            const listings = await page.$$('article.ListComponent_list-item__OC_Hm');
            
            for (const item of listings.slice(0, 10)) {
                try {
                    const title = await item.$eval('h2', el => el.textContent || '');
                    const priceText = await item.$eval('p[data-test="price"]', el => el.textContent || '0');
                    const price = parseInt(priceText.replace(/[^0-9]/g, ''));
                    const relativeUrl = await item.$eval('a', el => el.getAttribute('href') || '');
                    const id = relativeUrl.split('/').pop()?.split('?')[0] || Math.random().toString();
                    
                    cars.push({
                        id,
                        site: this.siteName,
                        title: title.trim(),
                        price,
                        url: `https://www.autoscout24.fr${relativeUrl}`
                    });
                } catch (e) {
                    // Ignorer les éléments qui ne sont pas des annonces valides (pubs, etc.)
                }
            }
        } catch (error) {
            console.error(`[AUTOSCOUT24] Erreur lors du scraping:`, error);
        } finally {
            await browser.close();
        }

        return cars;
    }
}