export const getPosts = async () => {
    const WP_URL = process.env.NEXT_PUBLIC_WP_URL;
    
    // Jules Directive: Provide high-quality mock data if no WP_URL is set
    const mockPosts = [
        {
            id: 1,
            date: new Date().toISOString(),
            title: { rendered: "L'IA révolutionne la médecine génomique en 2026" },
            excerpt: { rendered: "Une percée majeure dans le séquençage ADN piloté par l'IA promet de guérir des maladies auparavant incurables..." },
            _embedded: {
                'wp:featuredmedia': [{ source_url: "https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&q=80&w=800" }]
            }
        },
        {
            id: 2,
            date: new Date().toISOString(),
            title: { rendered: "Exploration spatiale : Une base autonome sur Mars d'ici 2030" },
            excerpt: { rendered: "Les agences spatiales mondiales s'unissent pour lancer le projet 'Red Horizon', une colonie martienne auto-suffisante..." },
            _embedded: {
                'wp:featuredmedia': [{ source_url: "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&q=80&w=800" }]
            }
        },
        {
            id: 3,
            date: new Date().toISOString(),
            title: { rendered: "L'économie mondiale pivote vers l'énergie fusion" },
            excerpt: { rendered: "Les premiers réacteurs à fusion commerciale commencent à alimenter des villes entières, marquant la fin de l'ère fossile..." },
            _embedded: {
                'wp:featuredmedia': [{ source_url: "https://images.unsplash.com/photo-1518152006812-edab29b069ac?auto=format&fit=crop&q=80&w=800" }]
            }
        }
    ];

    if (!WP_URL) {
        console.log('💡 Mode Démo activé : Affichage des articles de test.');
        return mockPosts;
    }

    try {
        const res = await fetch(`${WP_URL}?_embed&per_page=10`, { next: { revalidate: 3600 } });
        if (!res.ok) return mockPosts; // Repli sur le mode démo en cas d'erreur
        return res.json();
    } catch (error) {
        console.error('Fetch error, switching to mock data:', error);
        return mockPosts;
    }
};