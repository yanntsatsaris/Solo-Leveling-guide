// Gestion des onglets
document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".tab");
  const tabContents = document.querySelectorAll(".tab-content");

  // Vérifier si un paramètre "tab" est présent dans l'URL
  const urlParams = new URLSearchParams(window.location.search);
  const activeTab = urlParams.get("tab");

  if (activeTab) {
    // Désactiver tous les onglets et contenus
    tabs.forEach((tab) => tab.classList.remove("active"));
    tabContents.forEach((content) => content.classList.remove("active"));

    // Activer l'onglet et le contenu correspondant
    const targetTab = document.querySelector(`.tab[data-tab="${activeTab}"]`);
    const targetContent = document.getElementById(activeTab);
    if (targetTab && targetContent) {
      targetTab.classList.add("active");
      targetContent.classList.add("active");
    }
  } else {
    // Activer l'onglet par défaut (Description)
    const defaultTab = document.querySelector('.tab[data-tab="description"]');
    const defaultContent = document.getElementById("description");
    if (defaultTab && defaultContent) {
      defaultTab.classList.add("active");
      defaultContent.classList.add("active");
    }
  }

  // Gestion du clic sur les onglets
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      // Ignorer le clic sur l'onglet avec la flèche (dropdown-tab)
      if (tab.id === "dropdown-tab") {
        return;
      }

      // Retirer la classe active de tous les onglets et contenus
      tabs.forEach((t) => t.classList.remove("active"));
      tabContents.forEach((tc) => tc.classList.remove("active"));

      // Ajouter la classe active à l'onglet cliqué et son contenu
      tab.classList.add("active");
      const targetTabContent = document.getElementById(tab.dataset.tab);
      if (targetTabContent) {
        targetTabContent.classList.add("active");
      }
    });
  });
});

// Gestion des effets de panoplie
const equipmentSetsEffects = JSON.parse(
  document.getElementById("equipmentSetsEffectsData").textContent
);

function showSetEffects(setName, event) {
  const effectsContainer = document.getElementById("set-effects");
  const effectsList = document.getElementById("set-effects-list");
  const effectsTitle = effectsContainer.querySelector("h3");

  // Vider la liste des effets
  effectsList.innerHTML = "";

  // Mettre à jour le titre avec le nom de la panoplie
  effectsTitle.textContent = setName;

  // Récupérer les effets activés pour le set actuellement sélectionné
  const selectedSetEffects = equipmentSetsEffects[currentSetIndex];

  // Ajouter les effets activés pour la panoplie survolée
  selectedSetEffects.forEach((effect) => {
    if (effect.set_name === setName) {
      const listItem = document.createElement("li");
      listItem.innerHTML = `
        <span style="color: #ffcc00; font-weight: bold;">${
          effect.pieces_required
        } pièces :</span>
        <span style="display: block; margin-top: 5px;">${effect.effect.replace(
          /\n/g,
          "<br>"
        )}</span>
      `;
      effectsList.appendChild(listItem);
    }
  });

  // Rendre la bulle visible temporairement pour calculer ses dimensions
  effectsContainer.style.display = "block";
  const bubbleWidth = effectsContainer.offsetWidth;
  const bubbleHeight = effectsContainer.offsetHeight;
  effectsContainer.style.display = "none";

  // Positionner la bulle
  const rect = event.target.getBoundingClientRect();
  let leftPosition = rect.left - bubbleWidth - 10;
  if (leftPosition < 0) {
    leftPosition = rect.right + 10;
  }
  let topPosition = rect.top + window.scrollY;
  const viewportHeight = window.innerHeight;
  if (topPosition + bubbleHeight > viewportHeight + window.scrollY) {
    topPosition = viewportHeight + window.scrollY - bubbleHeight - 10;
  }

  effectsContainer.style.top = `${topPosition}px`;
  effectsContainer.style.left = `${leftPosition}px`;
  effectsContainer.style.display = "block";
}

function hideSetEffects() {
  const effectsContainer = document.getElementById("set-effects");
  effectsContainer.style.display = "none";
}

