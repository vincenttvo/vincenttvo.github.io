// Get the toggle button and the body element
const toggleButton = document.getElementById('dark-mode-toggle');
const body = document.body;

// Function to toggle dark mode
toggleButton.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    body.classList.toggle('light-mode');

    // Save the user's preference to local storage
    if (body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
});

// Check the user's preference on page load
const currentTheme = localStorage.getItem('theme');
if (currentTheme) {
    body.classList.add(currentTheme);
} else {
    body.classList.add('light-mode'); // Default to light mode
}
