function showAlert() {
    alert("Hello! Flask is serving JavaScript!");
}

document
	.getElementById('registerForm')
	.addEventListener('submit', function (event) {
		event.preventDefault();
		let formData = new FormData(this);

		fetch("{{ url_for('auth.register') }}", {
			method: 'POST',
			body: formData,
		})
			.then((response) => response.json())
			.then((data) => {
				if (data.error) {
					document.getElementById('error-message').innerText = data.error;
				} else {
					window.location.href = "{{ url_for('auth.login') }}";
				}
			});
	});
