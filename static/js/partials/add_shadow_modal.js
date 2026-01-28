function initializeAddShadowModal() {
    const modal = document.getElementById('add-shadow-modal');
    const closeBtn = document.querySelector('.close-add-shadow');
    const addShadowBtn = document.getElementById('add-shadow-btn');
    const form = document.getElementById('add-shadow-form');

    if (addShadowBtn) {
        addShadowBtn.addEventListener('click', async function() {
            const name = prompt("Nom de l'ombre :");
            if (!name) return;
            const alias = prompt("Alias de l'ombre :");
            if (!alias) return;

            const aliasFolder = alias.replace(/ /g, "_");
            const folderName = `Shadow_${aliasFolder}`;

            let folderExists = false;
            try {
                const resp = await fetch(`/SJW/add_shadow/check_image_folder_shadow?alias=${encodeURIComponent(alias)}`);
                folderExists = (await resp.json()).exists;
            } catch (e) {
                folderExists = false;
            }

            if (modal) modal.showModal();

            document.querySelector('#add-shadow-form input[name="name"]').value = name;
            document.querySelector('#add-shadow-form input[name="alias"]').value = alias;

            if (!folderExists) {
                let uploadOverlay = document.createElement('dialog');
                uploadOverlay.id = "upload-shadow-images-overlay";
                uploadOverlay.className = "edit-shadow-content";
                uploadOverlay.innerHTML = `
                    <form id="upload-shadow-images-form" enctype="multipart/form-data">
                        <h2>Uploader les images de l'ombre (.zip)</h2>
                        <input type="file" name="images_zip" accept=".zip" required>
                        <input type="hidden" name="alias" value="${alias}">
                        <div style="margin-top:16px; display:flex; justify-content: space-between;">
                            <button type="submit" class="admin-btn">Envoyer</button>
                            <button type="button" id="cancel-upload-shadow-images" class="close-btn">&times;</button>
                        </div>
                    </form>
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
        });
    }

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
}

document.addEventListener('DOMContentLoaded', () => {
    // Basic tab switching for add shadow modal
    document.querySelectorAll('#add-shadow-modal .edit-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('#add-shadow-modal .edit-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('#add-shadow-modal .edit-tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const targetContent = document.getElementById('add-shadow-modal').querySelector('#edit-tab-' + tab.dataset.tab);
            if (targetContent) targetContent.classList.add('active');
        });
    });
});
