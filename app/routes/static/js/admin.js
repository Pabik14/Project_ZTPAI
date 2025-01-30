document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-user").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();

            let row = this.closest("tr");
            let userId = row.dataset.userId;

            fetch(`/admin/delete_user/${userId}`, {
                method: "DELETE"
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    row.remove();
                } else {
                    alert("Error deleting user: " + data.error);
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });
});
