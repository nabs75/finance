// Fonction universelle de mise à jour du dashboard
async function refreshDashboard() {
    try {
        const response = await fetch('status.json');
        const data = await response.json();

        // 1. Mise à jour de l'heure
        document.getElementById('last-update').innerText = data.update || data.last_update;

        // 2. Génération dynamique du tableau des 7 valeurs
        const tableBody = document.getElementById('trading-body');
        tableBody.innerHTML = ''; // Nettoyer le tableau existant

        data.assets.forEach(asset => {
            const row = document.createElement('tr');

            // Couleur du RSI (Alerte si < 30)
            const rsiClass = asset.rsi < 30 ? 'text-red-500 font-bold' : 'text-green-400';

            row.innerHTML = `
                <td class="px-4 py-2 border-b border-gray-700">${asset.symbol}</td>
                <td class="px-4 py-2 border-b border-gray-700">${asset.price} $</td>
                <td class="px-4 py-2 border-b border-gray-700 ${rsiClass}">${asset.rsi}</td>
                <td class="px-4 py-2 border-b border-gray-700">${asset.atr}</td>
                <td class="px-4 py-2 border-b border-gray-700">
                    <span class="px-2 py-1 rounded text-xs ${asset.rsi < 30 ? 'bg-red-900' : 'bg-blue-900'}">
                        ${asset.rsi < 30 ? 'SIGNAL' : 'SCAN'}
                    </span>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error("Erreur de synchronisation Jules:", error);
    }
}

// Rafraîchir toutes les 30 secondes
setInterval(refreshDashboard, 30000);
refreshDashboard();
