function filterAnime() {
    let searchValue = document.getElementById("search-input").value.toLowerCase();
    let statusValue = document.getElementById("status-filter").value.toLowerCase();
    let rows = document.querySelectorAll("#anime-table-body tr");

    rows.forEach(row => {
        let title = row.cells[0].innerText.toLowerCase();
        let status = row.cells[3].innerText.toLowerCase();

        let matchesSearch = title.includes(searchValue);
        let matchesStatus = statusValue === "" || status.includes(statusValue);

        if (matchesSearch && matchesStatus) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

function resetFilters() {
    document.getElementById("search-input").value = "";
    document.getElementById("status-filter").value = "";
    filterAnime();
}

function deleteAnime(animeId) {


    fetch(`/delete_anime/${animeId}`, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let row = document.getElementById(`anime-row-${animeId}`);
            row.remove();

            // Sprawdzenie, czy tabela jest pusta
            let tableBody = document.getElementById("anime-table-body");
            if (tableBody.children.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="6">No anime found in your list.</td>
                    </tr>
                `;
            }
        } else {
            alert("Error deleting anime: " + data.error);
        }
    })
    .catch(error => console.error("Error:", error));
}