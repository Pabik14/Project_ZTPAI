async function fetchAnime(data) {
    const response = await fetch("/searchAnime", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error('Błąd sieciowy podczas pobierania danych.');
    }

    return await response.json();
}

document.querySelector('#status-filter').addEventListener('change', async function() {
    updateAnimeList();
});

document.querySelector('#search-input').addEventListener('keyup', async function(e) {
    updateAnimeList();
});

document.querySelector('#reset-search').addEventListener('click', async function() {
    document.querySelector('#search-input').value = ''; 
    document.querySelector('#status-filter').value = ''; 
    updateAnimeList();
});

async function updateAnimeList() {
    const query = document.querySelector('#search-input').value.trim();
    const status = document.querySelector('#status-filter').value;

    try {
        const data = { search: query, status: status };

        const animeList = await fetchAnime(data);

        renderAnimeList(animeList);
    } catch (error) {
        console.error('Błąd podczas wyszukiwania:', error);
    }
}

function renderAnimeList(animeList) {
    const animeListContainer = document.querySelector('.anime-table tbody');

    animeListContainer.innerHTML = '';

    if (animeList.length > 0) {
        animeList.forEach(anime => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${anime.anime_name}</td>
                <td>${anime.category}</td>
                <td>${anime.type}</td>
                <td>${anime.status}</td>
                <td>${anime.episodes_count}</td>
                <td>
                    <img 
                        src="public/img/x.png" 
                        alt="Delete" 
                        class="delete-anime x-delete" 
                        data-anime-id="${anime.id}" 
                    >
                </td>
            `;
            animeListContainer.appendChild(row);
        });
    } else {
        animeListContainer.innerHTML = '<tr><td colspan="6">No results!</td></tr>';
    }
}

document.querySelector('#anime-table-body').addEventListener('click', async function(event) {
    if (event.target.classList.contains('delete-anime')) {
        const animeId = event.target.dataset.animeId; 

        console.log('Clicked delete for anime ID:', animeId); 

        if (animeId) {
            try {
                const response = await fetch('/deleteAnime', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ anime_id: animeId })
                });

                const result = await response.json();

                if (result.success) {
                    event.target.closest('tr').remove();
                } else {
                    console.error('Error when deleting:', result.error);
                }
            } catch (error) {
                console.error('Error when deleting:', error);
            }
        }
    }
});
