// Ces deux lignes doivent être tout en haut du fichier, AVANT toute fonction
const equipmentSets = JSON.parse(
  document.getElementById("equipmentSetsData").textContent
);
const equipmentSetsEffects = JSON.parse(
  document.getElementById("equipmentSetsEffectsData").textContent
);

// Les effets de core sont passés depuis Flask
const coresEffects = JSON.parse(document.getElementById("coresEffectsData").textContent);

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
function showSetEffects(setName, event) {
  const effectsContainer = document.getElementById("set-effects");
  const effectsList = document.getElementById("set-effects-list");
  const effectsTitle = effectsContainer.querySelector("h3");

  effectsList.innerHTML = "";

  // Récupère le display_name correspondant au set
  let displayName = setName;
  const effectSet = equipmentSetsEffects.find(e => e.set_name === setName);
  if (effectSet && effectSet.display_name) {
    displayName = effectSet.display_name;
  } else {
    // Si non trouvé, tente dans equipmentSets
    const selectedSet = equipmentSets.find(s => s.name === setName);
    if (selectedSet && selectedSet.display_name) {
      displayName = selectedSet.display_name;
    }
  }
  effectsTitle.textContent = displayName;

  // Récupère le set actuellement sélectionné
  const equipmentSelect = document.getElementById("equipment-select");
  const selectedSetIndex = equipmentSelect ? parseInt(equipmentSelect.value) : 0;
  const selectedSet = equipmentSets[selectedSetIndex];

  // Récupère le nombre de pièces pour le set survolé
  const numPieces = selectedSet.set_piece_count && selectedSet.set_piece_count[setName]
    ? selectedSet.set_piece_count[setName]
    : 0;

  // Filtre les effets pour le set affiché et le nombre de pièces
  const effects = equipmentSetsEffects.filter(
    (e) => e.set_name === setName && e.pieces_required <= numPieces
  );

  effectsContainer.style.display = "block";
  effectsList.innerHTML = "";
  if (effects.length === 0) {
    effectsList.innerHTML = "<li>Aucun effet disponible pour ce nombre de pièces.</li>";
  } else {
    effects.forEach((effect) => {
      const listItem = document.createElement("li");
      listItem.innerHTML = `
        <span style="color: #ffcc00; font-weight: bold;">${effect.pieces_required} pièces :</span>
        <span style="display: block; margin-top: 5px;">${effect.effect.replace(/\n/g, "<br>")}</span>
      `;
      effectsList.appendChild(listItem);
    });
  }

  // Positionner la bulle à gauche de l'image
  const rect = event.target.getBoundingClientRect();
  const bubbleWidth = effectsContainer.offsetWidth || 300;
  const bubbleHeight = effectsContainer.offsetHeight || 100;

  let leftPosition = rect.left + window.scrollX - bubbleWidth - 10;
  if (leftPosition < 0) {
    leftPosition = rect.right + window.scrollX + 10;
  }
  let topPosition = rect.top + window.scrollY;

  if (topPosition + bubbleHeight > window.innerHeight + window.scrollY) {
    topPosition = window.innerHeight + window.scrollY - bubbleHeight - 10;
  }

  effectsContainer.style.top = `${topPosition}px`;
  effectsContainer.style.left = `${leftPosition}px`;
  effectsContainer.style.display = "block";
}

function hideSetEffects() {
  const effectsContainer = document.getElementById("set-effects");
  effectsContainer.style.display = "none";
}

// Affichage de la bulle d'effet pour un core
function showCoreEffect(color, number, event) {
  const bubble = document.getElementById("core-effect-bubble");
  const title = document.getElementById("core-effect-title");
  const desc = document.getElementById("core-effect-description");

  const effect = coresEffects.find(
    (e) => e.color === color && e.number === number
  );

  if (effect) {
    title.textContent = effect.name;
    desc.innerHTML = effect.effect.replace(/\n/g, "<br>");
  } else {
    title.textContent = "Effet inconnu";
    desc.textContent = "";
  }

  bubble.style.display = "block";

  // Positionne la bulle à gauche de l'image
  const rect = event.target.getBoundingClientRect();
  const bubbleWidth = bubble.offsetWidth || 300;
  const bubbleHeight = bubble.offsetHeight || 100;

  let leftPosition = rect.left + window.scrollX - bubbleWidth - 10;
  if (leftPosition < 0) {
    leftPosition = rect.right + window.scrollX + 10;
  }
  let topPosition = rect.top + window.scrollY;

  if (topPosition + bubbleHeight > window.innerHeight + window.scrollY) {
    topPosition = window.innerHeight + window.scrollY - bubbleHeight - 10;
  }

  bubble.style.top = `${topPosition}px`;
  bubble.style.left = `${leftPosition}px`;
}

function hideCoreEffect() {
  document.getElementById("core-effect-bubble").style.display = "none";
}

// Gestion de la mise à jour dynamique des artefacts, focus_stats et cores
document.addEventListener("DOMContentLoaded", () => {
  // Toutes les variables ici sont accessibles partout dans ce bloc !
  const tabs = document.querySelectorAll(".tab");
  const tabContents = document.querySelectorAll(".tab-content");
  let currentSetIndex = 0;

  // Gestion des onglets
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

  // Gestion de la mise à jour dynamique des artefacts, focus_stats et cores
  const focusStatsList = document.querySelector(".focus-stats-list");
  const artefactsContainer = document.querySelector(".artefacts-container");
  const coresContainer = document.querySelector(".cores-container");
  const descriptionText = document.querySelector(".equipment-set-description-text");

  function displaySet(setIndex) {
    const selectedSet = equipmentSets[setIndex];
    descriptionText.innerHTML = selectedSet.description ? selectedSet.description : "";

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
        <img src="/static/${core.image}" alt="${core.name}" class="core-image"
             onmouseover="showCoreEffect('${core.color}', '${core.number}', event)"
             onmouseout="hideCoreEffect()">
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
  equipmentSelect.addEventListener("click", function(event) {
    event.stopPropagation(); // Empêche le clic de se propager comme un onglet
    const setIndex = equipmentSelect.value;

    // Si le set sélectionné est déjà affiché, activer l'onglet Artefacts
    if (setIndex === currentSetIndex) {
      tabs.forEach((t) => t.classList.remove("active"));
      tabContents.forEach((tc) => tc.classList.remove("active"));
      artefactsTab.classList.add("active");
      document.getElementById("artefacts").classList.add("active");
    }
  });

  // Gestion du changement de sélection
  equipmentSelect.addEventListener("change", (event) => {
    const setIndex = event.target.value;
    currentSetIndex = setIndex;
    displaySet(setIndex);
    tabs.forEach((t) => t.classList.remove("active"));
    tabContents.forEach((tc) => tc.classList.remove("active"));
    artefactsTab.classList.add("active");
    document.getElementById("artefacts").classList.add("active");
  });

  // Afficher le premier set par défaut au chargement
  if (equipmentSelect.options.length > 0) {
    currentSetIndex = equipmentSelect.options[0].value; // Initialiser avec le premier set
    displaySet(currentSetIndex);
  }
});

document.addEventListener("DOMContentLoaded", function() {
  const editBtn = document.getElementById('edit-character-btn');
  const overlay = document.getElementById('edit-character-overlay');
  const closeBtn = document.getElementById('close-edit-character');

  if (editBtn && overlay) {
    editBtn.onclick = function() {
      overlay.style.display = 'flex';
    };
  }
  if (closeBtn && overlay) {
    closeBtn.onclick = function() {
      overlay.style.display = 'none';
    };
  }
});
