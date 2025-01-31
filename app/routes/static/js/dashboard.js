document.addEventListener("DOMContentLoaded", function () {
    let statusData = {{ status_counts | tojson }};
    let typeData = {{ type_counts | tojson }};

    renderStatusChart(statusData);
    renderTypeChart(typeData);
});

function renderStatusChart(statusData) {
    const ctx = document.getElementById("animeStatusChart").getContext("2d");
    new Chart(ctx, {
        type: "pie",
        data: {
            labels: Object.keys(statusData),
            datasets: [{
                label: "Anime by Status",
                data: Object.values(statusData),
                backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff"]
            }]
        }
    });
}

function renderTypeChart(typeData) {
    const ctx = document.getElementById("animeTypeChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(typeData),
            datasets: [{
                label: "Anime by Type",
                data: Object.values(typeData),
                backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0"]
            }]
        }
    });
}