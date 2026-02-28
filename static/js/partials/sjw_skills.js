document.addEventListener("DOMContentLoaded", function() {
    const innerTabBtns = document.querySelectorAll('.sjw-inner-tab-btn');
    const innerTabContents = document.querySelectorAll('.sjw-inner-tab-content');
    const infoBubble = document.getElementById('sjw-info-bubble');
    const gemsBubble = document.getElementById('sjw-gems-bubble');
    const gemsBubbleList = document.getElementById('sjw-gems-bubble-list');

    if (!innerTabBtns.length) return;

    innerTabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            innerTabBtns.forEach(b => b.classList.remove('active'));
            innerTabContents.forEach(tc => tc.classList.remove('active'));
            this.classList.add('active');
            const target = document.getElementById('sjw-inner-tab-' + this.dataset.innerTab);
            if (target) {
                target.classList.add('active');
                updateSkillHoverListeners();
                initSkillInteractions();
            }
        });
    });

    function updateSkillHoverListeners() {
        const activeContent = document.querySelector('.sjw-inner-tab-content.active');
        if (!activeContent || !infoBubble) return;
        const skillCells = activeContent.querySelectorAll('.sjw-skill-cell');
        const activeTab = document.querySelector('.sjw-inner-tab-btn.active').dataset.innerTab;
        const skillsData = (window.allSkillsData || []).filter(s => s.type === activeTab);

        skillCells.forEach((cell, idx) => {
            cell.onmouseenter = function(e) {
                const skill = skillsData[idx];
                if (skill) {
                    infoBubble.innerHTML = `
                        <strong>${skill.name || ''}</strong><br>
                        <span>${skill.description || ''}</span>
                    `;
                    infoBubble.style.display = "block";
                    infoBubble.style.opacity = "1";
                    positionBubble(infoBubble, e);
                }
            };
            cell.onmousemove = function(e) {
                positionBubble(infoBubble, e);
            };
            cell.onmouseleave = function() {
                infoBubble.style.display = "none";
                infoBubble.style.opacity = "0";
            };
        });
    }

    function initSkillInteractions() {
        const activeContent = document.querySelector('.sjw-inner-tab-content.active');
        if (!activeContent || !gemsBubble || !gemsBubbleList) return;
        const skillCells = activeContent.querySelectorAll('.sjw-skill-clickable');
        const allSkillsData = window.allSkillsData || [];

        skillCells.forEach(cell => {
            cell.onclick = function(event) {
                const activeTab = document.querySelector('.sjw-inner-tab-btn.active').dataset.innerTab;
                const skillsData = allSkillsData.filter(s => s.type === activeTab);
                const idx = parseInt(cell.dataset.skillIndex);
                const skill = skillsData[idx];
                gemsBubbleList.innerHTML = '';
                if (skill && skill.gems) {
                    skill.gems.forEach((gem, gemIdx) => {
                        if (gem.image_path) {
                            const img = document.createElement('img');
                            img.src = "/static/" + gem.image_path;
                            img.className = "sjw-gem-bubble-img";
                            img.alt = "Gem Image";
                            img.dataset.gemIdx = gemIdx;
                            gemsBubbleList.appendChild(img);
                        }
                    });

                    const rect = cell.getBoundingClientRect();
                    const bubbleWidth = gemsBubble.offsetWidth || 120;
                    const bubbleHeight = gemsBubble.offsetHeight || 200;
                    let leftPosition = rect.left + window.scrollX - bubbleWidth - 16;
                    if (leftPosition < 0) {
                        leftPosition = rect.right + window.scrollX + 16;
                    }
                    let topPosition = rect.top + window.scrollY + (rect.height / 2) - (bubbleHeight / 2);
                    if (topPosition < 0) topPosition = 10;
                    gemsBubble.style.top = `${topPosition}px`;
                    gemsBubble.style.left = `${leftPosition}px`;
                    gemsBubble.style.display = "flex";
                    updateGemHoverListeners(skill);
                }
            };
        });
    }

    function updateGemHoverListeners(skill) {
        if (!infoBubble) return;
        const gemImgs = document.querySelectorAll('.sjw-gem-bubble-img');
        gemImgs.forEach(img => {
            img.onmouseenter = function(e) {
                const gemIdx = parseInt(img.dataset.gemIdx);
                const gem = skill.gems[gemIdx];
                if (gem) {
                    infoBubble.innerHTML = `
                        <strong>${gem.name || ''}</strong><br>
                        <span>${gem.description || ''}</span>
                    `;
                    infoBubble.style.display = "block";
                    infoBubble.style.opacity = "1";
                    positionBubble(infoBubble, e);
                }
            };
            img.onmousemove = function(e) {
                positionBubble(infoBubble, e);
            };
            img.onmouseleave = function() {
                infoBubble.style.display = "none";
                infoBubble.style.opacity = "0";
            };
        });
    }

    function positionBubble(bubble, e) {
        bubble.style.left = (e.clientX + 18) + "px";
        bubble.style.top = (e.clientY + 18) + "px";
    }

    // Initial check
    updateSkillHoverListeners();
    initSkillInteractions();

    document.addEventListener('click', function(e) {
        if (gemsBubble && !e.target.closest('.sjw-skill-clickable') && !e.target.closest('#sjw-gems-bubble')) {
            gemsBubble.style.display = "none";
        }
    });
});
