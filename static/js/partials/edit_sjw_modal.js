let panopliesList = [];
let artefactMainStats = {};
let secondaryStatsOptions = [];
let focusStatsOptions = [];
let coresList = [];
let coreMainStats = {};
let coreSecondaryStats = {};
let artefactTypeLabels = {};
let currentLang = "FR-fr";

function initializeEditSjwModalData(data) {
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
  const form = document.getElementById('edit-sjw-form');
  if (form) {
    function serializeForm(form) {
      const formData = new FormData(form);
      return Array.from(formData.entries()).sort();
    }
    document.getElementById('edit-sjw-btn')?.addEventListener('click', () => {
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
  const modal = document.getElementById('edit-sjw-modal');
  const closeBtn = document.querySelector("#edit-sjw-modal [data-close-modal]");
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

  // Ajout d'une arme
  document.getElementById('add-weapon-btn')?.addEventListener('click', async function() {
    const grid = document.querySelector('#edit-tab-weapons');
    if (!grid) return;
    const index = grid.querySelectorAll('.edit-weapon-block').length;
    let images = [];
    const folder = document.querySelector('#edit-sjw-form input[name="folder"]').value;
    if (folder) {
      try {
        images = await fetch(`/SJW/images_for/${encodeURIComponent(folder)}`).then(r => r.json());
      } catch (e) { images = []; }
    }
    const selectOptions = ['<option value=""></option>']
      .concat(images.map(img => `<option value="${img}">${img}</option>`)).join('');
    const div = document.createElement('div');
    div.className = 'edit-weapon-block';
    div.innerHTML = `
      <label>Nom de l'arme :</label>
      <input type="text" name="weapon_name_${index}" value="" />
      <label>Alias de l'arme :</label>
      <input type="text" name="weapon_alias_${index}" value="" />
      <label>Type :</label>
      <input type="text" name="weapon_type_${index}" value="" />
      <label>Stats :</label>
      <textarea name="weapon_stats_${index}"></textarea>
      <label>Tag :</label>
      <input type="text" name="weapon_tag_${index}" value="" />
      <label>Principal :</label>
      <input type="checkbox" name="weapon_principal_${index}" />
      <input type="hidden" name="weapon_id_${index}" value="">
      <h4 style="margin-top: 18px">Évolutions de l'arme</h4>
      <div class="evolutions-grid">
        ${Array.from({length: 7}).map((_, i) => `
          ${i % 2 === 0 ? '<div class="evolutions-row">' : ''}
          <div class="edit-weapon-evolution-block">
            <label>Évolution : ${i === 6 ? 'A6-10' : 'A' + i}</label>
            <textarea name="weapon_evolution_description_${index}_${i}"></textarea>
            <input type="hidden" name="weapon_evolutions_${index}_${i}_evolution_id" value="${i === 6 ? 'A6-10' : 'A' + i}">
            <input type="hidden" name="weapon_evolutions_id_${index}_${i}" value="">
          </div>
          ${(i % 2 === 1 || i === 6) ? '</div>' : ''}
        `).join('')}
      </div>
      <hr />
    `;
    grid.appendChild(div);
  });

  async function fillImageSelects() {
    const folder = document.querySelector('#edit-sjw-form input[name="folder"]')?.value;
    let images = [];
    if (folder) {
      try {
        images = await fetch(`/SJW/images_for/${encodeURIComponent(folder)}`).then(r => r.json());
      } catch (e) { images = []; }
    }
    document.querySelectorAll('.blessing-image-select').forEach(select => {
      const current = select.dataset.current || "";
      select.innerHTML = ['<option value=""></option>']
        .concat(images.map(img => `<option value="${img}"${img === current ? ' selected' : ''}>${img}</option>`)).join('');
    });
  }

  document.querySelectorAll('.skill-image-select, .gem-image-select, .gem-buff-image-select, .gem-debuff-image-select').forEach(select => {
      const current = select.dataset.current || "";
      fetch(`/SJW/skill_images?type=${encodeURIComponent(select.dataset.type)}&order=${encodeURIComponent(select.dataset.order)}`)
          .then(resp => resp.json())
          .then(images => {
              select.innerHTML = ['<option value=""></option>']
                  .concat(images.map(img => `<option value="${img}"${img === current ? ' selected' : ''}>${img}</option>`)).join('');
          });
  });

  document.getElementById('edit-sjw-btn')?.addEventListener('click', fillImageSelects);

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
