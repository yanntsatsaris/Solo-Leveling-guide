// Liste des noms de panoplies récupérée depuis Flask
const panopliesList = [];
const artefactMainStats = {};
const secondaryStatsOptions = [];
const focusStatsOptions = [];
const coresList = [];
const coreMainStats = {};
const coreSecondaryStats = {};

function initializeAddCharacterModalData(data) {
  Object.assign(panopliesList, data.panopliesList || []);
  Object.assign(artefactMainStats, data.artefactMainStats || {});
  Object.assign(secondaryStatsOptions, data.secondaryStatsOptions || []);
  Object.assign(focusStatsOptions, data.focusStatsOptions || []);
  Object.assign(coresList, data.coresList || []);
  Object.assign(coreMainStats, data.coreMainStats || {});
  Object.assign(coreSecondaryStats, data.coreSecondaryStats || {});
}

document.addEventListener('DOMContentLoaded', () => {
    // Gestion des onglets
    document.querySelectorAll('#add-character-menu .edit-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('#add-character-menu .edit-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('#add-character-menu .edit-tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById('add-character-menu').querySelector('#edit-tab-' + tab.dataset.tab).classList.add('active');
        });
    });

    // Sélecteur pour afficher le bon bloc de set à modifier dans l'onglet artefacts
    document.getElementById('add-equipment-select')?.addEventListener('change', function(e) {
        const idx = this.value;
        document.querySelectorAll('.edit-eqset-block').forEach((block) => {
            block.style.display = (block.id === `eqset-block-${idx}`) ? 'block' : 'none';
        });
    });

    // Ajout d'un passif
    document.getElementById('add-passive-btn')?.addEventListener('click', async function() {
        const grid = document.getElementById('passives-grid');
        const index = grid.querySelectorAll('.edit-passive-block').length;
        // Récupère le dossier image du personnage
        const folder = document.querySelector('#add-character-form input[name="image_folder"]').value;
        const type = document.querySelector('#add-character-form input[name="type"]').value;
        const alias = document.querySelector('#add-character-form input[name="alias"]').value;
        const rarity = document.querySelector('#add-character-form input[name="rarity"]').value;
        const typeFolder = type.replace(/ /g, "_");
        const aliasFolder = alias.replace(/ /g, "_");
        const rarityFolder = rarity.replace(/ /g, "_");
        const folderName = `${rarityFolder}_${typeFolder}_${aliasFolder}`;
        let images = [];
        if (folderName && typeFolder) {
            try {
                images = await fetch(`/characters/images_for/${encodeURIComponent(typeFolder)}/${encodeURIComponent(folderName)}`).then(r => r.json());
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
          <label>Ordre :</label>
          <input type="number" name="passive_order_${index}" value="${index}" min="0" style="width:60px;">
        </div>
      </div>
    `;
        grid.appendChild(row);
    });

    // Ajout d'une compétence
    document.getElementById('add-skill-btn')?.addEventListener('click', async function() {
        const grid = document.getElementById('skills-grid');
        const index = grid.querySelectorAll('.edit-skill-block').length;
        const folder = document.querySelector('#add-character-form input[name="image_folder"]').value;
        const type = document.querySelector('#add-character-form input[name="type"]').value;
        const alias = document.querySelector('#add-character-form input[name="alias"]').value;
        const rarity = document.querySelector('#add-character-form input[name="rarity"]').value;
        const typeFolder = type.replace(/ /g, "_");
        const aliasFolder = alias.replace(/ /g, "_");
        const rarityFolder = rarity.replace(/ /g, "_");
        const folderName = `${rarityFolder}_${typeFolder}_${aliasFolder}`;
        let images = [];
        if (folderName && typeFolder) {
            try {
                images = await fetch(`/characters/images_for/${encodeURIComponent(typeFolder)}/${encodeURIComponent(folderName)}`).then(r => r.json());
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

    // Ajout d'un set d'équipement (similaire à edit_character_modal.html)
    document.getElementById('add-equipment-select')?.addEventListener('click', function(e) {
        if (this.value === "add_new_set") {
            const setName = prompt("Nom du nouveau set :");
            if (!setName) {
                this.value = 0;
                return;
            }
            const options = Array.from(this.options).filter(opt => opt.value !== "add_new_set");
            const setCount = options.length;
            let setOrder;
            do {
                setOrder = prompt(`Ordre d'affichage du set (entrez un chiffre entre 1 et ${setCount + 1}) :`);
                if (setOrder === null) {
                    this.value = 0;
                    return;
                }
                if (setOrder.trim() === "") {
                    setOrder = setCount + 1;
                    break;
                }
                setOrder = Number(setOrder);
            } while (!Number.isInteger(setOrder) || setOrder < 1 || setOrder > setCount + 1);

            const setOrderIndex = setOrder - 1;

            options.forEach(opt => {
                const optOrder = opt.dataset.order !== undefined && opt.dataset.order !== "" ?
                    Number(opt.dataset.order) :
                    Number.MAX_SAFE_INTEGER;
                if (optOrder >= setOrderIndex) {
                    opt.dataset.order = optOrder + 1;
                    const block = document.getElementById(`eqset-block-${opt.value}`);
                    if (block) {
                        const orderInput = block.querySelector(`input[name="eqset_order_${opt.value}"]`);
                        if (orderInput) orderInput.value = Number(opt.dataset.order) + 1;
                    }
                }
            });

            const option = document.createElement('option');
            option.value = setOrderIndex;
            option.textContent = setName;
            option.dataset.order = setOrderIndex;

            const select = this;
            const addNewSetOption = select.querySelector('option[value="add_new_set"]');
            const setOptions = Array.from(select.options).filter(opt => opt !== addNewSetOption);

            let insertPos = 0;
            if (setOptions.length > 0) {
                insertPos = setOptions.filter(opt => {
                    const optOrder = opt.dataset.order !== undefined && opt.dataset.order !== "" ?
                        Number(opt.dataset.order) :
                        Number.MAX_SAFE_INTEGER;
                    return optOrder < setOrderIndex;
                }).length;
            }
            select.insertBefore(option, setOptions[insertPos] || addNewSetOption);
            select.value = setOrderIndex;

            // Crée le bloc HTML du nouveau set
            const fields = document.getElementById('add-artefacts-fields');
            const div = document.createElement('div');
            div.className = 'edit-eqset-block';
            div.id = `eqset-block-${setOrderIndex}`;
            div.style.display = 'block';
            const focusStatsSelect = `
        <select multiple size="6" class="eqset-focus-multiselect" data-target="eqset_focus_stats_${setOrderIndex}">
          ${focusStatsOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
        </select>
        <input type="text" name="eqset_focus_stats_${setOrderIndex}" value="" readonly style="margin-top:4px;">
      `;
            let artefactsCol1 = '';
            for (let a_idx = 0; a_idx < 4; a_idx++) {
                const artefactLabel = artefactTypeLabels[currentLang] ? artefactTypeLabels[currentLang][a_idx] : artefactTypeLabels["FR-fr"][a_idx];
                const mainStatOptions = artefactMainStats[artefactLabel] || [];
                const mainStatSelect = `
          <select name="artefact_main_stat_${setOrderIndex}_${a_idx}">
            <option value=""></option>
            ${mainStatOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
          </select>
        `;
                const secondaryStatSelect = `
          <select multiple size="6" class="artefact-secondary-multiselect" data-target="artefact_secondary_stats_${setOrderIndex}_${a_idx}">
            ${secondaryStatsOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
          </select>
          <input type="text" name="artefact_secondary_stats_${setOrderIndex}_${a_idx}" value="" readonly style="margin-top:4px;">
        `;
                const panoplieSelect = `
          <select name="artefact_set_${setOrderIndex}_${a_idx}">
            <option value=""></option>
            ${panopliesList.map(p => `<option value="${p}">${p}</option>`).join('')}
          </select>
        `;
                artefactsCol1 += `
          <div class="edit-artefact-block">
            <label>${artefactLabel}</label>
            <input type="hidden" name="artefact_name_${setOrderIndex}_${a_idx}" value="${artefactLabel}">
            <label>Pannoplie :</label>
            ${panoplieSelect}
            <label>Stat principale :</label>
            ${mainStatSelect}
            <label>Stats secondaires :</label>
            ${secondaryStatSelect}
            <input type="hidden" name="artefact_id_${setOrderIndex}_${a_idx}" value="">
          </div>
        `;
            }

            let artefactsCol2 = '';
            for (let a_idx = 4; a_idx < 8; a_idx++) {
                const artefactLabel = artefactTypeLabels[currentLang] ? artefactTypeLabels[currentLang][a_idx] : artefactTypeLabels["FR-fr"][a_idx];
                const mainStatOptions = artefactMainStats[artefactLabel] || [];
                const mainStatSelect = `
          <select name="artefact_main_stat_${setOrderIndex}_${a_idx}">
            <option value=""></option>
            ${mainStatOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
          </select>
        `;
                const secondaryStatSelect = `
          <select multiple size="6" class="artefact-secondary-multiselect" data-target="artefact_secondary_stats_${setOrderIndex}_${a_idx}">
            ${secondaryStatsOptions.map(stat => `<option value="${stat}">${stat}</option>`).join('')}
          </select>
          <input type="text" name="artefact_secondary_stats_${setOrderIndex}_${a_idx}" value="" readonly style="margin-top:4px;">
        `;
                const panoplieSelect = `
          <select name="artefact_set_${setOrderIndex}_${a_idx}">
            <option value=""></option>
            ${panopliesList.map(p => `<option value="${p}">${p}</option>`).join('')}
          </select>
        `;
                artefactsCol2 += `
          <div class="edit-artefact-block">
            <label>${artefactLabel}</label>
            <input type="hidden" name="artefact_name_${setOrderIndex}_${a_idx}" value="${artefactLabel}">
            <label>Pannoplie :</label>
            ${panoplieSelect}
            <label>Stat principale :</label>
            ${mainStatSelect}
            <label>Stats secondaires :</label>
            ${secondaryStatSelect}
            <input type="hidden" name="artefact_id_${setOrderIndex}_${a_idx}" value="">
          </div>
        `;
            }
            let coresHtml = '';
            for (let coreIdx = 0; coreIdx < 3; coreIdx++) {
                const coreNumber = `${coreIdx + 1}`.padStart(2, "0"); // "01", "02", "03"
                const coreNameSelect = `
          <select name="core_name_${setOrderIndex}_${coreIdx}">
            <option value=""></option>
            ${coresList.map(c => `<option value="${c}">${c}</option>`).join('')}
          </select>
        `;
                const coreMainStatSelect = `
          <select name="core_main_stat_${setOrderIndex}_${coreIdx}">
            <option value=""></option>
            ${coreMainStats[coreNumber].map(stat => `<option value="${stat}">${stat}</option>`).join('')}
          </select>
        `;
                const coreSecondaryStatSelect = `
          <select name="core_secondary_stat_${setOrderIndex}_${coreIdx}">
            <option value=""></option>
            ${coreSecondaryStats[coreNumber].map(stat => `<option value="${stat}">${stat}</option>`).join('')}
          </select>
        `;
                coresHtml += `
          <div class="edit-core-block">
            <label>Nom du noyau :</label>
            ${coreNameSelect}
            <label>Stat principale :</label>
            ${coreMainStatSelect}
            <label>Stat secondaire :</label>
            ${coreSecondaryStatSelect}
            <input type="hidden" name="core_id_${setOrderIndex}_${coreIdx}" value="">
          </div>
          <hr>
        `;
            }
            div.innerHTML = `
        <h4>Set : ${setName}</h4>
        <input type="hidden" name="eqset_name_${setOrderIndex}" value="${setName}">
        <input type="hidden" name="eqset_id_${setOrderIndex}" value="">
        <label>Description :</label>
        <textarea name="eqset_description_${setOrderIndex}"></textarea>
        <label>Stats à focus :</label>
        ${focusStatsSelect}
        <input type="hidden" name="eqset_order_${setOrderIndex}" value="${setOrder}">
        <h4>Artefacts du set</h4>
        <div class="artefacts-row" style="display: flex;">
          <div class="artefacts-col" style="flex: 1;">
            ${artefactsCol1}
          </div>
          <div class="artefacts-col" style="flex: 1;">
            ${artefactsCol2}
          </div>
        </div>
        <hr>
        <h4>Noyaux du set</h4>
        ${coresHtml}
      `;
            const blocks = Array.from(fields.querySelectorAll('.edit-eqset-block'));
            if (insertPos < blocks.length) {
                fields.insertBefore(div, blocks[insertPos]);
            } else {
                fields.appendChild(div);
            }
            reindexEqsetBlocks();
            reindexEqsetOptions();
        }
    });

    function reindexEqsetBlocks() {
        const fields = document.getElementById('add-artefacts-fields');
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
        const addNewSetOption = select.querySelector('option[value="add_new_set"]');
        const options = Array.from(select.options).filter(opt => opt !== addNewSetOption);
        options.forEach((option, idx) => {
            option.value = idx;
            option.dataset.order = idx;
        });
    }

    // Dictionnaire des types d'artefacts par langue
    const artefactTypeLabels = {
        "FR-fr": ["Casque", "Plastron", "Gants", "Bottes", "Collier", "Bracelet", "Bague", "Boucle d'oreille"],
        "EN-en": ["Helmet", "Chestplate", "Gloves", "Boots", "Necklace", "Bracelet", "Ring", "Earring"]
    };
    // Détecte la langue courante (à adapter selon ton contexte)
    const currentLang = "{{ language if language is defined else 'FR-fr' }}";

    // Fermeture de la modale
    document.getElementById('close-add-character')?.addEventListener('click', function() {
        document.getElementById('add-character-overlay').style.display = 'none';
    });
    // Ferme la modale si clic en dehors du popup
    const addOverlay = document.getElementById('add-character-overlay');
    const addPopup = document.getElementById('add-character-menu');
    if (addOverlay && addPopup) {
        addOverlay.addEventListener('mousedown', function(e) {
            if (e.target === addOverlay) {
                addOverlay.style.display = 'none';
            }
        });
    }

    document.getElementById('add-character-btn')?.addEventListener('click', async function() {
        // Demande les infos de base
        const name = prompt("Nom du personnage :");
        if (!name) return;
        const alias = prompt("Alias du personnage :");
        if (!alias) return;
        const type = prompt("Type du personnage :");
        if (!type) return;
        const rarity = prompt("Rareté du personnage :");
        if (!rarity) return;

        // Construit le chemin du dossier image
        // On suppose que tu veux remplacer les espaces par des underscores
        const typeFolder = type.replace(/ /g, "_");
        const aliasFolder = alias.replace(/ /g, "_");
        const rarityFolder = rarity.replace(/ /g, "_");
        const folderName = `${rarityFolder}_${typeFolder}_${aliasFolder}`;
        const folderPath = `/static/images/Personnage/SLA_Personnages_${typeFolder}/${folderName}/`;

        // Vérifie si le dossier existe côté serveur (nécessite une route Flask dédiée)
        let folderExists = false;
        try {
            const resp = await fetch(`/characters/add/check_image_folder?type=${encodeURIComponent(type)}&alias=${encodeURIComponent(alias)}&rarity=${encodeURIComponent(rarity)}`);
            folderExists = (await resp.json()).exists;
        } catch (e) {
            // Si la vérification échoue, on continue quand même
            folderExists = false;
        }

        // Ouvre la modale d'ajout
        document.getElementById('add-character-overlay').style.display = 'flex';

        // Pré-remplit les champs
        document.querySelector('#add-character-form input[name="name"]').value = name;
        document.querySelector('#add-character-form input[name="alias"]').value = alias;
        document.querySelector('#add-character-form input[name="type"]').value = type;
        document.querySelector('#add-character-form input[name="rarity"]').value = rarity;

        // Ajoute ou met à jour l'input hidden pour le dossier image
        let hiddenInput = document.querySelector('#add-character-form input[name="image_folder"]');
        if (!hiddenInput) {
            hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'image_folder';
            document.getElementById('add-character-form').appendChild(hiddenInput);
        }
        hiddenInput.value = folderExists ? folderName : "";

        // Optionnel : affiche une alerte si le dossier n'existe pas
        if (!folderExists) {
            let overlay = document.createElement('div');
            overlay.id = "upload-character-images-overlay";
            overlay.className = "edit-character-overlay";
            overlay.style.display = "flex";
            overlay.innerHTML = `
        <div class="edit-character-popup">
          <form id="upload-character-images-form" enctype="multipart/form-data">
            <h2>Uploader les images du personnage (.zip)</h2>
            <input type="file" name="images_zip" accept=".zip" required>
            <input type="hidden" name="type" value="${type}">
            <input type="hidden" name="alias" value="${alias}">
            <input type="hidden" name="rarity" value="${rarity}">
            <div style="margin-top:16px;">
              <button type="submit" class="admin-btn">Envoyer</button>
              <button type="button" id="cancel-upload-character-images" class="close-btn">&times;</button>
            </div>
          </form>
        </div>
      `;
            document.body.appendChild(overlay);

            document.getElementById('cancel-upload-character-images').onclick = function() {
                overlay.remove();
            };

            document.getElementById('upload-character-images-form').onsubmit = async function(e) {
                e.preventDefault();
                let formData = new FormData(this);
                let resp = await fetch('/admin/upload_character_images_zip', {
                    method: 'POST',
                    body: formData
                });
                let txt = await resp.text();
                overlay.remove();
                alert(txt);
                // Optionnel : recharger ou réinitialiser le formulaire
            };
        }
    });
    document.addEventListener('change', function(e) {
        // Limite à 4 stats secondaires
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
        // Limite à 6 stats à focus
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