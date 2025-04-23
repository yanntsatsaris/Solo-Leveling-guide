// Gestion des onglets
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Ignorer le clic sur l'onglet avec la flèche (dropdown-tab)
        if (tab.id === 'dropdown-tab') {
            return;
        }

        // Retirer la classe active de tous les onglets
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(tc => tc.classList.remove('active'));

        // Ajouter la classe active à l'onglet cliqué et son contenu
        tab.classList.add('active');
        const targetTabContent = document.getElementById(tab.dataset.tab);
        if (targetTabContent) {
            targetTabContent.classList.add('active');
        }
    });
});

// Gestion des effets de panoplie
const activeSetEffects = JSON.parse(document.getElementById('activeSetEffectsData').textContent);

function showSetEffects(setName, event) {
    const effectsContainer = document.getElementById('set-effects');
    const effectsList = document.getElementById('set-effects-list');
    const effectsTitle = effectsContainer.querySelector('h3');

    // Vider la liste des effets
    effectsList.innerHTML = '';

    // Mettre à jour le titre avec le nom de la panoplie
    effectsTitle.textContent = setName;

    // Ajouter les effets activés pour la panoplie survolée
    activeSetEffects.forEach(effect => {
        if (effect.set_name === setName) {
            const listItem = document.createElement('li');
            // Remplacer les \n par des <br> pour gérer les sauts de ligne
            listItem.innerHTML = `${effect.pieces_required} pièces : ${effect.effect.replace(/\n/g, '<br>')}`;
            effectsList.appendChild(listItem);
        }
    });

    // Rendre la bulle visible temporairement pour calculer sa largeur
    effectsContainer.style.display = 'block';
    const bubbleWidth = effectsContainer.offsetWidth; // Largeur réelle de la bulle
    effectsContainer.style.display = 'none';

    // Positionner la bulle à gauche de l'image
    const rect = event.target.getBoundingClientRect();
    let leftPosition = rect.left - bubbleWidth - 10;

    // Si la bulle dépasse le bord gauche, la positionner à droite
    if (leftPosition < 0) {
        leftPosition = rect.right + 10;
    }

    effectsContainer.style.top = `${rect.top + window.scrollY}px`;
    effectsContainer.style.left = `${leftPosition}px`;

    // Afficher le conteneur des effets
    effectsContainer.style.display = 'block';
}

function hideSetEffects() {
    const effectsContainer = document.getElementById('set-effects');
    effectsContainer.style.display = 'none';
}

// Gestion de la mise à jour dynamique des artefacts, focus_stats et cores
document.addEventListener('DOMContentLoaded', () => {
    const artefactsTab = document.getElementById('artefacts-tab');
    const dropdownTab = document.getElementById('dropdown-tab');
    const dropdownArrow = document.getElementById('dropdown-arrow');
    const dropdownOptions = document.getElementById('dropdown-options');
    const focusStatsList = document.querySelector('.focus-stats-list');
    const artefactsContainer = document.querySelector('.artefacts-container');
    const coresContainer = document.querySelector('.cores-container');
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    // Récupérer les données des sets d'équipement depuis le script JSON
    const equipmentSets = JSON.parse(document.getElementById('equipmentSetsData').textContent);

    // Fonction pour afficher un set spécifique
    function displaySet(setIndex) {
        const selectedSet = equipmentSets[setIndex];

        // Mettre à jour les focus stats
        focusStatsList.innerHTML = selectedSet.focus_stats.map(stat => `<li>${stat}</li>`).join('');

        // Mettre à jour les artefacts
        const leftColumnArtefacts = selectedSet.artefacts.slice(0, 4).map(artefact => `
            <div class="artefact-item" data-set="${artefact.set}">
                <div class="artefact-item-content">
                    <img src="/static/${artefact.image}" alt="${artefact.name}" class="artefact-image"
                         onmouseover="showSetEffects('${artefact.set}', event)"
                         onmouseout="hideSetEffects()">
                    <div>
                        <div class="stat-main">
                            <div class="stat-container">
                                <span>${artefact.main_stat.name}</span>
                                <img src="/static/images/Stats_Principale.png" alt="Statistique Principale">
                            </div>
                        </div>
                        <div class="stat-secondary-container">
                            ${artefact.secondary_stats.map(stat => `
                                <div class="stat-secondary">
                                    <div class="stat-container">
                                        <span>${stat.name}</span>
                                        <img src="/static/images/Stats_Secondaire.png" alt="Statistique Secondaire">
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        const rightColumnArtefacts = selectedSet.artefacts.slice(4).map(artefact => `
            <div class="artefact-item" data-set="${artefact.set}">
                <div class="artefact-item-content">
                    <img src="/static/${artefact.image}" alt="${artefact.name}" class="artefact-image"
                         onmouseover="showSetEffects('${artefact.set}', event)"
                         onmouseout="hideSetEffects()">
                    <div>
                        <div class="stat-main">
                            <div class="stat-container">
                                <span>${artefact.main_stat.name}</span>
                                <img src="/static/images/Stats_Principale.png" alt="Statistique Principale">
                            </div>
                        </div>
                        <div class="stat-secondary-container">
                            ${artefact.secondary_stats.map(stat => `
                                <div class="stat-secondary">
                                    <div class="stat-container">
                                        <span>${stat.name}</span>
                                        <img src="/static/images/Stats_Secondaire.png" alt="Statistique Secondaire">
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        artefactsContainer.innerHTML = `
            <div class="artefacts-column">${leftColumnArtefacts}</div>
            <div class="artefacts-column">${rightColumnArtefacts}</div>
        `;

        // Mettre à jour les cores
        coresContainer.innerHTML = selectedSet.cores.map(core => `
            <div class="core-item">
                <img src="/static/${core.image}" alt="${core.name}" class="core-image">
                <div class="stats">
                    <div class="stat-main">
                        <div class="stat-container">
                            <span>${core.main_stat.name}</span>
                            <img src="/static/images/Stats_Principale.png" alt="Statistique Principale">
                        </div>
                    </div>
                    <div class="stat-secondary">
                        <div class="stat-container">
                            <span>${core.secondary_stat.name}</span>
                            <img src="/static/images/Stats_Secondaire.png" alt="Statistique Secondaire">
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Gérer le clic sur la flèche pour afficher/masquer les options
    dropdownArrow.addEventListener('click', (event) => {
        event.stopPropagation(); // Empêche la propagation du clic
        dropdownTab.classList.toggle('active');
    });

    // Gérer le clic sur une option
    dropdownOptions.addEventListener('click', (event) => {
        if (event.target.tagName === 'LI') {
            const setIndex = event.target.dataset.setIndex;

            // Afficher le set sélectionné
            displaySet(setIndex);

            // Activer l'onglet Artefacts
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));
            artefactsTab.classList.add('active');
            document.getElementById('artefacts').classList.add('active');

            // Fermer le menu déroulant
            dropdownTab.classList.remove('active');
        }
    });

    // Gérer le clic sur l'onglet Artefacts (affiche le premier set par défaut)
    artefactsTab.addEventListener('click', () => {
        displaySet(0);
    });

    // Afficher le premier set par défaut au chargement
    displaySet(0);
});