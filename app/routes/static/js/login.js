document
	.getElementById('loginForm')
	.addEventListener('submit', function (event) {
		event.preventDefault();
		let formData = new FormData(this);

		let loginUrl = document
			.getElementById('loginForm')
			.getAttribute('data-login-url');

		fetch(loginUrl, {
			method: 'POST',
			body: formData,
		}).then((response) => {
			if (response.redirected) {
				window.location.href = response.url; 
			} else {
				response.text().then((text) => {
					document.getElementById('error-message').innerHTML = text;
				});
			}
		});
	});
