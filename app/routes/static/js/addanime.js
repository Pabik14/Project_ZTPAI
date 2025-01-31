document.getElementById("addAnimeForm").addEventListener("submit", function(event) {
    event.preventDefault();
    
    let formData = new FormData(this);
    
    fetch("{{ url_for('views.add_anime') }}", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
            window.location.href = "{{ url_for('views.anime_list') }}";
      
    })
    .catch(error => console.error("Error:", error));
});