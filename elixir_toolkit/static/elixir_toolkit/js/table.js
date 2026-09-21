// Gestion des lignes expandables dans les tableaux
function setupTableExpandables() {
    // Helper pour toggler une ligne de détails
    function toggleDetails(targetId, iconElement, textSpan, rowElement) {
        const detailsRow = document.getElementById(targetId);
        if (!detailsRow) return;

        const isHidden = detailsRow.style.display === 'none' || detailsRow.style.display === '';
        detailsRow.style.display = isHidden ? 'table-row' : 'none';

        if (iconElement) {
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
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const row = this.closest('.table-row-expandable');
            const icon = this.querySelector('.fa-chevron-down, .fa-chevron-up');
            const textSpan = this.querySelector('span:not(.icon)');
            toggleDetails(targetId, icon, textSpan, row);
        });
    });

    // Clic sur toute la ligne pour expand/collapse
    document.querySelectorAll('.table-row-expandable').forEach(row => {
        row.addEventListener('click', function(e) {
            // Ne pas déclencher si on a cliqué sur le bouton
            if (e.target.closest('.expand-toggle')) return;

            const targetId = this.getAttribute('data-target');
            const button = this.querySelector('.expand-toggle');
            const icon = button.querySelector('.fa-chevron-down, .fa-chevron-up');
            const textSpan = button.querySelector('span:not(.icon)');
            toggleDetails(targetId, icon, textSpan, this);
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
