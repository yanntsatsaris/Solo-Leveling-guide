// static/js/character_details.js

// Les données sont initialisées via initializePageData dans common.js
document.addEventListener("DOMContentLoaded", function () {
    // Initialise uniquement la modale spécifique à cette page
    initializeModal("edit-character-btn", "edit-character-overlay", "close-edit-character");
});