// Gestion de la mise à jour dynamique des artefacts, focus_stats et cores
document.addEventListener("DOMContentLoaded", () => {
  const focusStatsList = document.querySelector(".focus-stats-list");
  const artefactsContainer = document.querySelector(".artefacts-container");
  const coresContainer = document.querySelector(".cores-container");
  const equipmentSets = JSON.parse(
    document.getElementById("equipmentSetsData").textContent
  );

  function displaySet(setIndex) {
    const selectedSet = equipmentSets[setIndex];

    // Mettre à jour les focus stats
    focusStatsList.innerHTML = selectedSet.focus_stats
      .map((stat) => `<li>${stat}</li>`)
      .join("");

    // Mettre à jour les artefacts
    const leftColumnArtefacts = selectedSet.artefacts
      .slice(0, 4)
      .map(
        (artefact) => `
            <div class="artefact-item" data-set="${artefact.set}">
                <div class="artefact-item-content">
                    <img src="/static/${artefact.image}" alt="${artefact.name}" class="artefact-image"
                         onmouseover="showSetEffects('${artefact.set}', event)"
                         onmouseout="hideSetEffects()">
                    <div>
                        <div class="stat-main">
                            <div class="stat-container">
                                <span>${artefact.main_stat}</span>
                                <img src="/static/images/Stats_Principale.png" alt="Statistique Principale">
                            </div>
                        </div>
                        <div class="stat-secondary-container">
                            ${artefact.secondary_stats
                              .map(
                                (stat) => `
                                <div class="stat-secondary">
                                    <div class="stat-container">
                                        <span>${stat}</span>
                                        <img src="/static/images/Stats_Secondaire.png" alt="Statistique Secondaire">
                                    </div>
                                </div>
                            `
                              )
                              .join("")}
                        </div>
                    </div>
                </div>
            </div>
        `
      )
      .join("");

    const rightColumnArtefacts = selectedSet.artefacts
      .slice(4)
      .map(
        (artefact) => `
            <div class="artefact-item" data-set="${artefact.set}">
                <div class="artefact-item-content">
                    <img src="/static/${artefact.image}" alt="${artefact.name}" class="artefact-image"
                         onmouseover="showSetEffects('${artefact.set}', event)"
                         onmouseout="hideSetEffects()">
                    <div>
                        <div class="stat-main">
                            <div class="stat-container">
                                <span>${artefact.main_stat}</span>
                                <img src="/static/images/Stats_Principale.png" alt="Statistique Principale">
                            </div>
                        </div>
                        <div class="stat-secondary-container">
                            ${artefact.secondary_stats
                              .map(
                                (stat) => `
                                <div class="stat-secondary">
                                    <div class="stat-container">
                                        <span>${stat}</span>
                                        <img src="/static/images/Stats_Secondaire.png" alt="Statistique Secondaire">
                                    </div>
                                </div>
                            `
                              )
                              .join("")}
                        </div>
                    </div>
                </div>
            </div>
        `
      )
      .join("");

    artefactsContainer.innerHTML = `
            <div class="artefacts-column">${leftColumnArtefacts}</div>
            <div class="artefacts-column">${rightColumnArtefacts}</div>
        `;

    // Mettre à jour les cores
    coresContainer.innerHTML = selectedSet.cores
      .map(
        (core) => `
            <div class="core-item">
                <img src="/static/${core.image}" alt="${core.name}" class="core-image">
                <div class="stats">
                    <div class="stat-main">
                        <div class="stat-container">
                            <span>${core.main_stat}</span>
                            <img src="/static/images/Stats_Principale.png" alt="Statistique Principale">
                        </div>
                    </div>
                    <div class="stat-secondary">
                        <div class="stat-container">
                            <span>${core.secondary_stat}</span>
                            <img src="/static/images/Stats_Secondaire.png" alt="Statistique Secondaire">
                        </div>
                    </div>
                </div>
            </div>
        `
      )
      .join("");
  }

  // Gestion du changement de sélection dans le <select>
  const equipmentSelect = document.getElementById("equipment-select");
  const artefactsTab = document.getElementById("artefacts-tab");

  // Gestion du clic sur le <select>
  equipmentSelect.addEventListener("click", (event) => {
    event.stopPropagation(); // Empêche le clic de se propager comme un onglet
    const setIndex = equipmentSelect.value;

    // Si le set sélectionné est déjà affiché, activer l'onglet Artefacts
    if (setIndex === currentSetIndex) {
      tabs.forEach((t) => t.classList.remove("active"));
      tabContents.forEach((tc) => tc.classList.remove("active"));
      const artefactsTab = document.getElementById("artefacts-tab");
      artefactsTab.classList.add("active");
      document.getElementById("artefacts").classList.add("active");
    }
  });

  // Gestion du changement de sélection
  equipmentSelect.addEventListener("change", (event) => {
    const setIndex = event.target.value;

    // Mettre à jour le set sélectionné
    currentSetIndex = setIndex;

    // Afficher le set sélectionné
    displaySet(setIndex);

    // Activer l'onglet Artefacts
    tabs.forEach((t) => t.classList.remove("active"));
    tabContents.forEach((tc) => tc.classList.remove("active"));
    const artefactsTab = document.getElementById("artefacts-tab");
    artefactsTab.classList.add("active");
    document.getElementById("artefacts").classList.add("active");
  });

  // Afficher le premier set par défaut au chargement
  if (equipmentSelect.options.length > 0) {
    currentSetIndex = equipmentSelect.options[0].value; // Initialiser avec le premier set
    displaySet(currentSetIndex);
  }
});
