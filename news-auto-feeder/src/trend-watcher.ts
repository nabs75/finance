// @ts-ignore
import googleTrends from 'google-trends-api';

export const getDailyTrends = async (): Promise<string[]> => {
    console.log('🔍 Analyse des tendances actuelles (France)...');
    
    try {
        const results = await googleTrends.dailyTrends({
            geo: 'FR',
        });

        const data = JSON.parse(results);
        const trends: string[] = [];

        data.default.trendingSearchesDays.forEach((day: any) => {
            day.trendingSearches.forEach((search: any) => {
                trends.push(search.title.query.toLowerCase());
            });
        });

        console.log(`📈 Tendances détectées : ${trends.slice(0, 5).join(', ')}...`);
        return trends;
    } catch (error) {
        console.error('❌ Erreur lors de la récupération des tendances :', error);
        return [];
    }
};

export const isTrending = (title: string, trends: string[]): boolean => {
    const titleLower = title.toLowerCase();
    return trends.some(trend => titleLower.includes(trend));
};