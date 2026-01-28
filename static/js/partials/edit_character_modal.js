// Liste des noms de panoplies récupérée depuis Flask
let panopliesList = [];
let artefactMainStats = {};
let secondaryStatsOptions = [];
let focusStatsOptions = [];
let coresList = [];
let coreMainStats = {};
let coreSecondaryStats = {};
let artefactTypeLabels = {};
let currentLang = "FR-fr";

function initializeEditCharacterModalData(data) {
  panopliesList = data.panopliesList || [];
  artefactMainStats = data.artefactMainStats || {};
  secondaryStatsOptions = data.secondaryStatsOptions || [];
  focusStatsOptions = data.focusStatsOptions || [];
  coresList = data.coresList || [];
  coreMainStats = data.coreMainStats || {};
  coreSecondaryStats = data.coreSecondaryStats || {};
  artefactTypeLabels = data.artefactTypeLabels || {};
  currentLang = data.currentLang || "FR-fr";
}

document.addEventListener("DOMContentLoaded", () => {
  // Gestion des onglets
  document.querySelectorAll('.edit-tab').forEach(tab => {
    tab.addEventListener('click', function() {
      document.querySelectorAll('.edit-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.edit-tab-content').forEach(c => c.classList.remove('active'));
      tab.classList.add('active');
      const content = document.getElementById('edit-tab-' + tab.dataset.tab);
      if (content) content.classList.add('active');
    });
  });

  // Sélecteur pour afficher le bon bloc de set à modifier dans l'onglet artefacts
  document.getElementById('edit-equipment-select')?.addEventListener('change', function(e) {
    const idx = this.value;
    document.querySelectorAll('.edit-eqset-block').forEach((block) => {
      block.style.display = (block.id === `eqset-block-${idx}`) ? 'block' : 'none';
    });
  });

  // Sauvegarde l'état initial du formulaire à l'ouverture
  let initialFormData = null;
  const form = document.getElementById('edit-character-form');
  if (form) {
    function serializeForm(form) {
      const formData = new FormData(form);
      return Array.from(formData.entries()).sort();
    }
    document.getElementById('edit-character-btn')?.addEventListener('click', () => {
      initialFormData = serializeForm(form);
    });
    form.addEventListener('submit', function(e) {
      Array.from(form.elements).forEach(el => {
        if (el.value === "None") {
          el.value = null;
        }
      });
      const currentFormData = serializeForm(form);
      if (initialFormData && JSON.stringify(initialFormData) === JSON.stringify(currentFormData)) {
        e.preventDefault();
        alert("Aucune modification détectée.");
        return false;
      }
    });
  }

  // Fermeture de la modale
  const modal = document.getElementById('edit-character-modal');
  const closeBtn = document.querySelector("#edit-character-modal [data-close-modal]");
  if (closeBtn && modal) {
    closeBtn.onclick = () => {
      if (typeof modal.close === 'function') {
        modal.close();
      } else {
        modal.style.display = "none";
      }
    };
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
    const folder = document.querySelector('#edit-character-form input[name="image_folder"]').value;
    const type = document.querySelector('#edit-character-form input[name="type"]').value;
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
    const folder = document.querySelector('#edit-character-form input[name="image_folder"]').value;
    const type = document.querySelector('#edit-character-form input[name="type"]').value;
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

  // Ajout d'un set d'équipement
  document.getElementById('edit-equipment-select')?.addEventListener('click', function(e) {
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
        const optOrder = opt.dataset.order !== undefined && opt.dataset.order !== ""
          ? Number(opt.dataset.order)
          : Number.MAX_SAFE_INTEGER;
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
          const optOrder = opt.dataset.order !== undefined && opt.dataset.order !== ""
            ? Number(opt.dataset.order)
            : Number.MAX_SAFE_INTEGER;
          return optOrder < setOrderIndex;
        }).length;
      }
      select.insertBefore(option, setOptions[insertPos] || addNewSetOption);
      select.value = setOrderIndex;

      const fields = document.getElementById('edit-artefacts-fields');
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
      const labels = artefactTypeLabels[currentLang] || artefactTypeLabels["FR-fr"];
      for (let a_idx = 0; a_idx < 4; a_idx++) {
        const artefactLabel = labels[a_idx];
        const mainStatOptions = artefactMainStats[artefactLabel] || [];
        artefactsCol1 += generateArtefactBlock(setOrderIndex, a_idx, artefactLabel, mainStatOptions);
      }

      let artefactsCol2 = '';
      for (let a_idx = 4; a_idx < 8; a_idx++) {
        const artefactLabel = labels[a_idx];
        const mainStatOptions = artefactMainStats[artefactLabel] || [];
        artefactsCol2 += generateArtefactBlock(setOrderIndex, a_idx, artefactLabel, mainStatOptions);
      }

      let coresHtml = '';
      for (let coreIdx = 0; coreIdx < 3; coreIdx++) {
        coresHtml += generateCoreBlock(setOrderIndex, coreIdx);
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

  function generateArtefactBlock(setOrderIndex, a_idx, artefactLabel, mainStatOptions) {
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
    return `
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

  function generateCoreBlock(setOrderIndex, coreIdx) {
    const coreNumber = `${coreIdx + 1}`.padStart(2, "0");
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
    return `
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

  function reindexEqsetBlocks() {
    const fields = document.getElementById('edit-artefacts-fields');
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
    const select = document.getElementById('edit-equipment-select');
    const addNewSetOption = select.querySelector('option[value="add_new_set"]');
    const options = Array.from(select.options).filter(opt => opt !== addNewSetOption);
    options.forEach((option, idx) => {
      option.value = idx;
      option.dataset.order = idx;
    });
  }

  async function fillImageSelects() {
    const folder = document.querySelector('#edit-character-form input[name="image_folder"]')?.value;
    const type = document.querySelector('#edit-character-form input[name="type"]')?.value;
    const typeFolder = type?.replace(/ /g, "_");

    let images = [];
    if (folder && typeFolder) {
      try {
        images = await fetch(`/characters/images_for/${encodeURIComponent(typeFolder)}/${encodeURIComponent(folder)}`).then(r => r.json());
      } catch (e) { images = []; }
    }
    document.querySelectorAll('.passive-image-select').forEach(select => {
      const current = select.dataset.current || "";
      select.innerHTML = ['<option value=""></option>']
        .concat(images.map(img => `<option value="${img}"${img === current ? ' selected' : ''}>${img}</option>`)).join('');
    });
    document.querySelectorAll('.skill-image-select').forEach(select => {
      const current = select.dataset.current || "";
      select.innerHTML = ['<option value=""></option>']
        .concat(images.map(img => `<option value="${img}"${img === current ? ' selected' : ''}>${img}</option>`)).join('');
    });
  }

  document.getElementById('edit-character-btn')?.addEventListener('click', fillImageSelects);

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
