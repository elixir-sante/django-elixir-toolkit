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

    // 4.1.2 : expose l'état de tri sur les en-têtes (aria-sort) + focus clavier (tabindex)
    function updateAriaSort($table) {
        $table.find('> thead th').each(function() {
            var $th = $(this);
            if ($th.attr('data-orderable') === 'false') {
                $th.removeAttr('aria-sort');
                return;
            }
            if ($th.hasClass('sort-asc')) {
                $th.attr('aria-sort', 'ascending');
            } else if ($th.hasClass('sort-desc')) {
                $th.attr('aria-sort', 'descending');
            } else {
                $th.attr('aria-sort', 'none');
            }
            if (!$th.attr('tabindex')) {
                $th.attr('tabindex', '0');
            }
        });
    }

    // Fonction pour initialiser tablesorter sur un conteneur
    function initTablesorter(container) {
        var $container = $(container || document);
        $container.find('[data-orderable="true"] table').filter(function() {
            // Vérifier si tablesorter n'est pas déjà initialisé sur cette table
            return !$(this).data('tablesorter');
        }).each(function() {
            var $table = $(this);
            $table.tablesorter(tablesorterConfig);
            $table.on('sortEnd', function() { updateAriaSort($table); });
            updateAriaSort($table);
        });
    }

    // Initialisation au chargement de la page
    $(document).ready(function() {
        initTablesorter();
    });

    document.addEventListener('htmx:afterSettle', function() {
        initTablesorter();
    });

})(jQuery);
