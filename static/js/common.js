// static/js/common.js

// Les données peuvent être pour SJW ou un autre personnage
let pageData = {
    equipmentSets: [],
    panopliesEffects: [],
    coresEffects: []
};

// Fonction générique pour initialiser les données de la page
function initializePageData(data) {
    Object.assign(pageData, data);
}
// Alias pour la rétrocompatibilité
const initializeSJWData = initializePageData;
const initializeCharacterData = initializePageData;


document.addEventListener("DOMContentLoaded", function () {
    // Initialiser les fonctionnalités communes à toutes les pages
    setupTabs();

    // N'afficher un set que si des données sont disponibles
    if (pageData.equipmentSets && pageData.equipmentSets.length > 0) {
        setupEquipmentSetDisplay();
    }
});

function setupTabs() {
    const tabs = document.querySelectorAll(".tab");
    if (tabs.length === 0) return;

    tabs.forEach(tab => {
        tab.addEventListener("click", function () {
            if (this.id === 'dropdown-tab') return;

            tabs.forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.style.display = "none");

            this.classList.add("active");
            const tabName = this.dataset.tab;
            const content = document.getElementById(tabName);
            if (content) {
                content.style.display = "block";
            }
        });
    });

    const equipmentSelect = document.getElementById('equipment-select');
    if (equipmentSelect) {
        equipmentSelect.addEventListener('change', function() {
            displayEquipmentSet(this.value);
        });
    }
}

function setupEquipmentSetDisplay() {
    // Afficher le premier set par défaut
    displayEquipmentSet(0);
}

function displayEquipmentSet(setIndex) {
    const set = pageData.equipmentSets[setIndex];
    if (!set) return;

    // Mise à jour de la description et des stats focus
    const descContainer = document.querySelector('.equipment-set-description-text');
    const focusContainer = document.querySelector('.focus-stats-list');
    if (descContainer) descContainer.innerHTML = set.description || 'Aucune description.';
    if (focusContainer) {
        focusContainer.innerHTML = set.focus_stats && set.focus_stats.length > 0 ?
            set.focus_stats.map(stat => `<li>${stat}</li>`).join('') :
            '<li>Aucune stat à focus.</li>';
    }

    // Mise à jour des artefacts et des noyaux
    updateArtefactsDisplay(set.artefacts);
    updateCoresDisplay(set.cores);
}

function updateArtefactsDisplay(artefacts) {
    const container = document.querySelector('.artefacts-container');
    if (!container) return;

    container.innerHTML = '';
    if (artefacts && artefacts.length > 0) {
        const col1 = document.createElement('div');
        col1.className = 'artefacts-column';
        const col2 = document.createElement('div');
        col2.className = 'artefacts-column';

        artefacts.forEach((artefact, i) => {
            const item = createArtefactItem(artefact);
            if (i < 4) col1.appendChild(item);
            else col2.appendChild(item);
        });
        container.appendChild(col1);
        container.appendChild(col2);
    } else {
        container.innerHTML = '<p>Aucun artefact pour ce set.</p>';
    }
}

function updateCoresDisplay(cores) {
    const container = document.querySelector('.cores-container');
    if (!container) return;

    container.innerHTML = '';
    if (cores && cores.length > 0) {
        cores.forEach(core => {
            container.appendChild(createCoreItem(core));
        });
    } else {
        container.innerHTML = '<p>Aucun noyau pour ce set.</p>';
    }
}

function createArtefactItem(artefact) {
    const item = document.createElement('div');
    item.className = 'artefact-item';
    item.dataset.set = artefact.set;

    const secondaryStats = (artefact.secondary_stats || []).map(stat => `
        <div class="stat-secondary">
            <div class="stat-container">
                <span>${stat}</span>
                <img src="/static/images/Stats_Secondaire.png" alt="Statistique Secondaire" />
            </div>
        </div>`).join('');

    item.innerHTML = `
        <div class="artefact-item-content">
            <img src="${artefact.image}" alt="${artefact.name}" class="artefact-image" />
            <div>
                <div class="stat-main">
                    <div class="stat-container">
                        <span>${artefact.main_stat}</span>
                        <img src="/static/images/Stats_Principale.png" alt="Statistique Principale" />
                    </div>
                </div>
                <div class="stat-secondary-container">${secondaryStats}</div>
            </div>
        </div>`;

    const img = item.querySelector('.artefact-image');
    img.addEventListener('mouseover', e => showSetEffects(artefact.set, e));
    img.addEventListener('mouseout', hideSetEffects);
    return item;
}

function createCoreItem(core) {
    const item = document.createElement('div');
    item.className = 'core-item';
    item.innerHTML = `
        <img src="${core.image}" alt="${core.name}" class="core-image" />
        <div class="stats">
            <div class="stat-main">
                <div class="stat-container">
                    <span>${core.main_stat}</span>
                    <img src="/static/images/Stats_Principale.png" alt="Statistique Principale" />
                </div>
            </div>
            <div class="stat-secondary">
                <div class="stat-container">
                    <span>${core.secondary_stat}</span>
                    <img src="/static/images/Stats_Secondaire.png" alt="Statistique Secondaire" />
                </div>
            </div>
        </div>`;

    const img = item.querySelector('.core-image');
    img.addEventListener('mouseover', e => showCoreEffect(core.color, core.number, e));
    img.addEventListener('mouseout', hideCoreEffect);
    return item;
}

// Fonctions pour les tooltips
function showSetEffects(setName, event) {
    const effects = pageData.panopliesEffects.filter(e => e.set_name === setName);
    if (effects.length === 0) return;

    const tooltip = document.getElementById('set-effects');
    tooltip.querySelector('h3').textContent = setName;
    const list = tooltip.querySelector('#set-effects-list');
    list.innerHTML = effects.map(e => `<li><strong>(${e.pieces} pieces):</strong> ${e.effect}</li>`).join('');

    tooltip.style.display = 'block';
    moveTooltip(tooltip, event);
}

function hideSetEffects() {
    document.getElementById('set-effects').style.display = 'none';
}

function showCoreEffect(color, number, event) {
    const effect = pageData.coresEffects.find(e => e.color === color && e.number === parseInt(number, 10));
    if (!effect) return;

    const tooltip = document.getElementById('core-effect-bubble');
    tooltip.querySelector('#core-effect-title').textContent = effect.effect_name;
    tooltip.querySelector('#core-effect-description').innerHTML = effect.effect;

    tooltip.style.display = 'block';
    moveTooltip(tooltip, event);
}

function hideCoreEffect() {
    document.getElementById('core-effect-bubble').style.display = 'none';
}

function moveTooltip(tooltip, event) {
    tooltip.style.left = `${event.pageX + 15}px`;
    tooltip.style.top = `${event.pageY + 15}px`;
}

// Lazy Loading pour les images
document.addEventListener("DOMContentLoaded", function() {
    const lazyImages = [].slice.call(document.querySelectorAll("img.lazy"));

    if ("IntersectionObserver" in window) {
        let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    let lazyImage = entry.target;
                    lazyImage.src = lazyImage.dataset.src;
                    lazyImage.classList.remove("lazy");
                    lazyImageObserver.unobserve(lazyImage);
                }
            });
        });

        lazyImages.forEach(function(lazyImage) {
            lazyImageObserver.observe(lazyImage);
        });
    } else {
        // Fallback pour les anciens navigateurs
        lazyImages.forEach(function(lazyImage) {
            lazyImage.src = lazyImage.dataset.src;
        });
    }
});
