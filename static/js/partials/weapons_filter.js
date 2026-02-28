document.addEventListener("DOMContentLoaded", () => {
  const typeButtons = document.querySelectorAll(".weapon-type-button");
  const rarityButtons = document.querySelectorAll(".weapon-rarity-button");
  const weaponCells = document.querySelectorAll("#weapons-table td");

  if (!weaponCells.length) return;

  let selectedType = "All";
  let selectedRarity = "All";

  function filterWeapons() {
    weaponCells.forEach((cell) => {
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
      typeButtons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      selectedType = button.getAttribute("data-type");
      filterWeapons();
    });
  });

  rarityButtons.forEach((button) => {
    button.addEventListener("click", () => {
      rarityButtons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      selectedRarity = button.getAttribute("data-rarity");
      filterWeapons();
    });
  });
});
