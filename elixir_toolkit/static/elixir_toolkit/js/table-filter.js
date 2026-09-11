/**
 * Filtrage de tableau avec jQuery
 * Utilisation: 
 * 1. Ajouter data-filterable="true" sur le conteneur du tableau
 * 2. Ajouter data-filter-columns="0,1,2" pour spécifier les colonnes à filtrer (index 0-based)
 * 3. Ajouter data-filter-target="#mon-input" pour lier à un champ de formulaire
 * 4. Ou utiliser la classe .table-filter sur l'input et data-filter-id="mon-id" sur le tableau
 */

(function($) {
    'use strict';

    /**
     * Normalise une chaîne en supprimant les accents et en mettant en minuscules
     */
    function normalizeString(str) {
        if (!str) return '';
        return str
            .normalize('NFD')  // Décompose les caractères accentués
            .replace(/[\u0300-\u036f]/g, '')  // Supprime les diacritiques
            .toLowerCase();
    }

    // Initialisation automatique au chargement
    $(document).ready(function() {
        initTableFilters();
        
        // Support HTMX : réinitialiser les filtres après un settle
        if (typeof htmx !== 'undefined') {
            htmx.onLoad(function(content) {
                // Réinitialiser les filtres pour le contenu chargé
                initTableFiltersForContainer($(content));
            });
            
            // Écouter les événements afterSettle pour les requêtes HTMX
            document.addEventListener('htmx:afterSettle', function(evt) {
                initTableFiltersForContainer($(evt.detail.elt));
            });
        }
    });

    /**
     * Réinitialise les filtres pour un conteneur spécifique
     */
    function initTableFiltersForContainer($container) {
        // Trouver les conteneurs filterable dans le conteneur donné
        $container.find('[data-filterable="true"]').each(function() {
            var $thisContainer = $(this);
            
            // Éviter de réinitialiser si déjà fait
            if ($thisContainer.data('table-filters-initialized')) {
                return;
            }
            
            var filterSelector = $thisContainer.attr('data-filter-target');
            var columnsAttr = $thisContainer.attr('data-filter-columns');
            
            if (filterSelector) {
                // Support des sélecteurs multiples séparés par des virgules
                var selectors = filterSelector.split(',').map(s => s.trim());
                var $filterInputs = $();
                
                selectors.forEach(function(selector) {
                    var $input = $(selector);
                    if ($input.length) {
                        $filterInputs = $filterInputs.add($input);
                    }
                });
                
                if ($filterInputs.length > 0) {
                    // Marquer comme non initialisé pour permettre la réinitialisation
                    $thisContainer.removeData('table-filters-initialized');
                    setupMultiTableFilter($thisContainer, $filterInputs, columnsAttr);
                    $thisContainer.data('table-filters-initialized', true);
                }
            }
        });
        
        // Méthode 2: Filtre via classe .table-filter et data-filter-id
        $container.find('.table-filter').each(function() {
            var $filterInput = $(this);
            var filterId = $filterInput.attr('data-filter-id') || $filterInput.attr('id');
            var $targetContainer = $container.find('[data-filterable="true"][data-filter-id="' + filterId + '"]');
            var columnsAttr = $targetContainer.attr('data-filter-columns');
            
            if ($targetContainer.length) {
                // Marquer comme non initialisé pour permettre la réinitialisation
                $targetContainer.removeData('table-filters-initialized');
                
                // Vérifier s'il y a déjà un filtre configuré pour ce conteneur
                var existingFilters = $targetContainer.data('table-filters') || $();
                if (existingFilters.length === 0 || !existingFilters.is($filterInput)) {
                    existingFilters = existingFilters.add($filterInput);
                    $targetContainer.data('table-filters', existingFilters);
                    
                    if (existingFilters.length === 1) {
                        // Premier filtre pour ce conteneur
                        setupMultiTableFilter($targetContainer, existingFilters, columnsAttr);
                        $targetContainer.data('table-filters-initialized', true);
                    }
                }
            }
        });
    }

    /**
     * Initialise tous les filtres de tableau sur la page
     */
    function initTableFilters() {
        // Méthode 1: Filtre lié via data-filter-target (peut être multiple, séparés par des virgules)
        $('[data-filterable="true"]').each(function() {
            var $container = $(this);
            var filterSelector = $container.attr('data-filter-target');
            var columnsAttr = $container.attr('data-filter-columns');
            
            if (filterSelector) {
                // Support des sélecteurs multiples séparés par des virgules
                var selectors = filterSelector.split(',').map(s => s.trim());
                var $filterInputs = $();
                
                selectors.forEach(function(selector) {
                    var $input = $(selector);
                    if ($input.length) {
                        $filterInputs = $filterInputs.add($input);
                    }
                });
                
                if ($filterInputs.length > 0) {
                    setupMultiTableFilter($container, $filterInputs, columnsAttr);
                }
            }
        });

        // Méthode 2: Filtre via classe .table-filter et data-filter-id
        $('.table-filter').each(function() {
            var $filterInput = $(this);
            var filterId = $filterInput.attr('data-filter-id') || $filterInput.attr('id');
            var $container = $('[data-filterable="true"][data-filter-id="' + filterId + '"]');
            var columnsAttr = $container.attr('data-filter-columns');
            
            if ($container.length) {
                // Vérifier s'il y a déjà un filtre configuré pour ce conteneur
                var existingFilters = $container.data('table-filters') || $();
                if (existingFilters.length === 0 || !existingFilters.is($filterInput)) {
                    existingFilters = existingFilters.add($filterInput);
                    $container.data('table-filters', existingFilters);
                    
                    if (existingFilters.length === 1) {
                        // Premier filtre pour ce conteneur
                        setupMultiTableFilter($container, existingFilters, columnsAttr);
                    }
                }
            }
        });
    }

    /**
     * Configure le filtrage pour un tableau spécifique (version simple avec un seul champ)
     */
    function setupTableFilter($container, $filterInput, columnsAttr) {
        var columns = parseColumns(columnsAttr);
        var $table = $container.find('table');
        
        // Gestion de l'événement input (pour la saisie en temps réel)
        $filterInput.on('input', function() {
            filterTable($table, $(this).val(), columns);
        });

        // Gestion de l'événement change (pour les selects, etc.)
        $filterInput.on('change', function() {
            filterTable($table, $(this).val(), columns);
        });

        // Gestion de l'événement keyup (pour la touche Escape, etc.)
        $filterInput.on('keyup', function(e) {
            if (e.key === 'Escape') {
                $(this).val('');
                filterTable($table, '', columns);
            }
        });
        
        // Appliquer le filtre initial avec la valeur déjà présente dans le champ
        filterTable($table, $filterInput.val(), columns);
    }

    /**
     * Configure le filtrage pour un tableau avec plusieurs champs (logique ET)
     * Chaque champ peut spécifier sur quelle colonne filtrer via data-filter-column
     */
    function setupMultiTableFilter($container, $filterInputs, columnsAttr) {
        var columns = parseColumns(columnsAttr);
        var $table = $container.find('table');
        
        // Stocker les valeurs des filtres avec leur colonne associée
        var filterConfig = {};
        
        // Pour les checkboxes, stocker aussi toutes les valeurs possibles de chaque groupe
        var checkboxGroupValues = {};
        
        // D'abord, collecter UNIQUEMENT les groupes de checkboxes (ceux qui ont plusieurs éléments avec le même name)
        $filterInputs.filter('[type="checkbox"]').each(function() {
            var name = $(this).attr('name') || 'filter_' + $filterInputs.index(this);
            // Vérifier si c'est un groupe (plusieurs checkboxes avec le même name)
            var isGroup = $('[name="' + name + '"]').length > 1;
            if (isGroup && !checkboxGroupValues[name]) {
                checkboxGroupValues[name] = {
                    allValues: [],
                    checkedValues: []
                };
            }
        });
        
        // Collecter toutes les valeurs possibles pour chaque groupe de checkboxes
        for (var name in checkboxGroupValues) {
            $('[name="' + name + '"]').each(function() {
                var normalizedValue = normalizeString($(this).val());
                checkboxGroupValues[name].allValues.push(normalizedValue);
                if ($(this).is(':checked')) {
                    checkboxGroupValues[name].checkedValues.push(normalizedValue);
                }
            });
        }
        
        // Configurer chaque champ de filtre
        $filterInputs.each(function(index) {
            var $input = $(this);
            var filterName = $input.attr('name') || 'filter_' + index;
            var filterColumn = $input.attr('data-filter-column'); // Quelle colonne ce filtre contrôle
            
            // Pour les checkboxes, la valeur initiale dépend de l'état coché
            var initialValue = $input.is('[type="checkbox"]') && !$input.is(':checked') ? '' : $input.val();
            
            // Stocker la configuration
            filterConfig[filterName] = {
                column: filterColumn ? parseInt(filterColumn, 10) : null,
                value: initialValue,
                isCheckbox: $input.is('[type="checkbox"]'),
                isSingleCheckbox: $input.is('[type="checkbox"]') && $('[name="' + filterName + '"]').length === 1
            };
            
            // Stocker le nom directement dans les données de l'élément
            $input.data('filter-name', filterName);
            
            // Gestion différente pour les checkboxes
            if ($input.is('[type="checkbox"]')) {
                // Vérifier si c'est une checkbox unique (pas de groupe)
                var isSingleCheckbox = $('[name="' + filterName + '"]').length === 1;
                
                // Gestion de l'événement change pour les checkboxes
                $input.on('change', function() {
                    var name = $(this).data('filter-name');
                    
                    if (isSingleCheckbox) {
                        // Pour une checkbox unique, traiter comme un filtre classique
                        // Si cochée, utiliser sa valeur, sinon valeur vide
                        filterConfig[name].value = $(this).is(':checked') ? $(this).val() : '';
                    } else {
                        // Pour les checkboxes de groupe, mettre à jour la valeur dans filterConfig
                        // Si au moins une checkbox du groupe est cochée, on garde la valeur, sinon on met vide
                        var anyChecked = false;
                        $('[name="' + name + '"]').each(function() {
                            if ($(this).is(':checked')) {
                                anyChecked = true;
                                return false;
                            }
                        });
                        filterConfig[name].value = anyChecked ? $(this).val() : '';
                        
                        // Mettre à jour les valeurs cochées pour ce groupe
                        var checkedValues = [];
                        $('[name="' + name + '"]').each(function() {
                            if ($(this).is(':checked')) {
                                checkedValues.push(normalizeString($(this).val()));
                            }
                        });
                        checkboxGroupValues[name].checkedValues = checkedValues;
                    }
                    
                    filterTableMulti($table, filterConfig, columns, checkboxGroupValues);
                });
            } else {
                // Gestion de l'événement input
                $input.on('input', function() {
                    var name = $(this).data('filter-name');
                    filterConfig[name].value = $(this).val();
                    filterTableMulti($table, filterConfig, columns, checkboxGroupValues);
                });

                // Gestion de l'événement change
                $input.on('change', function() {
                    var name = $(this).data('filter-name');
                    filterConfig[name].value = $(this).val();
                    filterTableMulti($table, filterConfig, columns, checkboxGroupValues);
                });

                // Gestion de l'événement keyup (pour Escape)
                $input.on('keyup', function(e) {
                    if (e.key === 'Escape') {
                        var name = $(this).data('filter-name');
                        $(this).val('');
                        filterConfig[name].value = '';
                        filterTableMulti($table, filterConfig, columns, checkboxGroupValues);
                    }
                });
            }
        });
        
        // Appliquer le filtre initial avec les valeurs déjà présentes dans les champs
        filterTableMulti($table, filterConfig, columns, checkboxGroupValues);
    }

    /**
     * Parse les colonnes à filtrer
     */
    function parseColumns(columnsAttr) {
        if (!columnsAttr) {
            // Par défaut, filtrer sur toutes les colonnes
            return null;
        }
        
        // Convertir en tableau d'index numériques
        var columns = columnsAttr.split(',').map(function(col) {
            return parseInt(col.trim(), 10);
        });
        
        return columns;
    }

    /**
     * Filtre les lignes du tableau (version simple avec un seul filtre)
     */
    function filterTable($table, filterValue, columns) {
        var $rows = $table.find('tbody tr');
        var searchTerm = normalizeString(filterValue);

        if (searchTerm === '') {
            // Si le filtre est vide, afficher toutes les lignes
            $rows.show();
            return;
        }

        $rows.each(function() {
            var $row = $(this);
            var $cells = $row.find('td');
            var isVisible = false;

            // Vérifier d'abord l'attribut data-search sur la ligne
            var rowSearchData = $row.attr('data-search');
            if (rowSearchData) {
                var rowSearchText = normalizeString(rowSearchData);
                if (rowSearchText.includes(searchTerm)) {
                    isVisible = true;
                }
            }

            // Si pas encore visible, vérifier les cellules
            if (!isVisible) {
                // Si columns n'est pas spécifié, vérifier toutes les cellules
                if (columns === null) {
                    $cells.each(function() {
                        var cellText = normalizeString($(this).text());
                        if (cellText.includes(searchTerm)) {
                            isVisible = true;
                            return false; // Sortir de la boucle each
                        }
                    });
                } else {
                    // Vérifier uniquement les colonnes spécifiées
                    for (var i = 0; i < columns.length; i++) {
                        var colIndex = columns[i];
                        if (colIndex >= 0 && colIndex < $cells.length) {
                            var cellText = normalizeString($cells.eq(colIndex).text());
                            if (cellText.includes(searchTerm)) {
                                isVisible = true;
                                break;
                            }
                        }
                    }
                }
            }

            $row.toggle(isVisible);
        });
    }

    /**
     * Filtre les lignes du tableau avec plusieurs valeurs de filtre
     * - Logique ET entre les différents types de filtres (textes, selects)
     * - Logique OU entre les checkboxes du même groupe (au moins une case cochée doit matcher)
     * - Si toutes les cases d'un groupe sont cochées, le filtre pour ce groupe est désactivé
     */
    function filterTableMulti($table, filterConfig, columns, checkboxGroupValues) {
        var $rows = $table.find('tbody tr');
        
        // Séparer les filtres en deux catégories : checkboxes (groupes) et autres (y compris checkboxes uniques)
        var otherFilters = {};
        var checkboxGroupFilters = {};
        
        for (var key in filterConfig) {
            var config = filterConfig[key];
            
            // Les checkboxes uniques sont traitées comme des filtres classiques
            if (config.isSingleCheckbox) {
                if (config.value && config.value.trim() !== '') {
                    otherFilters[key] = config;
                }
            }
            // Les checkboxes de groupe sont traitées séparément
            else if (config.isCheckbox && !config.isSingleCheckbox) {
                checkboxGroupFilters[key] = config;
            }
            // Les autres types de filtres (text, select, etc.)
            else if (!config.isCheckbox && config.value && config.value.trim() !== '') {
                otherFilters[key] = config;
            }
        }
        
        // Vérifier si tous les filtres sont vides
        var allEmpty = Object.keys(otherFilters).length === 0;
        
        // Vérifier si au moins un groupe de checkboxes a des cases cochées
        var hasActiveCheckboxFilters = false;
        if (checkboxGroupValues && Object.keys(checkboxGroupValues).length > 0) {
            for (var key in checkboxGroupValues) {
                if (checkboxGroupValues[key] && checkboxGroupValues[key].checkedValues.length > 0) {
                    // Vérifier si toutes les cases sont cochées
                    if (checkboxGroupValues[key].checkedValues.length !== checkboxGroupValues[key].allValues.length) {
                        hasActiveCheckboxFilters = true;
                        break;
                    }
                }
            }
        }
        
        if (allEmpty && !hasActiveCheckboxFilters) {
            // Si tous les filtres sont vides, afficher toutes les lignes
            $rows.show();
            return;
        }

        $rows.each(function() {
            var $row = $(this);
            var $cells = $row.find('td');
            var isVisible = true; // On part de visible

            // Vérifier les filtres autres que checkboxes (logique ET)
            for (var filterName in otherFilters) {
                var config = otherFilters[filterName];
                var filterValue = config.value;
                var searchTerm = normalizeString(filterValue);
                var filterMatched = false;
                var targetColumn = config.column; // La colonne spécifique pour ce filtre
                
                // Vérifier d'abord l'attribut data-search sur la ligne
                var rowSearchData = $row.attr('data-search');
                if (rowSearchData) {
                    var rowSearchText = normalizeString(rowSearchData);
                    if (rowSearchText.includes(searchTerm)) {
                        filterMatched = true;
                    }
                }

                // Si pas encore matched, vérifier les cellules
                if (!filterMatched) {
                    // Si une colonne spécifique est définie pour ce filtre
                    if (targetColumn !== null) {
                        // Vérifier uniquement cette colonne spécifique
                        if (targetColumn >= 0 && targetColumn < $cells.length) {
                            var cellText = normalizeString($cells.eq(targetColumn).text());
                            if (cellText.includes(searchTerm)) {
                                filterMatched = true;
                            }
                        }
                    } else if (columns === null) {
                        // Vérifier toutes les cellules
                        $cells.each(function() {
                            var cellText = normalizeString($(this).text());
                            if (cellText.includes(searchTerm)) {
                                filterMatched = true;
                                return false; // Sortir de la boucle each
                            }
                        });
                    } else {
                        // Vérifier uniquement les colonnes spécifiées dans filter_columns
                        for (var i = 0; i < columns.length; i++) {
                            var colIndex = columns[i];
                            if (colIndex >= 0 && colIndex < $cells.length) {
                                var cellText = normalizeString($cells.eq(colIndex).text());
                                if (cellText.includes(searchTerm)) {
                                    filterMatched = true;
                                    break;
                                }
                            }
                        }
                    }
                }
                
                // Si ce filtre ne match pas, la ligne n'est pas visible
                if (!filterMatched) {
                    isVisible = false;
                    break; // Sortir de la boucle des filtres
                }
            }
            
            // Si les filtres précédents ont déjà exclu la ligne, pas besoin de vérifier les checkboxes
            if (!isVisible) {
                $row.toggle(false);
                return;
            }
            
            // Vérifier les filtres checkbox (logique OU entre les checkboxes du même groupe)
            // Chaque groupe de checkboxes est un filtre OU, mais combiné avec ET aux autres filtres
            if (checkboxGroupValues && Object.keys(checkboxGroupValues).length > 0) {
                for (var filterName in checkboxGroupValues) {
                    var groupData = checkboxGroupValues[filterName];
                    
                    // Si toutes les cases sont cochées, on ignore ce groupe
                    if (groupData.checkedValues.length === groupData.allValues.length) {
                        continue;
                    }
                    
                    // Si aucune case n'est cochée, on ignore ce groupe (pas de filtre actif)
                    if (groupData.checkedValues.length === 0) {
                        continue;
                    }
                    
                    // Sinon, vérifier si au moins une valeur cochée match
                    var groupMatched = false;
                    var config = filterConfig[filterName];
                    var targetColumn = config ? config.column : null;
                    
                    // Vérifier chaque valeur cochée
                    for (var j = 0; j < groupData.checkedValues.length; j++) {
                        var searchTerm = groupData.checkedValues[j];
                        var valueMatched = false;
                        
                        // Vérifier d'abord l'attribut data-search sur la ligne
                        var rowSearchData = $row.attr('data-search');
                        if (rowSearchData) {
                            var rowSearchText = normalizeString(rowSearchData);
                            if (rowSearchText.includes(searchTerm)) {
                                valueMatched = true;
                            }
                        }
                        
                        // Si pas encore matched, vérifier les cellules
                        if (!valueMatched) {
                            if (targetColumn !== null) {
                                // Vérifier uniquement la colonne spécifique pour ce filtre checkbox
                                if (targetColumn >= 0 && targetColumn < $cells.length) {
                                    var cellText = normalizeString($cells.eq(targetColumn).text());
                                    if (cellText.includes(searchTerm)) {
                                        valueMatched = true;
                                    }
                                }
                            } else if (columns === null) {
                                // Vérifier toutes les cellules
                                $cells.each(function() {
                                    var cellText = normalizeString($(this).text());
                                    if (cellText.includes(searchTerm)) {
                                        valueMatched = true;
                                        return false; // Sortir de la boucle each
                                    }
                                });
                            } else {
                                // Vérifier uniquement les colonnes spécifiées dans filter_columns
                                for (var i = 0; i < columns.length; i++) {
                                    var colIndex = columns[i];
                                    if (colIndex >= 0 && colIndex < $cells.length) {
                                        var cellText = normalizeString($cells.eq(colIndex).text());
                                        if (cellText.includes(searchTerm)) {
                                            valueMatched = true;
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Si au moins une valeur cochée match, le groupe est validé (logique OU)
                        if (valueMatched) {
                            groupMatched = true;
                            break; // Sortir de la boucle des valeurs cochées
                        }
                    }
                    
                    // Si aucune valeur cochée ne match, la ligne n'est pas visible
                    if (!groupMatched) {
                        isVisible = false;
                        break; // Sortir de la boucle des groupes de checkboxes
                    }
                }
            }

            $row.toggle(isVisible);
        });
    }

    /**
     * Fonction publique pour filtrer manuellement
     */
    $.fn.filterTable = function(filterValue, columns) {
        var $table = this;
        if ($table.is('table')) {
            filterTable($table, filterValue, parseColumns(columns));
        } else {
            // Si c'est un conteneur
            var $foundTable = $table.find('table');
            if ($foundTable.length) {
                filterTable($foundTable, filterValue, parseColumns(columns));
            }
        }
        return this;
    };

    /**
     * Fonction publique pour initialiser un filtre manuellement
     */
    $.fn.setupTableFilter = function(options) {
        var settings = $.extend({
            filterSelector: null,
            columns: null
        }, options);

        var $container = this;
        var $filterInput = $(settings.filterSelector);
        
        if ($filterInput.length) {
            setupTableFilter($container, $filterInput, settings.columns);
        }
        
        return this;
    };

})(jQuery);
