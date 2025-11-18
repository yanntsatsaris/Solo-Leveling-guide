document.addEventListener("DOMContentLoaded", () => {
    const typeButtons = document.querySelectorAll(".type-button");
    const rarityButtons = document.querySelectorAll(".rarity-button");
    const characterCells = document.querySelectorAll("#character-table td");

    let selectedType = "All";
    let selectedRarity = "All";

    function filterCharacters() {
        characterCells.forEach((cell) => {
            const matchesType =
                selectedType === "All" ||
                cell.getAttribute("data-type") === selectedType;
            const matchesRarity =
                selectedRarity === "All" ||
                cell.getAttribute("data-rarity") === selectedRarity;
            cell.style.display = matchesType && matchesRarity ? "" : "none";
        });
    }

    typeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            selectedType = button.getAttribute("data-type");
            filterCharacters();
        });
    });

    rarityButtons.forEach((button) => {
        button.addEventListener("click", () => {
            selectedRarity = button.getAttribute("data-rarity");
            filterCharacters();
        });
    });
});
