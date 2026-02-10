const panopliesList = [];
const artefactMainStats = {};
const secondaryStatsOptions = [];
const focusStatsOptions = [];
const coresList = [];
const coreMainStats = {};
const coreSecondaryStats = {};
let currentLang = 'FR-fr';

const artefactTypeLabels = {
    "FR-fr": ["Casque", "Plastron", "Gants", "Bottes", "Collier", "Bracelet", "Bague", "Boucle d'oreille"],
    "EN-en": ["Helmet", "Chestplate", "Gloves", "Boots", "Necklace", "Bracelet", "Ring", "Earring"]
};

function initializeAddCharacterModalData(data) {
    Object.assign(panopliesList, data.panopliesList || []);
    Object.assign(artefactMainStats, data.artefactMainStats || {});
    Object.assign(secondaryStatsOptions, data.secondaryStatsOptions || []);
    Object.assign(focusStatsOptions, data.focusStatsOptions || []);
    Object.assign(coresList, data.coresList || []);
    Object.assign(coreMainStats, data.coreMainStats || {});
    Object.assign(coreSecondaryStats, data.coreSecondaryStats || {});
    currentLang = data.currentLang || 'FR-fr';
}

function reindexEqsetBlocks() {
    const fields = document.getElementById('add-artefacts-fields');
    if (!fields) return;
    const blocks = Array.from(fields.querySelectorAll('.edit-eqset-block'));
    blocks.forEach((block, idx) => {
        block.id = `eqset-block-${idx}`;
        block.querySelectorAll('[name]').forEach(input => {
            input.name = input.name.replace(/_(\d+)(?:_(\d+))?/, function(_, oldIdx, subIdx) {
                if (typeof subIdx !== "undefined") {
                    return `_${idx}_${subIdx}`;
                }
                return `_${idx}`;
            });
            if (input.name === `eqset_order_${idx}`) {
                input.value = idx + 1;
            }
        });
    });
}

