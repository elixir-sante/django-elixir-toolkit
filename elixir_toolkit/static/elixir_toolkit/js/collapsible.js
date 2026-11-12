// Blocs repliables ({% ui_collapsible %}) : repli à --collapsible-max-height si le contenu déborde,
// bouton « Afficher la suite / Réduire ». Sans JS, le contenu reste entièrement visible.

function setCollapsibleExpanded(block, expanded) {
    const toggle = block.querySelector('.collapsible-toggle');
    block.classList.toggle('is-collapsed', !expanded);
    toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    toggle.querySelector('.collapsible-toggle-label').textContent = expanded ? toggle.dataset.labelLess : toggle.dataset.labelMore;
}

function updateCollapsibles() {
    document.querySelectorAll('[data-collapsible]').forEach(block => {
        const toggle = block.querySelector('.collapsible-toggle');
        // Bloc déplié par l'utilisateur : ne pas le replier (resize, chargement des images)
        if (toggle.getAttribute('aria-expanded') === 'true') return;
        const content = block.querySelector('.collapsible-content');
        block.classList.add('is-collapsed');
        const overflows = content.scrollHeight > content.clientHeight + 1;
        block.classList.toggle('is-collapsed', overflows);
        toggle.classList.toggle('is-hidden', !overflows);
    });
}

function loadCollapsibles() {
    document.querySelectorAll('[data-collapsible]').forEach(block => {
        if (block.dataset.collapsibleBound) return;
        block.dataset.collapsibleBound = '1';

        block.querySelector('.collapsible-toggle').addEventListener('click', () => {
            setCollapsibleExpanded(block, block.classList.contains('is-collapsed'));
        });
        // Navigation clavier : un lien caché par le repli qui reçoit le focus déplie le bloc
        block.querySelector('.collapsible-content').addEventListener('focusin', () => {
            if (block.classList.contains('is-collapsed')) setCollapsibleExpanded(block, true);
        });
    });
    updateCollapsibles();
}

window.addEventListener('resize', updateCollapsibles);
// Les images et iframes changent la hauteur du contenu une fois chargées
window.addEventListener('load', updateCollapsibles);

document.addEventListener('DOMContentLoaded', loadCollapsibles);
