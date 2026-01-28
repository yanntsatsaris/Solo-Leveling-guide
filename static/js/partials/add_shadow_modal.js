document.addEventListener("DOMContentLoaded", () => {
    // Selectors
    const modal = document.getElementById('add-shadow-modal');
    const closeBtn = document.querySelector('#add-shadow-modal [data-close-modal]');
    const addShadowBtn = document.getElementById('add-shadow-btn');
    const addShadowForm = document.getElementById('add-shadow-form');

    // Fermeture de la modale
    if (closeBtn && modal) {
        closeBtn.onclick = function() {
            modal.close();
        };
    }

    // Ferme la modale si clic en dehors du popup
    if (modal) {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.close();
            }
        });
    }

    if (addShadowBtn) {
        addShadowBtn.onclick = async function() {
            // Demande les infos de base
            const name = prompt("Nom de l'ombre :");
            if (!name) return;
            const alias = prompt("Alias de l'ombre :");
            if (!alias) return;

            // Construit le chemin du dossier image
            const aliasFolder = alias.replace(/ /g, "_");
            const folderName = `Shadow_${aliasFolder}`;

            // Vérifie si le dossier existe côté serveur
            let folderExists = false;
            try {
                const resp = await fetch(`/SJW/add_shadow/check_image_folder_shadow?alias=${encodeURIComponent(alias)}`);
                const data = await resp.json();
                folderExists = data.exists;
            } catch (e) {
                folderExists = false;
            }

            // Ouvre la modale d'ajout
            if (modal) modal.showModal();

            // Pré-remplit les champs
            if (addShadowForm) {
                addShadowForm.querySelector('input[name="name"]').value = name;
                addShadowForm.querySelector('input[name="alias"]').value = alias;
            }

            // Optionnel : affiche une alerte si le dossier n'existe pas
            if (!folderExists) {
                let uploadOverlay = document.createElement('dialog');
                uploadOverlay.id = "upload-shadow-images-overlay";
                uploadOverlay.className = "edit-shadow-popup";
                uploadOverlay.innerHTML = `
                  <article>
                    <form id="upload-shadow-images-form" enctype="multipart/form-data">
                        <h2>Uploader les images de l'ombre (.zip)</h2>
                        <input type="file" name="images_zip" accept=".zip" required>
                        <input type="hidden" name="alias" value="${alias}">
                        <div style="margin-top:16px; display: flex; justify-content: space-between;">
                            <button type="submit" class="admin-btn">Envoyer</button>
                            <button type="button" id="cancel-upload-shadow-images" class="close-btn">&times;</button>
                        </div>
                    </form>
                  </article>
                `;
                document.body.appendChild(uploadOverlay);
                uploadOverlay.showModal();

                document.getElementById('cancel-upload-shadow-images').onclick = function() {
                    uploadOverlay.close();
                    uploadOverlay.remove();
                };

                document.getElementById('upload-shadow-images-form').onsubmit = async function(e) {
                    e.preventDefault();
                    let formData = new FormData(this);
                    let resp = await fetch('/admin/upload_shadow_images_zip', {
                        method: 'POST',
                        body: formData
                    });
                    let txt = await resp.text();
                    uploadOverlay.close();
                    uploadOverlay.remove();
                    alert(txt);
                };
            }
        };
    }
});
