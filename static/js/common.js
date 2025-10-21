document.addEventListener("DOMContentLoaded", () => {
    handleTabs();
    handleEquipmentSets();
});

function handleTabs() {
    const tabs = document.querySelectorAll(".tab");
    const tabContents = document.querySelectorAll(".tab-content");

    const urlParams = new URLSearchParams(window.location.search);
    const activeTab = urlParams.get("tab");

    if (activeTab) {
        tabs.forEach((tab) => tab.classList.remove("active"));
        tabContents.forEach((content) => content.classList.remove("active"));
        const targetTab = document.querySelector(`.tab[data-tab="${activeTab}"]`);
        const targetContent = document.getElementById(activeTab);
        if (targetTab && targetContent) {
            targetTab.classList.add("active");
            targetContent.classList.add("active");
        }
    } else {
        const defaultTab = document.querySelector('.tab[data-tab="description"]') || document.querySelector('.tab[data-tab="review"]');
        if (defaultTab) {
            const defaultContent = document.getElementById(defaultTab.dataset.tab);
            if (defaultContent) {
                defaultTab.classList.add("active");
                defaultContent.classList.add("active");
            }
        }
    }

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            if (tab.id === "dropdown-tab") return;
            tabs.forEach((t) => t.classList.remove("active"));
            tabContents.forEach((tc) => tc.classList.remove("active"));
            tab.classList.add("active");
            const targetTabContent = document.getElementById(tab.dataset.tab);
            if (targetTabContent) {
                targetTabContent.classList.add("active");
            }
        });
    });
}

