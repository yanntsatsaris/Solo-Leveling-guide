function initializeModal(openButtonId, dialogId, closeButtonId) {
    const openBtn = document.getElementById(openButtonId);
    const dialog = document.getElementById(dialogId);
    const closeBtn = document.getElementById(closeButtonId);

    if (openBtn && dialog) {
        openBtn.addEventListener('click', () => {
            dialog.showModal();
        });
    }

    if (closeBtn && dialog) {
        closeBtn.addEventListener('click', () => {
            dialog.close();
        });
    }

    // Ferme la modale si on clique en dehors
    if (dialog) {
        dialog.addEventListener('click', (event) => {
            if (event.target === dialog) {
                dialog.close();
            }
        });
    }
}
