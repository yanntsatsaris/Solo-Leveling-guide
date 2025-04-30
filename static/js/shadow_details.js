// Gestion des onglets
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", function () {
    // Supprime la classe active de tous les onglets et contenus
    document
      .querySelectorAll(".tab, .tab-content")
      .forEach((el) => el.classList.remove("active"));

    // Ajoute la classe active à l'onglet et au contenu sélectionnés
    this.classList.add("active");
    document
      .getElementById(this.getAttribute("data-tab"))
      .classList.add("active");
  });
});
