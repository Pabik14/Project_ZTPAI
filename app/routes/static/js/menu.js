document.addEventListener('DOMContentLoaded', () => {
    const burgerMenu = document.getElementById('burger-menu');
    const navLinks = document.getElementById('nav-links');

    // Dodanie event listenera do burger menu
    burgerMenu.addEventListener('click', () => {
        navLinks.classList.toggle('show');
    });
});
