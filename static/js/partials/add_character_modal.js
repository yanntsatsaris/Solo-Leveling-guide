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
    const modal = document.getElementById('add-character-modal');
    const closeBtn = document.querySelector('#add-character-modal [data-close-modal]');

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
        const idx = this.value;
        document.querySelectorAll('.edit-eqset-block').forEach((block) => {
            block.style.display = (block.id === `eqset-block-${idx}`) ? 'block' : 'none';
        });
    });

    // Fermeture de la modale
    if (closeBtn && modal) {
        closeBtn.onclick = () => modal.close();
    }
    if (modal) {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.close();
            }
        });
    }

    // Ajout d'un passif
    document.getElementById('add-passive-btn')?.addEventListener('click', async function() {
        const grid = document.getElementById('passives-grid');
        const index = grid.querySelectorAll('.edit-passive-block').length;
        const folder = document.querySelector('#add-character-form input[name="image_folder"]').value;
        const type = document.querySelector('#add-character-form input[name="type"]').value;
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
        const folder = document.querySelector('#add-character-form input[name="image_folder"]').value;
        const type = document.querySelector('#add-character-form input[name="type"]').value;
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

        if (modal) modal.showModal();

        document.querySelector('#add-character-form input[name="name"]').value = name;
        document.querySelector('#add-character-form input[name="alias"]').value = alias;
        document.querySelector('#add-character-form input[name="type"]').value = type;
        document.querySelector('#add-character-form input[name="rarity"]').value = rarity;

        let hiddenInput = document.querySelector('#add-character-form input[name="image_folder"]');
        if (hiddenInput) hiddenInput.value = folderExists ? folderName : "";

        if (!folderExists) {
            let uploadOverlay = document.createElement('dialog');
            uploadOverlay.id = "upload-character-images-overlay";
            uploadOverlay.className = "edit-character-popup";
            uploadOverlay.innerHTML = `
              <article>
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
              </article>
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
