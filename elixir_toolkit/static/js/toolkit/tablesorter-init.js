/**
 * Tablesorter initialization for Elixir Toolkit
 * Requires jQuery and tablesorter to be loaded first
 */
(function($) {
    $(document).ready(function() {
        // Initialize tablesorter on tables inside a container with data-orderable="true"
        $('[data-orderable="true"] table').tablesorter({
            theme: 'bulma',
            sortReset: true,
            sortRestart: true,
            widgets: ['zebra'],
            widgetZebra: {css: ['is-striped', 'is-striped']},
            headerTemplate: '{content}<span class="sort-icon"><i class="fas fa-sort"></i></span>',
            cssAsc: 'sort-asc',
            cssDesc: 'sort-desc',
            cssNone: 'sort-none',
            selectorHeaders: '> thead th'
        });
    });
})(jQuery);
