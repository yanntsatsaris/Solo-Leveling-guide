document.addEventListener("DOMContentLoaded", function() {
  // Ouvre la modale d'édition d'un core
  document.querySelectorAll('a[data-core-name]').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const color = this.getAttribute('data-core-name');
      // On récupère le numéro dans la même ligne du tableau
      const number = this.closest('tr').querySelector('td:nth-child(3)').textContent.trim();
      fetch(`/admin/cores/api/${encodeURIComponent(color)}/${number}`)
        .then(resp => resp.json())
        .then(data => {
          const langDiv = document.getElementById('edit-core-languages');
          langDiv.innerHTML = '';
          ['FR-fr', 'EN-en'].forEach(function(lang) {
            const effect = data[lang] || {};
            langDiv.innerHTML += `
              <fieldset>
                <legend>${lang}</legend>
                <label>Nom :</label>
                <input type="text" name="name_${lang}" value="${effect.name || ''}" required>
                <label>Effet :</label>
                <textarea name="effect_${lang}" class="effect-input">${effect.effect || ''}</textarea>
              </fieldset>
            `;
          });
          document.getElementById('edit-core-overlay').style.display = 'flex';
          document.getElementById('edit-core-form').action = `/admin/cores/${encodeURIComponent(color)}/${number}`;
          autoResizeAllTextareas();
        });
    });
  });

  // Fermer la modale en cliquant sur la croix
  document.getElementById('close-edit-core').onclick = function() {
    document.getElementById('edit-core-overlay').style.display = 'none';
  };

  // Fermer la modale en cliquant en dehors du menu
  document.getElementById('edit-core-overlay').addEventListener('mousedown', function(e) {
    if (e.target === this) {
      this.style.display = 'none';
    }
  });

  // Fermer la modale avec la touche Échap
  document.addEventListener('keydown', function(e) {
    if (e.key === "Escape") {
      document.getElementById('edit-core-overlay').style.display = 'none';
    }
  });

  // Création d'un nouveau core
  document.getElementById('create-core-btn').onclick = async function() {
    let color = prompt("Couleur du noyau ?");
    if (!color) return;

    // Vérifie la présence des 3 images
    let imgExists = await Promise.all([1,2,3].map(num => {
      let imgPath = `/static/images/Noyaux/${color}${String(num).padStart(2, "0")}.webp`;
      return fetch(imgPath, {method: "HEAD"}).then(r => r.ok).catch(() => false);
    }));

    if (!imgExists[0] && !imgExists[1] && !imgExists[2]) {
      // Aucune image, demande l'upload des 3
      showCoreUploadPopup(color, [1,2,3]);
      return;
    }

    // Au moins une image existe, demande le numéro
    let number = prompt("Numéro du noyau ? (01, 02 ou 03)");
    if (!number || !["01","02","03"].includes(number)) {
      alert("Numéro invalide.");
      return;
    }
    let numIdx = parseInt(number, 10);

    let imgPath = `/static/images/Noyaux/${color}${number}.webp`;
    let exists = await fetch(imgPath, {method: "HEAD"}).then(r => r.ok).catch(() => false);

    if (!exists) {
      // Image absente, demande l'upload de cette image uniquement
      showCoreUploadPopup(color, [numIdx]);
      return;
    }

    // Image présente, affiche le menu pour renseigner les infos de ce core
    showCoreInfoPopup(color, [numIdx]);
  };

  // Affiche le popup d'upload pour les numéros donnés
  function showCoreUploadPopup(color, nums) {
    let overlay = document.createElement('div');
    overlay.id = "upload-core-overlay";
    overlay.className = "edit-core-overlay";
    overlay.style.display = "flex";
    overlay.innerHTML = `
      <div class="edit-core-popup">
        <form id="upload-core-img-form" enctype="multipart/form-data">
          <h2>Uploader les images du noyau (${color})</h2>
          ${nums.map(num => `
            <div style="margin-bottom:12px;">
              <label>Image ${color}${String(num).padStart(2, "0")}.webp :</label>
              <input type="file" name="file_${num}" accept=".webp,.png,.jpg,.jpeg" required>
            </div>
          `).join('')}
          <input type="hidden" name="core_color" value="${color}">
          <input type="hidden" name="core_nums" value="${nums.join(',')}">
          <div style="margin-top:16px;">
            <button type="submit" class="admin-btn">Envoyer</button>
            <button type="button" id="cancel-upload-core" class="close-btn">&times;</button>
          </div>
        </form>
      </div>
    `;
    document.body.appendChild(overlay);

    document.getElementById('cancel-upload-core').onclick = function() {
      overlay.remove();
    };

    document.getElementById('upload-core-img-form').onsubmit = async function(e) {
      e.preventDefault();
      let formData = new FormData(this);
      let resp = await fetch('/admin/upload_core_images', {
        method: 'POST',
        body: formData
      });
      let txt = await resp.text();
      overlay.remove();
      if (!resp.ok) {
        alert(txt);
        return;
      }
      // Après upload, affiche le menu pour renseigner les infos des cores concernés
      let nums = this.core_nums.value.split(',').map(n => parseInt(n,10));
      showCoreInfoPopup(color, nums);
    };
  }

  // Affiche le menu pour renseigner les infos des cores concernés
  function showCoreInfoPopup(color, nums) {
    document.getElementById('edit-core-form').setAttribute('data-mode', 'create');
    const langDiv = document.getElementById('edit-core-languages');
    langDiv.innerHTML = '';
    nums.forEach(function(num) {
      ['FR-fr', 'EN-en'].forEach(function(lang) {
        langDiv.innerHTML += `
          <fieldset>
            <legend>${lang} - Noyau ${String(num).padStart(2,"0")}</legend>
            <label>Nom :</label>
            <input type="text" name="name_${lang}_${num}" value="" required>
            <label>Effet :</label>
            <textarea name="effect_${lang}_${num}" class="effect-input"></textarea>
          </fieldset>
        `;
      });
    });
    document.getElementById('edit-core-overlay').style.display = 'flex';
    document.getElementById('edit-core-form').action = `/admin/cores/${encodeURIComponent(color)}`;
    autoResizeAllTextareas();
  }

  // Soumission du formulaire de création (PUT)
  document.getElementById('edit-core-form').onsubmit = async function(e) {
    const mode = this.getAttribute('data-mode');
    if (mode === "edit") return; // édition classique (POST)
    e.preventDefault();
    const url = this.action;
    const names = {};
    const effects = {};
    document.querySelectorAll('#edit-core-languages fieldset').forEach(fs => {
      const lang = fs.querySelector('legend').textContent;
      names[lang] = fs.querySelector(`input[name="name_${lang}"]`).value;
      effects[lang] = fs.querySelector(`textarea[name="effect_${lang}"]`).value;
    });
    const resp = await fetch(url, {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({names, effects})
    });
    if (resp.ok) {
      location.reload();
    } else {
      alert("Erreur lors de la création du noyau.");
    }
  };
});
function autoResizeAllTextareas() {
  document.querySelectorAll("textarea.effect-input").forEach(function(el) {
    el.style.height = "auto";
    el.style.height = (el.scrollHeight) + "px";
  });
}
