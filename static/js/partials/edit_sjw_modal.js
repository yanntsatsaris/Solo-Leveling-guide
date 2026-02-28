const panopliesList = [];
const artefactMainStats = {};
const secondaryStatsOptions = [];
const focusStatsOptions = [];
const coresList = [];
const coreMainStats = {};
const coreSecondaryStats = {};
let currentLang = 'FR-fr';

function initializeEditSjwModalData(data) {
    Object.assign(panopliesList, data.panopliesList || []);
    Object.assign(artefactMainStats, data.artefactMainStats || {});
    Object.assign(secondaryStatsOptions, data.secondaryStatsOptions || []);
    Object.assign(focusStatsOptions, data.focusStatsOptions || []);
    Object.assign(coresList, data.coresList || []);
    Object.assign(coreMainStats, data.coreMainStats || {});
    Object.assign(coreSecondaryStats, data.coreSecondaryStats || {});
    currentLang = data.currentLang || 'FR-fr';
}

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('edit-sjw-modal');
    const closeBtns = modal?.querySelectorAll('.close-modal, [data-close-modal]');
    const editBtn = document.getElementById('edit-sjw-btn');

    if (editBtn && modal) {
        editBtn.addEventListener('click', () => {
            modal.removeAttribute('hidden');
            modal.showModal();
            fillImageSelects();
        });
    }

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

    // Gestion des onglets
    document.querySelectorAll('#edit-sjw-modal .edit-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('#edit-sjw-modal .edit-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('#edit-sjw-modal .edit-tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const targetContent = document.getElementById('edit-sjw-modal').querySelector('#edit-tab-' + tab.dataset.tab);
            if (targetContent) targetContent.classList.add('active');
        });
    });

    // Sélecteur pour afficher le bon bloc de set à modifier dans l'onglet artefacts
    document.getElementById('edit-equipment-select')?.addEventListener('change', function(e) {
        const idx = this.value;
        document.querySelectorAll('.edit-eqset-block').forEach((block) => {
            block.style.display = (block.id === `eqset-block-${idx}`) ? 'block' : 'none';
        });
    });

    async function fillImageSelects() {
        const folder = document.querySelector('#edit-sjw-form input[name="folder"]').value;
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

        document.querySelectorAll('.skill-image-select, .gem-image-select, .gem-buff-image-select, .gem-debuff-image-select').forEach(select => {
            const current = select.dataset.current || "";
            fetch(`/SJW/skill_images?type=${encodeURIComponent(select.dataset.type)}&order=${encodeURIComponent(select.dataset.order)}`)
                .then(resp => resp.json())
                .then(images => {
                    select.innerHTML = ['<option value=""></option>']
                        .concat(images.map(img => `<option value="${img}"${img === current ? ' selected' : ''}>${img}</option>`)).join('');
                });
        });
    }

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
