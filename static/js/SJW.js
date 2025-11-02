// static/js/SJW.js

// Les données sont initialisées via initializePageData dans common.js
document.addEventListener("DOMContentLoaded", function () {
    // Initialise uniquement la modale spécifique à cette page
    initializeModal("edit-sjw-btn", "edit-sjw-overlay", "close-edit-sjw");
});