function handleEquipmentSets() {
    const equipmentSetsData = document.getElementById("equipmentSetsData");
    if (!equipmentSetsData) return;

    const equipmentSets = JSON.parse(equipmentSetsData.textContent);
    const equipmentSetsEffects = JSON.parse(document.getElementById("equipmentSetsEffectsData").textContent);
    const coresEffects = JSON.parse(document.getElementById("coresEffectsData").textContent);

    const focusStatsList = document.querySelector(".focus-stats-list");
    const artefactsContainer = document.querySelector(".artefacts-container");
    const coresContainer = document.querySelector(".cores-container");
    const descriptionText = document.querySelector(".equipment-set-description-text");
    const equipmentSelect = document.getElementById("equipment-select");
    const artefactsTab = document.getElementById("artefacts-tab");
    let currentSetIndex = 0;

    function displaySet(setIndex) {
        const selectedSet = equipmentSets[setIndex];
        if (!selectedSet) {
            if (descriptionText) descriptionText.innerHTML = "";
            if (focusStatsList) focusStatsList.innerHTML = "";
            if (artefactsContainer) artefactsContainer.innerHTML = "";
            if (coresContainer) coresContainer.innerHTML = "";
            return;
        }

        if (descriptionText) descriptionText.innerHTML = selectedSet.description ? selectedSet.description : "";
        if (focusStatsList) focusStatsList.innerHTML = selectedSet.focus_stats.map((stat) => `<li>${stat}</li>`).join("");

        if (artefactsContainer) {
            const leftColumnArtefacts = selectedSet.artefacts.slice(0, 4).map(createArtefactHTML).join("");
            const rightColumnArtefacts = selectedSet.artefacts.slice(4).map(createArtefactHTML).join("");
            artefactsContainer.innerHTML = `<div class="artefacts-column">${leftColumnArtefacts}</div><div class="artefacts-column">${rightColumnArtefacts}</div>`;
        }

        if (coresContainer) coresContainer.innerHTML = selectedSet.cores.map(createCoreHTML).join("");
    }

    function createArtefactHTML(artefact) {
        return `
            <div class="artefact-item" data-set="${artefact.set}">
                <div class="artefact-item-content">
                    <img src="/static/${artefact.image}" alt="${artefact.name}" class="artefact-image" onmouseover="showSetEffects('${artefact.set}', event)" onmouseout="hideSetEffects()">
                    <div>
                        <div class="stat-main"><div class="stat-container"><span>${artefact.main_stat}</span><img src="/static/images/Stats_Principale.png" alt="Statistique Principale"></div></div>
                        <div class="stat-secondary-container">${artefact.secondary_stats.map(createStatHTML).join("")}</div>
                    </div>
                </div>
            </div>`;
    }

    function createStatHTML(stat) {
        return `<div class="stat-secondary"><div class="stat-container"><span>${stat}</span><img src="/static/images/Stats_Secondaire.png" alt="Statistique Secondaire"></div></div>`;
    }

    function createCoreHTML(core) {
        return `
            <div class="core-item">
                <img src="/static/${core.image}" alt="${core.name}" class="core-image" onmouseover="showCoreEffect('${core.color}', '${core.number}', event)" onmouseout="hideCoreEffect()">
                <div class="stats">
                    <div class="stat-main"><div class="stat-container"><span>${core.main_stat}</span><img src="/static/images/Stats_Principale.png" alt="Statistique Principale"></div></div>
                    <div class="stat-secondary"><div class="stat-container"><span>${core.secondary_stat}</span><img src="/static/images/Stats_Secondaire.png" alt="Statistique Secondaire"></div></div>
                </div>
            </div>`;
    }

    if (equipmentSelect) {
        equipmentSelect.addEventListener("click", (event) => {
            event.stopPropagation();
            if (equipmentSelect.value === currentSetIndex) {
                document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
                document.querySelectorAll(".tab-content").forEach((tc) => tc.classList.remove("active"));
                if(artefactsTab) artefactsTab.classList.add("active");
                const artefactsContent = document.getElementById("artefacts");
                if (artefactsContent) artefactsContent.classList.add("active");
            }
        });

        equipmentSelect.addEventListener("change", (event) => {
            currentSetIndex = event.target.value;
            displaySet(currentSetIndex);
            document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach((tc) => tc.classList.remove("active"));
            if(artefactsTab) artefactsTab.classList.add("active");
            const artefactsContent = document.getElementById("artefacts");
            if(artefactsContent) artefactsContent.classList.add("active");
        });

        if (equipmentSelect.options.length > 0 && equipmentSets.length > 0) {
            currentSetIndex = equipmentSelect.options[0].value;
            displaySet(currentSetIndex);
        }
    }
}
function showSetEffects(setName, event) {
    const effectsContainer = document.getElementById("set-effects");
    const effectsList = document.getElementById("set-effects-list");
    const effectsTitle = effectsContainer.querySelector("h3");
    const equipmentSelect = document.getElementById("equipment-select");
    const equipmentSets = JSON.parse(document.getElementById("equipmentSetsData").textContent);
    const equipmentSetsEffects = JSON.parse(document.getElementById("equipmentSetsEffectsData").textContent);

    let displayName = setName;
    const effectSet = equipmentSetsEffects.find((e) => e.set_name === setName);
    if (effectSet && effectSet.display_name) {
        displayName = effectSet.display_name;
    }
    effectsTitle.textContent = displayName;

    const selectedSetIndex = equipmentSelect ? parseInt(equipmentSelect.value) : 0;
    const selectedSet = equipmentSets[selectedSetIndex];
    const numPieces = (selectedSet.set_piece_count && selectedSet.set_piece_count[setName]) ? selectedSet.set_piece_count[setName] : 0;
    const effects = equipmentSetsEffects.filter((e) => e.set_name === setName && e.pieces_required <= numPieces).sort((a, b) => a.pieces_required - b.pieces_required);

    effectsList.innerHTML = "";
    if (effects.length === 0) {
        effectsList.innerHTML = "<li>Aucun effet disponible pour ce nombre de pièces.</li>";
    } else {
        effects.forEach((effect) => {
            const listItem = document.createElement("li");
            listItem.innerHTML = `<span style="color: #ffcc00; font-weight: bold;">${effect.pieces_required} pièces :</span><span style="display: block; margin-top: 5px;">${effect.effect.replace(/\n/g, "<br>")}</span>`;
            effectsList.appendChild(listItem);
        });
    }

    positionBubble(effectsContainer, event.target);
}

function hideSetEffects() {
    document.getElementById("set-effects").style.display = "none";
}

function showCoreEffect(color, number, event) {
    const bubble = document.getElementById("core-effect-bubble");
    const title = document.getElementById("core-effect-title");
    const desc = document.getElementById("core-effect-description");
    const coresEffects = JSON.parse(document.getElementById("coresEffectsData").textContent);

    const effect = coresEffects.find((e) => e.color === color && e.number === number);
    if (effect) {
        title.textContent = effect.name;
        desc.innerHTML = effect.effect.replace(/\n/g, "<br>");
    } else {
        title.textContent = "Effet inconnu";
        desc.textContent = "";
    }

    positionBubble(bubble, event.target);
}

function hideCoreEffect() {
    document.getElementById("core-effect-bubble").style.display = "none";
}

function positionBubble(bubble, target) {
    bubble.style.display = "block";
    const rect = target.getBoundingClientRect();
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
