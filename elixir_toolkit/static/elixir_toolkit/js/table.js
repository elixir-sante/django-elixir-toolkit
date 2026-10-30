// Gestion des lignes expandables dans les tableaux
function setupTableExpandables() {
    // Helper pour toggler une ligne de détails
    function toggleDetails(targetId, iconElement, textSpan, rowElement, button) {
        const detailsRow = document.getElementById(targetId);
        if (!detailsRow) return;

        const isHidden = !detailsRow.classList.contains('is-expanded');
        detailsRow.classList.toggle('is-expanded', isHidden);
        detailsRow.style.display = isHidden ? 'table-row' : 'none';

        // 4.1.2 : état exposé sur le bouton (aria-expanded / aria-controls)
        if (button) {
            button.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
        }

        if (iconElement) {
            iconElement.setAttribute('aria-hidden', 'true');
            iconElement.classList.toggle('fa-chevron-down', !isHidden);
            iconElement.classList.toggle('fa-chevron-up', isHidden);
        }

        if (textSpan) {
            textSpan.textContent = isHidden ? 'Masquer' : 'Détails';
        }

        // Toggle la classe is-selected sur la ligne pour indiquer qu'elle est expandée
        if (rowElement) {
            rowElement.classList.toggle('is-selected', isHidden);
        }
    }

    // Toggle pour les lignes expandables (clic sur le bouton)
    document.querySelectorAll('.expand-toggle').forEach(button => {
        // 4.1.2 : état initial exposé
        const targetId = button.dataset.target;
        if (targetId) {
            button.setAttribute('aria-controls', targetId);
            if (!button.hasAttribute('aria-expanded')) {
                button.setAttribute('aria-expanded', 'false');
            }
        }
        if (button.dataset.bound) return;
        button.dataset.bound = '1';
        button.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const row = this.closest('.table-row-expandable');
            const icon = this.querySelector('.fa-chevron-down, .fa-chevron-up');
            const textSpan = this.querySelector('span:not(.icon)');
            toggleDetails(targetId, icon, textSpan, row, this);
        });
    });

    // Clic sur toute la ligne pour expand/collapse (redondant avec le bouton,
    // qui lui est accessible au clavier — 2.1.1)
    document.querySelectorAll('.table-row-expandable').forEach(row => {
        if (row.dataset.bound) return;
        row.dataset.bound = '1';
        row.addEventListener('click', function(e) {
            // Ne pas déclencher si on a cliqué sur le bouton
            if (e.target.closest('.expand-toggle')) return;

            const targetId = this.dataset.target;
            const button = this.querySelector('.expand-toggle');
            if (!button) return;
            const icon = button.querySelector('.fa-chevron-down, .fa-chevron-up');
            const textSpan = button.querySelector('span:not(.icon)');
            toggleDetails(targetId, icon, textSpan, this, button);
        });

        // Empêcher la propagation du clic sur les éléments interactifs dans la ligne
        row.querySelectorAll('a, button, input, select, textarea').forEach(el => {
            el.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });
    });
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', setupTableExpandables);

// Ré-initialisation après chaque settlement HTMX
document.addEventListener('htmx:afterSettle', setupTableExpandables);
