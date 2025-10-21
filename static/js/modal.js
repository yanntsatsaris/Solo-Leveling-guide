function initializeModal(openButtonId, overlayId, closeButtonId) {
    const openBtn = document.getElementById(openButtonId);
    const overlay = document.getElementById(overlayId);
    const closeBtn = document.getElementById(closeButtonId);

    if (openBtn && overlay) {
        openBtn.onclick = function () {
            overlay.style.display = "flex";
        };
    }
    if (closeBtn && overlay) {
        closeBtn.onclick = function () {
            overlay.style.display = "none";
        };
    }
}