function reindexEqsetOptions() {
    const select = document.getElementById('add-equipment-select');
    if (!select) return;
    const addNewSetOption = select.querySelector('option[value="add_new_set"]');
    const options = Array.from(select.options).filter(opt => opt !== addNewSetOption);
    options.forEach((option, idx) => {
        option.value = idx;
        option.dataset.order = idx;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('add-character-modal');
    const closeBtns = modal?.querySelectorAll('.close-modal, [data-close-modal]');

    // Gestion des onglets
    document.querySelectorAll('#add-character-modal .edit-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('#add-character-modal .edit-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('#add-character-modal .edit-tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const targetContent = document.getElementById('add-character-modal').querySelector('#edit-tab-' + tab.dataset.tab);
            if (targetContent) targetContent.classList.add('active');
        });
    });

    // Sélecteur pour afficher le bon bloc de set à modifier dans l'onglet artefacts
    document.getElementById('add-equipment-select')?.addEventListener('change', function(e) {
        if (this.value === "add_new_set") {
            handleAddNewSet(this);
        } else {
            const idx = this.value;
            document.querySelectorAll('.edit-eqset-block').forEach((block) => {
                block.style.display = (block.id === `eqset-block-${idx}`) ? 'block' : 'none';
            });
        }
    });

    function handleAddNewSet(select) {
        const setName = prompt("Nom du nouveau set :");
        if (!setName) {
            select.value = 0;
            return;
        }
        const options = Array.from(select.options).filter(opt => opt.value !== "add_new_set");
        const setCount = options.length;
        let setOrder = prompt(`Ordre d'affichage du set (entrez un chiffre entre 1 et ${setCount + 1}) :`);

        if (setOrder === null) {
            select.value = 0;
            return;
        }
        setOrder = parseInt(setOrder) || (setCount + 1);
        const setOrderIndex = setOrder - 1;

        const option = document.createElement('option');
        option.value = setOrderIndex;
        option.textContent = setName;
        option.dataset.order = setOrderIndex;

        const addNewSetOption = select.querySelector('option[value="add_new_set"]');
        select.insertBefore(option, select.options[setOrderIndex] || addNewSetOption);
        select.value = setOrderIndex;

        // Create HTML block
        const fields = document.getElementById('add-artefacts-fields');
        const div = document.createElement('div');
        div.className = 'edit-eqset-block';
        div.id = `eqset-block-${setOrderIndex}`;
        div.style.display = 'block';

        document.querySelectorAll('.edit-eqset-block').forEach(b => b.style.display = 'none');

        const focusStatsSelect = `
            <select multiple size="6" class="eqset-focus-multiselect" data-target="eqset_focus_stats_${setOrderIndex}">
                ${focusStatsOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
            </select>
            <input type="text" name="eqset_focus_stats_${setOrderIndex}" value="" readonly style="margin-top:4px;">
        `;

        let artefactsHtml = '<div class="artefacts-row" style="display: flex; gap: 20px;"><div class="artefacts-col" style="flex: 1;">';
        for (let a_idx = 0; a_idx < 8; a_idx++) {
            if (a_idx === 4) artefactsHtml += '</div><div class="artefacts-col" style="flex: 1;">';
            const label = artefactTypeLabels[currentLang][a_idx];
            const mainStats = artefactMainStats[label] || [];
            artefactsHtml += `
                <div class="edit-artefact-block">
                    <label>${label}</label>
                    <input type="hidden" name="artefact_name_${setOrderIndex}_${a_idx}" value="${label}">
                    <label>Panoplie :</label>
                    <select name="artefact_set_${setOrderIndex}_${a_idx}">
                        <option value=""></option>
                        ${panopliesList.map(p => `<option value="${p}">${p}</option>`).join('')}
                    </select>
                    <label>Stat principale :</label>
                    <select name="artefact_main_stat_${setOrderIndex}_${a_idx}">
                        <option value=""></option>
                        ${mainStats.map(s => `<option value="${s}">${s}</option>`).join('')}
                    </select>
                    <label>Stats secondaires :</label>
                    <select multiple size="6" class="artefact-secondary-multiselect" data-target="artefact_secondary_stats_${setOrderIndex}_${a_idx}">
                        ${secondaryStatsOptions.map(s => `<option value="${s}">${s}</option>`).join('')}
                    </select>
                    <input type="text" name="artefact_secondary_stats_${setOrderIndex}_${a_idx}" value="" readonly style="margin-top:4px;">
                    <input type="hidden" name="artefact_id_${setOrderIndex}_${a_idx}" value="">
                </div>
            `;
        }
        artefactsHtml += '</div></div>';

        let coresHtml = '';
        for (let c_idx = 0; c_idx < 3; c_idx++) {
            const coreNum = (c_idx + 1).toString().padStart(2, '0');
            coresHtml += `
                <div class="edit-core-block">
                    <label>Nom du noyau :</label>
                    <select name="core_name_${setOrderIndex}_${c_idx}">
                        <option value=""></option>
                        ${coresList.map(c => `<option value="${c}">${c}</option>`).join('')}
                    </select>
                    <label>Stat principale :</label>
                    <select name="core_main_stat_${setOrderIndex}_${c_idx}">
                        <option value=""></option>
                        ${coreMainStats[coreNum].map(s => `<option value="${s}">${s}</option>`).join('')}
                    </select>
                    <label>Stat secondaire :</label>
                    <select name="core_secondary_stat_${setOrderIndex}_${c_idx}">
                        <option value=""></option>
                        ${coreSecondaryStats[coreNum].map(s => `<option value="${s}">${s}</option>`).join('')}
                    </select>
                    <input type="hidden" name="core_id_${setOrderIndex}_${c_idx}" value="">
                </div>
                <hr>
            `;
        }

        div.innerHTML = `
            <h4>Set : ${setName}</h4>
            <input type="hidden" name="eqset_name_${setOrderIndex}" value="${setName}">
            <input type="hidden" name="eqset_id_${setOrderIndex}" value="">
            <div class="add-form-group">
                <label>Description :</label>
                <textarea name="eqset_description_${setOrderIndex}"></textarea>
            </div>
            <div class="add-form-group">
                <label>Stats à focus :</label>
                ${focusStatsSelect}
            </div>
            <input type="hidden" name="eqset_order_${setOrderIndex}" value="${setOrder}">
            <h4>Artefacts du set</h4>
            ${artefactsHtml}
            <hr>
            <h4>Noyaux du set</h4>
            ${coresHtml}
        `;

        fields.appendChild(div);
        reindexEqsetBlocks();
        reindexEqsetOptions();
    }

    // Fermeture de la modale
    if (closeBtns && modal) {
        closeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                modal.close();
                modal.setAttribute('hidden', '');
            });
        });
    }
    if (modal) {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.close();
                modal.setAttribute('hidden', '');
            }
        });
    }

    // Ajout d'un passif
    document.getElementById('add-passive-btn')?.addEventListener('click', async function() {
        const grid = document.getElementById('passives-grid');
        const index = grid.querySelectorAll('.edit-passive-block').length;
        const folderInput = document.querySelector('#add-character-form input[name="image_folder"]');
        const typeInput = document.querySelector('#add-character-form input[name="type"]');
        if (!folderInput || !typeInput) return;
        const folder = folderInput.value;
        const type = typeInput.value;
        const typeFolder = type.replace(/ /g, "_");

        let images = [];
        if (folder && typeFolder) {
            try {
                images = await fetch(`/characters/images_for/${encodeURIComponent(typeFolder)}/${encodeURIComponent(folder)}`).then(r => r.json());
            } catch (e) { images = []; }
        }
        const selectOptions = ['<option value=""></option>']
            .concat(images.map(img => `<option value="${img}">${img}</option>`)).join('');
        const row = document.createElement('div');
        row.className = 'passives-row';
        row.innerHTML = `
      <div class="edit-passive-block">
        <label>Nom du passif :</label>
        <input type="text" name="passive_name_${index}" value="" />
        <label>Description :</label>
        <textarea name="passive_description_${index}"></textarea>
        <label>Tag :</label>
        <input type="text" name="passive_tag_${index}" value="" />
        <label>Image :</label>
        <select name="passive_image_${index}">${selectOptions}</select>
        <div class="checkbox-row">
          <label>
            <input type="checkbox" name="passive_principal_${index}" /> Principal
          </label>
          <label>
            <input type="checkbox" name="passive_hidden_${index}" /> Caché
          </label>
        </div>
        <label>Ordre :</label>
        <input type="number" name="passive_order_${index}" value="${index}" min="0" style="width:60px;">
      </div>
    `;
        grid.appendChild(row);
    });

    // Ajout d'une compétence
    document.getElementById('add-skill-btn')?.addEventListener('click', async function() {
        const grid = document.getElementById('skills-grid');
        const index = grid.querySelectorAll('.edit-skill-block').length;
        const folderInput = document.querySelector('#add-character-form input[name="image_folder"]');
        const typeInput = document.querySelector('#add-character-form input[name="type"]');
        if (!folderInput || !typeInput) return;
        const folder = folderInput.value;
        const type = typeInput.value;
        const typeFolder = type.replace(/ /g, "_");

        let images = [];
        if (folder && typeFolder) {
            try {
                images = await fetch(`/characters/images_for/${encodeURIComponent(typeFolder)}/${encodeURIComponent(folder)}`).then(r => r.json());
            } catch (e) { images = []; }
        }
        const selectOptions = ['<option value=""></option>']
            .concat(images.map(img => `<option value="${img}">${img}</option>`)).join('');
        const row = document.createElement('div');
        row.className = 'skills-row';
        row.innerHTML = `
      <div class="edit-skill-block">
        <label>Nom de la compétence :</label>
        <input type="text" name="skill_name_${index}" value="" />
        <label>Description :</label>
        <textarea name="skill_description_${index}"></textarea>
        <label>Tag :</label>
        <input type="text" name="skill_tag_${index}" value="" />
        <label>Image :</label>
        <select name="skill_image_${index}">${selectOptions}</select>
        <div class="checkbox-row">
          <label>
            <input type="checkbox" name="skill_principal_${index}" /> Principal
          </label>
        </div>
        <label>Ordre :</label>
        <input type="number" name="skill_order_${index}" value="${index}" min="0" style="width:60px;">
      </div>
    `;
        grid.appendChild(row);
    });

    document.getElementById('add-character-btn')?.addEventListener('click', async function() {
        const name = prompt("Nom du personnage :");
        if (!name) return;
        const alias = prompt("Alias du personnage :");
        if (!alias) return;
        const type = prompt("Type du personnage :");
        if (!type) return;
        const rarity = prompt("Rareté du personnage :");
        if (!rarity) return;

        const typeFolder = type.replace(/ /g, "_");
        const aliasFolder = alias.replace(/ /g, "_");
        const rarityFolder = rarity.replace(/ /g, "_");
        const folderName = `${rarityFolder}_${typeFolder}_${aliasFolder}`;

        let folderExists = false;
        try {
            const resp = await fetch(`/characters/add/check_image_folder?type=${encodeURIComponent(type)}&alias=${encodeURIComponent(alias)}&rarity=${encodeURIComponent(rarity)}`);
            const data = await resp.json();
            folderExists = data.exists;
        } catch (e) {
            folderExists = false;
        }

        if (modal) {
            modal.removeAttribute('hidden');
            modal.showModal();
        }

        document.querySelector('#add-character-form input[name="name"]').value = name;
        document.querySelector('#add-character-form input[name="alias"]').value = alias;
        document.querySelector('#add-character-form input[name="type"]').value = type;
        document.querySelector('#add-character-form input[name="rarity"]').value = rarity;

        let hiddenInput = document.querySelector('#add-character-form input[name="image_folder"]');
        if (hiddenInput) hiddenInput.value = folderExists ? folderName : "";

        if (!folderExists) {
            let uploadOverlay = document.createElement('dialog');
            uploadOverlay.id = "upload-character-images-overlay";
            uploadOverlay.className = "add-character-content"; // Reuse some styles
            uploadOverlay.innerHTML = `
                <form id="upload-character-images-form" enctype="multipart/form-data">
                    <h2>Uploader les images du personnage (.zip)</h2>
                    <input type="file" name="images_zip" accept=".zip" required>
                    <input type="hidden" name="type" value="${type}">
                    <input type="hidden" name="alias" value="${alias}">
                    <input type="hidden" name="rarity" value="${rarity}">
                    <div style="margin-top:16px; display:flex; justify-content: space-between;">
                        <button type="submit" class="admin-btn">Envoyer</button>
                        <button type="button" id="cancel-upload-character-images" class="close-btn">&times;</button>
                    </div>
                </form>
            `;
            document.body.appendChild(uploadOverlay);
            uploadOverlay.showModal();

            document.getElementById('cancel-upload-character-images').onclick = function() {
                uploadOverlay.close();
                uploadOverlay.remove();
            };

            document.getElementById('upload-character-images-form').onsubmit = async function(e) {
                e.preventDefault();
                let formData = new FormData(this);
                let resp = await fetch('/admin/upload_character_images_zip', {
                    method: 'POST',
                    body: formData
                });
                let txt = await resp.text();
                uploadOverlay.close();
                uploadOverlay.remove();
                alert(txt);
            };
        }
    });

    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('artefact-secondary-multiselect')) {
            const select = e.target;
            const selected = Array.from(select.selectedOptions).map(opt => opt.value);
            if (selected.length > 4) {
                select.options[select.selectedIndex].selected = false;
                alert("Vous ne pouvez sélectionner que 4 stats secondaires maximum.");
                return;
            }
            const inputName = select.dataset.target;
            const input = select.parentElement.querySelector(`input[name="${inputName}"]`);
            if (input) input.value = selected.join(', ');
        }
        if (e.target.classList.contains('eqset-focus-multiselect')) {
            const select = e.target;
            const selected = Array.from(select.selectedOptions).map(opt => opt.value);
            if (selected.length > 6) {
                select.options[select.selectedIndex].selected = false;
                alert("Vous ne pouvez sélectionner que 6 stats à focus maximum.");
                return;
            }
            const inputName = select.dataset.target;
            const input = select.parentElement.querySelector(`input[name="${inputName}"]`);
            if (input) input.value = selected.join(', ');
        }
    });
});
