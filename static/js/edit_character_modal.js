// static/js/edit_character_modal.js

// Données injectées depuis le template
let editModalData = {
    panopliesList: [],
    artefactMainStats: {},
    secondaryStatsOptions: [],
    focusStatsOptions: [],
    coresList: [],
    coreMainStats: {},
    coreSecondaryStats: {},
    artefactTypeLabels: {},
    currentLang: 'FR-fr'
};

function initializeEditModalData(data) {
    Object.assign(editModalData, data);
}

document.addEventListener("DOMContentLoaded", function () {
    const editCharacterDialog = document.getElementById('edit-character-dialog');
    if (!editCharacterDialog) return;

    // Gestion de l'ouverture/fermeture
    initializeModal("edit-character-btn", "edit-character-dialog", "close-edit-character");

    // Gestion des onglets
    editCharacterDialog.querySelectorAll('.edit-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            editCharacterDialog.querySelectorAll('.edit-tab').forEach(t => t.classList.remove('active'));
            editCharacterDialog.querySelectorAll('.edit-tab-content').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            editCharacterDialog.querySelector('#edit-tab-' + this.dataset.tab).classList.add('active');
        });
    });

    // Logique pour les champs dynamiques
    setupEditModalDynamicFields();

    // Remplir les selects d'images au chargement
    fillImageSelects();
});

function setupEditModalDynamicFields() {
    // Ajout d'un passif
    document.getElementById('add-passive-btn')?.addEventListener('click', addPassiveField);
    // Ajout d'une compétence
    document.getElementById('add-skill-btn')?.addEventListener('click', addSkillField);
    // Ajout d'un set d'équipement
    document.getElementById('edit-equipment-select')?.addEventListener('change', handleSetSelection);

    // Listeners pour les multi-selects
    document.addEventListener('change', function(e) {
      if (e.target.classList.contains('artefact-secondary-multiselect')) {
        handleMultiSelectChange(e.target, 4);
      }
      if (e.target.classList.contains('eqset-focus-multiselect')) {
        handleMultiSelectChange(e.target, 6);
      }
    });
}

async function getCharacterImagesForEdit() {
    const form = document.getElementById('edit-character-form');
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
    const images = await getCharacterImagesForEdit();
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
        <input type="hidden" name="passive_id_${index}" value="">
    `;
    grid.appendChild(block);
}
// ... (logique similaire pour addSkillField)

function handleSetSelection() {
    const selectedValue = this.value;
    if (selectedValue === "add_new_set") {
        // Logique pour ajouter un nouveau set
    } else {
        // Afficher le set sélectionné
        document.querySelectorAll('.edit-eqset-block').forEach(block => {
            block.style.display = 'none';
        });
        const blockToShow = document.getElementById(`eqset-block-${selectedValue}`);
        if(blockToShow) blockToShow.style.display = 'block';
    }
}

function handleMultiSelectChange(select, limit) {
    const selected = Array.from(select.selectedOptions).map(opt => opt.value);
    if (selected.length > limit) {
        // Simple alerte, pourrait être amélioré
        alert(`Vous ne pouvez sélectionner que ${limit} options.`);
        // Désélectionner la dernière option ajoutée
        const lastSelected = event.target.options[event.target.selectedIndex];
        lastSelected.selected = false;
    }
    const targetInput = document.querySelector(`input[name="${select.dataset.target}"]`);
    if (targetInput) {
        targetInput.value = Array.from(select.selectedOptions).map(opt => opt.value).join(', ');
    }
}

async function fillImageSelects() {
    const images = await getCharacterImagesForEdit();
    const passiveSelects = document.querySelectorAll('.passive-image-select');
    const skillSelects = document.querySelectorAll('.skill-image-select');

    passiveSelects.forEach(select => {
        const current = select.dataset.current || "";
        select.innerHTML = ['<option value=""></option>'].concat(images.map(img => `<option value="${img}"${img === current ? ' selected' : ''}>${img}</option>`)).join('');
    });
     skillSelects.forEach(select => {
        const current = select.dataset.current || "";
        select.innerHTML = ['<option value=""></option>'].concat(images.map(img => `<option value="${img}"${img === current ? ' selected' : ''}>${img}</option>`)).join('');
    });
}
