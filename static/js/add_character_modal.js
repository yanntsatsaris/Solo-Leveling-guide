// static/js/add_character_modal.js

// Les données passées depuis le template
const modalData = {
    panopliesList: [],
    artefactMainStats: {},
    secondaryStatsOptions: [],
    focusStatsOptions: [],
    coresList: [],
    coreMainStats: {},
    coreSecondaryStats: {},
    artefactTypeLabels: {
        "FR-fr": ["Casque", "Plastron", "Gants", "Bottes", "Collier", "Bracelet", "Bague", "Boucle d'oreille"],
        "EN-en": ["Helmet", "Chestplate", "Gloves", "Boots", "Necklace", "Bracelet", "Ring", "Earring"]
    },
    currentLang: 'FR-fr'
};

function initializeModalData(data) {
    Object.assign(modalData, data);
}

document.addEventListener('DOMContentLoaded', function() {
    const addCharacterDialog = document.getElementById('add-character-dialog');

    // Gestion des onglets
    addCharacterDialog.querySelectorAll('.edit-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            addCharacterDialog.querySelectorAll('.edit-tab').forEach(t => t.classList.remove('active'));
            addCharacterDialog.querySelectorAll('.edit-tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            addCharacterDialog.querySelector('#edit-tab-' + tab.dataset.tab).classList.add('active');
        });
    });

    // Logique pour ajouter dynamiquement les passifs, compétences, et sets d'artefacts
    setupDynamicFields();

    // Gestion de l'ouverture/fermeture de la modale
    document.getElementById('add-character-btn')?.addEventListener('click', () => {
        if (addCharacterDialog) addCharacterDialog.showModal();
    });

    document.getElementById('close-add-character')?.addEventListener('click', () => {
        if (addCharacterDialog) addCharacterDialog.close();
    });

    addCharacterDialog?.addEventListener('click', (event) => {
        if (event.target === addCharacterDialog) {
            addCharacterDialog.close();
        }
    });
});

function setupDynamicFields() {
    // Boutons pour ajouter des sections
    document.getElementById('add-passive-btn')?.addEventListener('click', addPassiveField);
    document.getElementById('add-skill-btn')?.addEventListener('click', addSkillField);
    // Initialiser la section des artefacts
    createArtefactSetSection();
}

async function getCharacterImages() {
    const form = document.getElementById('add-character-form');
    const type = form.querySelector('input[name="type"]').value;
    const alias = form.querySelector('input[name="alias"]').value;
    const rarity = form.querySelector('input[name="rarity"]').value;
    const typeFolder = type.replace(/ /g, "_");
    const folderName = `${rarity.replace(/ /g, "_")}_${typeFolder}_${alias.replace(/ /g, "_")}`;

    if (folderName && typeFolder) {
        try {
            const response = await fetch(`/characters/images_for/${encodeURIComponent(typeFolder)}/${encodeURIComponent(folderName)}`);
            if (response.ok) return await response.json();
        } catch (e) { console.error("Could not fetch images:", e); }
    }
    return [];
}

async function addPassiveField() {
    const grid = document.getElementById('passives-grid');
    const index = grid.querySelectorAll('.edit-passive-block').length;
    const images = await getCharacterImages();
    const selectOptions = ['<option value=""></option>'].concat(images.map(img => `<option value="${img}">${img}</option>`)).join('');

    const block = document.createElement('div');
    block.className = 'edit-passive-block';
    block.innerHTML = `
        <label>Nom du passif :</label> <input type="text" name="passive_name_${index}" />
        <label>Description :</label> <textarea name="passive_description_${index}"></textarea>
        <label>Tag :</label> <input type="text" name="passive_tag_${index}" />
        <label>Image :</label> <select name="passive_image_${index}">${selectOptions}</select>
        <div class="checkbox-row">
            <label><input type="checkbox" name="passive_principal_${index}" /> Principal</label>
            <label><input type="checkbox" name="passive_hidden_${index}" /> Caché</label>
        </div>
        <label>Ordre :</label> <input type="number" name="passive_order_${index}" value="${index}" min="0" style="width:60px;">
    `;
    grid.appendChild(block);
}

async function addSkillField() {
    const grid = document.getElementById('skills-grid');
    const index = grid.querySelectorAll('.edit-skill-block').length;
    const images = await getCharacterImages();
    const selectOptions = ['<option value=""></option>'].concat(images.map(img => `<option value="${img}">${img}</option>`)).join('');

    const block = document.createElement('div');
    block.className = 'edit-skill-block';
    block.innerHTML = `
        <label>Nom de la compétence :</label> <input type="text" name="skill_name_${index}" />
        <label>Description :</label> <textarea name="skill_description_${index}"></textarea>
        <label>Tag :</label> <input type="text" name="skill_tag_${index}" />
        <label>Image :</label> <select name="skill_image_${index}">${selectOptions}</select>
        <div class="checkbox-row"><label><input type="checkbox" name="skill_principal_${index}" /> Principal</label></div>
        <label>Ordre :</label> <input type="number" name="skill_order_${index}" value="${index}" min="0" style="width:60px;">
    `;
    grid.appendChild(block);
}

