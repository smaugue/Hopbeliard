let logoutButton = document.getElementById('logoutButton');

logoutButton.onclick = function() {
    window.location.href = "/api/logout";
};