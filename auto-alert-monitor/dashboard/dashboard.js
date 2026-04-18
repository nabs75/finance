/**
 * Dashboard Logic - UI/UX Pro
 */

// Simulation de données (En attendant l'API réelle liée à SQLite)
const mockCars = [
    { id: '1', site: 'leboncoin', title: 'Porsche 911 Carrera S', price: 85000, url: '#', seen_at: '2026-04-17 22:30' },
    { id: '2', site: 'mobile.de', title: 'Audi RS3 Sportback', price: 69900, url: '#', seen_at: '2026-04-17 22:45' },
    { id: '3', site: 'lacentrale', title: 'BMW M2 Competition', price: 58000, url: '#', seen_at: '2026-04-17 21:15' }
];

const renderCars = (cars) => {
    const grid = document.getElementById('cars-grid');
    grid.innerHTML = '';

    cars.forEach(car => {
        const card = document.createElement('a');
        card.href = car.url;
        card.target = '_blank';
        card.className = 'car-card';
        
        card.innerHTML = `
            <span class="car-site">${car.site}</span>
            <h3 class="car-title">${car.title}</h3>
            <div class="car-price">${new Intl.NumberFormat('fr-FR').format(car.price)} €</div>
            <span class="car-date">Détecté le ${new Date(car.seen_at).toLocaleString()}</span>
        `;
        
        grid.appendChild(card);
    });

    document.getElementById('total-scanned').innerText = cars.length;
    document.getElementById('active-filters').innerText = '2';
};

const renderFilters = (filters) => {
    const list = document.getElementById('filters-list');
    list.innerHTML = '';
    
    filters.forEach(f => {
        const item = document.createElement('span');
        item.className = 'filter-badge';
        item.innerText = `${f.brand} ${f.model} (< ${f.price_max}€)`;
        list.appendChild(item);
    });
    
    document.getElementById('active-filters').innerText = filters.length;
};

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    const fetchData = async () => {
        try {
            const [carsRes, filtersRes] = await Promise.all([
                fetch('/api/cars'),
                fetch('/api/filters')
            ]);
            
            const cars = await carsRes.json();
            const filters = await filtersRes.json();
            
            renderCars(cars);
            renderFilters(filters);
        } catch (error) {
            console.error('Erreur lors de la récupération des données:', error);
        }
    };

    fetchData();
    setInterval(fetchData, 60000);
});