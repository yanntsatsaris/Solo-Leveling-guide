function showGemTooltip(idx) {
  const tooltip = document.getElementById("gem-tooltip-" + idx);
  if (tooltip) tooltip.style.display = "block";
}

function hideGemTooltip(idx) {
  const tooltip = document.getElementById("gem-tooltip-" + idx);
  if (tooltip) tooltip.style.display = "none";
}