function createArtefactSetSection() {
    const container = document.getElementById('add-artefacts-fields');
    if (!container) return;

    // Ajouter un nouveau set
    const addSetButton = document.createElement('button');
    addSetButton.type = 'button';
    addSetButton.textContent = '+ Ajouter un nouveau set';
    addSetButton.className = 'add-btn';
    addSetButton.addEventListener('click', () => {
        const index = container.querySelectorAll('.edit-eqset-block').length;
        const setBlock = createSetBlock(index);
        container.appendChild(setBlock);
    });
    container.appendChild(addSetButton);
}

function createSetBlock(index) {
    const block = document.createElement('div');
    block.className = 'edit-eqset-block';
    block.id = `eqset-block-${index}`;

    // Elements du set
    block.innerHTML = `
        <h4>Set d'équipement #${index + 1}</h4>
        <label>Nom du set :</label><input type="text" name="eqset_name_${index}" required>
        <label>Description :</label><textarea name="eqset_description_${index}"></textarea>
        <label>Stats à focus :</label>
        <select multiple class="focus-stats-select" data-target="eqset_focus_stats_${index}">
            ${modalData.focusStatsOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
        </select>
        <input type="text" name="eqset_focus_stats_${index}" readonly placeholder="Max 6 stats">
        <input type="hidden" name="eqset_order_${index}" value="${index + 1}">

        <h4>Artefacts du set</h4>
        <div class="artefacts-grid">${createArtefactFields(index)}</div>

        <h4>Noyaux du set</h4>
        <div class="cores-grid">${createCoreFields(index)}</div>
        <hr style="margin-top: 20px;">
    `;

    // Ajout des listeners pour les multi-selects
    block.querySelectorAll('.focus-stats-select').forEach(select => {
        select.addEventListener('change', handleMultiSelectChange(6));
    });
     block.querySelectorAll('.artefact-secondary-multiselect').forEach(select => {
        select.addEventListener('change', handleMultiSelectChange(4));
    });

    return block;
}

function createArtefactFields(setIndex) {
    let html = '';
    const labels = modalData.artefactTypeLabels[modalData.currentLang] || modalData.artefactTypeLabels['FR-fr'];
    for (let i = 0; i < labels.length; i++) {
        const label = labels[i];
        const mainStatOptions = modalData.artefactMainStats[label] || [];

        html += `
            <div class="edit-artefact-block">
                <h5>${label}</h5>
                <input type="hidden" name="artefact_name_${setIndex}_${i}" value="${label}">
                <label>Panoplie :</label>
                <select name="artefact_set_${setIndex}_${i}">
                    <option value=""></option>
                    ${modalData.panopliesList.map(p => `<option value="${p}">${p}</option>`).join('')}
                </select>
                <label>Stat principale :</label>
                <select name="artefact_main_stat_${setIndex}_${i}">
                    <option value=""></option>
                    ${mainStatOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
                </select>
                <label>Stats secondaires :</label>
                 <select multiple class="artefact-secondary-multiselect" data-target="artefact_secondary_stats_${setIndex}_${i}">
                    ${modalData.secondaryStatsOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
                </select>
                <input type="text" name="artefact_secondary_stats_${setIndex}_${i}" readonly placeholder="Max 4 stats">
            </div>
        `;
    }
    return html;
}

function createCoreFields(setIndex) {
    let html = '';
    for (let i = 0; i < 3; i++) {
        const coreNum = `0${i + 1}`;
        const mainStatOptions = modalData.coreMainStats[coreNum] || [];
        const secondaryStatOptions = modalData.coreSecondaryStats[coreNum] || [];

        html += `
             <div class="edit-core-block">
                <h5>Noyau ${i + 1}</h5>
                <label>Nom du noyau :</label>
                <select name="core_name_${setIndex}_${i}">
                    <option value=""></option>
                    ${modalData.coresList.map(c => `<option value="${c}">${c}</option>`).join('')}
                </select>
                <label>Stat principale :</label>
                <select name="core_main_stat_${setIndex}_${i}">
                     <option value=""></option>
                    ${mainStatOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
                </select>
                <label>Stat secondaire :</label>
                <select name="core_secondary_stat_${setIndex}_${i}">
                     <option value=""></option>
                    ${secondaryStatOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
                </select>
            </div>
        `;
    }
    return html;
}

function handleMultiSelectChange(limit) {
    return function(event) {
        const select = event.target;
        const selected = Array.from(select.selectedOptions).map(opt => opt.value);
        if (selected.length > limit) {
            // Désélectionne la dernière option choisie
            event.target.options[event.target.selectedIndex].selected = false;
            alert(`Vous ne pouvez sélectionner que ${limit} options maximum.`);
        }
        const inputName = select.dataset.target;
        const input = select.closest('.edit-eqset-block, .edit-artefact-block').querySelector(`input[name="${inputName}"]`);
        if (input) {
            input.value = Array.from(select.selectedOptions).map(opt => opt.value).join(', ');
        }
    };
}
