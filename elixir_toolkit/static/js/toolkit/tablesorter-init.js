/**
 * Tablesorter initialization for Elixir Toolkit
 * Requires jQuery and tablesorter to be loaded first
 * Compatible with HTMX swaps
 */
(function($) {
    // Configuration pour tablesorter
    var tablesorterConfig = {
        theme: 'bulma',
        sortReset: true,
        sortRestart: true,
        widgets: ['zebra'],
        widgetZebra: {css: ['is-striped', 'is-striped']},
        headerTemplate: '{content}<span class="sort-icon"><i class="fas fa-sort"></i></span>',
        cssAsc: 'sort-asc',
        cssDesc: 'sort-desc',
        cssNone: 'sort-none',
        selectorHeaders: '> thead th[data-orderable!="false"]'
    };

    // Fonction pour initialiser tablesorter sur un conteneur
    function initTablesorter(container) {
        var $container = $(container || document);
        $container.find('[data-orderable="true"] table').filter(function() {
            // Vérifier si tablesorter n'est pas déjà initialisé sur cette table
            return !$(this).data('tablesorter');
        }).tablesorter(tablesorterConfig);
    }

    // Initialisation au chargement de la page
    $(document).ready(function() {
        initTablesorter();
    });

    document.body.addEventListener('htmx:afterSettle', function() {
        initTablesorter();
    });

})(jQuery);
