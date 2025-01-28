// Funkcja do pobierania statystyk anime z backendu
async function fetchAnimeStats() {
    try {
        const response = await fetch('/getAnimeStats', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Błąd w odpowiedzi sieciowej');
        }

        const data = await response.json();
        updateCharts(data);
    } catch (error) {
        console.error('Błąd podczas pobierania statystyk anime:', error);
    }
}

// Funkcja do aktualizowania danych na wykresach
function updateCharts(data) {
    // Aktualizuj dane dla wykresu statusu anime
    const statusCounts = data.statusData.map(item => item.count);
    const statusLabels = data.statusData.map(item => item.status);

    animeStatusChart.data.labels = statusLabels;
    animeStatusChart.data.datasets[0].data = statusCounts;
    animeStatusChart.update();

    // Aktualizuj dane dla wykresu typu anime
    const typeCounts = data.typeData.map(item => item.count);
    const typeLabels = data.typeData.map(item => item.type);

    animeTypeChart.data.labels = typeLabels;
    animeTypeChart.data.datasets[0].data = typeCounts;
    animeTypeChart.update();
}

// Inicjalizacja wykresu statusu anime
const ctx1 = document.getElementById('animeStatusChart').getContext('2d');
const animeStatusChart = new Chart(ctx1, {
    type: 'doughnut',
    data: {
        labels: [],
        datasets: [{
            label: 'Anime Status',
            data: [],
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
        }]
    }
});

// Inicjalizacja wykresu typu anime
const ctx2 = document.getElementById('animeTypeChart').getContext('2d');
const animeTypeChart = new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Anime Type',
            data: [],
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Wykonaj zapytanie do serwera po załadowaniu strony i pobierz dane
fetchAnimeStats();
