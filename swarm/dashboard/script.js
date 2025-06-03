// Configuration
const API_URL = `http://${window.location.hostname}:5000/health`;
const REFRESH_INTERVAL = 10000; // 10 secondes

// Variables globales
let refreshTimer;

// Démarrage automatique
document.addEventListener('DOMContentLoaded', function() {
    fetchData();
    startAutoRefresh();
});

async function fetchData() {
    const startTime = Date.now();
    
    try {
        const response = await fetch(API_URL);
        const responseTime = Date.now() - startTime;
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        updateUI(data, responseTime);
        updateStatus('online');
        
    } catch (error) {
        console.error('Failure to fectch data :', error);
        updateStatus('offline', error.message);
    }
}

function updateUI(data, responseTime) {
    // Informations du nœud
    document.getElementById('node-name').textContent = data.node;
    document.getElementById('last-update').textContent = 
        `Last update: ${new Date(data.timestamp).toLocaleString()}`;
    
    // Métriques CPU
    document.getElementById('cpu-usage').textContent = `${data.cpu.usage}%`;
    document.getElementById('cpu-cores').textContent = data.cpu.cores;
    document.getElementById('cpu-freq').textContent = data.cpu.frequency;
    
    // Barre de progression CPU
    const cpuBar = document.getElementById('cpu-bar');
    cpuBar.style.width = `${data.cpu.usage}%`;
    
    // Couleur selon l'utilisation
    cpuBar.className = 'progress-fill cpu-usage';
    if (data.cpu.usage > 80) cpuBar.classList.add('high');
    else if (data.cpu.usage > 60) cpuBar.classList.add('medium');
    
    // Temps de réponse
    document.getElementById('response-time').textContent = `${responseTime} ms`;
}

function updateStatus(status, errorMessage = '') {
    const statusElement = document.getElementById('node-status');
    
    if (status === 'online') {
        statusElement.textContent = '🟢 Online';
        statusElement.className = 'status online';
    } else {
        statusElement.textContent = '🔴 Offline';
        statusElement.className = 'status offline';
        
        if (errorMessage) {
            console.log('Erreur:', errorMessage);
        }
    }
}

function startAutoRefresh() {
    refreshTimer = setInterval(fetchData, REFRESH_INTERVAL);
}

function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
}

// Gestion de la visibilité de la page (pause si onglet inactif)
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
        fetchData(); // Refresh immédiat au retour
    }
});