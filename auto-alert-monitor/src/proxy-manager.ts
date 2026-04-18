import fs from 'fs';
import path from 'path';

export interface ProxyConfig {
    server: string;
    username?: string;
    password?: string;
}

export class ProxyManager {
    private proxies: ProxyConfig[] = [];
    private currentIndex = 0;
    private useProxies = false;

    constructor() {
        const configPath = path.resolve(__dirname, '../config/proxies.json');
        if (fs.existsSync(configPath)) {
            const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
            this.proxies = config.proxies;
            this.useProxies = config.use_proxies;
        }
    }

    getNextProxy(): ProxyConfig | undefined {
        if (!this.useProxies || this.proxies.length === 0) return undefined;
        
        const proxy = this.proxies[this.currentIndex];
        this.currentIndex = (this.currentIndex + 1) % this.proxies.length;
        return proxy;
    }
}

export const proxyManager = new ProxyManager();