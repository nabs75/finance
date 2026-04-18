export interface Car {
    id: string;
    site: string;
    title: string;
    price: number;
    url: string;
}

export interface Filter {
    id: string;
    brand: string;
    model: string;
    version?: string;
    price_max: number;
    year_min?: number;
    km_max?: number;
    countries?: string[];
}

export abstract class BaseScraper {
    abstract siteName: string;
    abstract search(filter: Filter): Promise<Car[]>;
}