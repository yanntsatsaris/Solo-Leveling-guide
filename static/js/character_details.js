// Gestion des onglets
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Retirer la classe active de tous les onglets
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(tc => tc.classList.remove('active'));

        // Ajouter la classe active à l'onglet cliqué et son contenu
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
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