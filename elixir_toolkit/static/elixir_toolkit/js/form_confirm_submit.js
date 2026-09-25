/**
 * Form Confirm Submit - JavaScript
 * Gère les modales de confirmation de soumission de formulaire
 * Utilise des boutons type="button" pour éviter le blocage par la validation HTML5 native
 *
 * Extension de la synthèse depuis un projet : après avoir listé les champs,
 * l'événement `form-confirm:summary` est émis sur le formulaire. Un projet
 * peut l'écouter pour compléter la synthèse (champs sans `name`, données
 * construites en JS…) sans modifier ce fichier :
 *
 *     form.addEventListener('form-confirm:summary', function (event) {
 *         event.detail.addItem('Libellé', 'Valeur');
 *     });
 *
 * detail : { form, container, list, addItem(label, value) }
 */

(function() {
    'use strict';

    // Functions to open and close a modal (approche standard Bulma)
    function openModal($el) {
        $el.classList.add('is-active');
    }

    function closeModal($el) {
        $el.classList.remove('is-active');
    }

    function closeAllModals() {
        (document.querySelectorAll('.modal') || []).forEach(function($modal) {
            closeModal($modal);
        });
    }

    // Fonction pour mettre en évidence les champs invalides avec Bulma is-danger
    function highlightInvalidFields(formElement) {
        var inputs = formElement.querySelectorAll('input, textarea, select');
        
        inputs.forEach(function(input) {
            
            if (!input.checkValidity()) {
                // Ajouter is-danger sur le parent .control
                input.classList.add('is-danger');
                
                // Retirer la classe quand l'utilisateur corrige le champ
                input.addEventListener('input', function() {
                    if (input.checkValidity()) {
                        input.classList.remove('is-danger');
                    }
                }, { once: true });
            } else {
                input.classList.remove('is-danger');
            }
        });
    }

    // Texte d'un libellé, sans le marqueur de champ obligatoire (« * »)
    function labelText(labelEl) {
        return labelEl ? labelEl.textContent.replace(/\s*\*\s*$/, '').trim() : '';
    }

    // Libellé du champ : celui du groupe pour une radio (pas celui de l'option), sinon
    // label[for=id], à défaut le .label du .field Bulma parent
    function fieldLabel(formElement, input) {
        var fieldParent = input.closest('.field');
        var groupLabel = fieldParent ? fieldParent.querySelector('.label') : null;

        if (input.type === 'radio') {
            return labelText(groupLabel);
        }

        var inputId = input.getAttribute('id');
        var labelFor = inputId ? formElement.querySelector('label[for="' + inputId + '"]') : null;
        return labelText(labelFor) || labelText(groupLabel);
    }

    // Valeur lisible du champ ; chaîne vide = champ ignoré dans la synthèse
    function fieldValue(input) {
        if (input.type === 'radio') {
            // Seule l'option cochée est reprise, avec son libellé
            if (!input.checked) { return ''; }
            var optionLabel = input.id ? document.querySelector('label[for="' + input.id + '"]') : null;
            return labelText(optionLabel) || input.value;
        }

        if (input.type === 'checkbox') {
            // Case non cochée ignorée (ex. case cachée « -clear » des uploads)
            return input.checked ? 'Oui' : '';
        }

        if (input.type === 'file') {
            // Tous les fichiers sélectionnés, un seul ou plusieurs
            return Array.from(input.files || []).map(function(f) { return f.name; }).join(', ');
        }

        if (input.tagName === 'SELECT') {
            // Libellé des options choisies plutôt que leur valeur technique
            return Array.from(input.selectedOptions || [])
                .filter(function(option) { return option.value !== ''; })
                .map(function(option) { return option.textContent.trim(); })
                .join(', ');
        }

        if (input.type === 'date' && input.value) {
            return new Date(input.value).toLocaleDateString('fr');
        }

        return input.value.trim();
    }

    // Ligne « libellé / valeur » de la synthèse
    function createSummaryItem(label, value) {
        var item = document.createElement('div');
        item.className = 'form-summary-item';

        var labelSpan = document.createElement('span');
        labelSpan.className = 'form-summary-label';
        labelSpan.textContent = label;

        var valueSpan = document.createElement('span');
        valueSpan.className = 'form-summary-value';
        valueSpan.textContent = value;

        item.appendChild(labelSpan);
        item.appendChild(valueSpan);
        return item;
    }

    // Génère la synthèse des champs du formulaire en HTML (divs)
    function generateFormSummary(formElement, containerClass) {
        var inputs = formElement.querySelectorAll('input[name]:not([type="hidden"]), textarea[name], select[name]');
        var summaryContainer = null;
        
        // Trouver le conteneur dans la modale
        var modal = formElement.closest('.modal') || document.querySelector('.modal[data-form-id="' + formElement.id + '"]');
        if (modal) {
            summaryContainer = modal.querySelector('.' + containerClass);
        }
        
        // Si pas trouvé, chercher dans le content target
        if (!summaryContainer) {
            var contentTarget = document.getElementById('form-confirm-content-' + formElement.id);
            if (contentTarget) {
                var containerClassFromData = contentTarget.getAttribute('data-summary-container-class');
                if (containerClassFromData) {
                    summaryContainer = contentTarget.querySelector('.' + containerClassFromData);
                }
            }
        }
        
        if (!summaryContainer) {
            return;
        }
        
        // Vider le conteneur
        summaryContainer.innerHTML = '';
        
        // Créer la liste de divs
        var summaryList = document.createElement('div');
        summaryList.className = 'form-summary-list';
        
        inputs.forEach(function(input) {
            var name = input.getAttribute('name');
            var value = fieldValue(input);

            // Ignorer les champs vides (dont radios / cases non cochées)
            if (!name || value === '') {
                return;
            }

            summaryList.appendChild(
                createSummaryItem(fieldLabel(formElement, input) || name, value)
            );
        });

        summaryContainer.appendChild(summaryList);

        // Point d'extension : le projet complète la synthèse s'il le souhaite
        formElement.dispatchEvent(new CustomEvent('form-confirm:summary', {
            bubbles: true,
            detail: {
                form: formElement,
                container: summaryContainer,
                list: summaryList,
                addItem: function(label, value) {
                    if (value === undefined || value === null || value === '') { return; }
                    summaryList.appendChild(createSummaryItem(label, value));
                }
            }
        }));
    }

    // Initialise une seule modale de confirmation
    function initModal(modal) {
        var formId = modal.getAttribute('data-form-id');
        var form = document.getElementById(formId);
        
        if (!form) {
            return;
        }

        var submitButton = modal.querySelector('.button[action="submit"]');
        
        // Trouver le bouton de soumission dans le formulaire (type="button" avec data-form-confirm)
        var formSubmitBtn = form.querySelector('[data-form-confirm="' + formId + '"], button.js-form-confirm');

        if (formSubmitBtn) {
            // Écouter le clic sur le bouton de soumission du formulaire
            formSubmitBtn.addEventListener('click', function(event) {

                event.preventDefault();
                event.stopPropagation();
                
                // Valider le formulaire
                if (!form.checkValidity()) {
                    highlightInvalidFields(form);
                    form.reportValidity();
                    return;
                }
                
                // Formulaire valide : ouvrir la modale
                openModal(modal);
                
                // Générer et injecter la synthèse des champs
                var contentTarget = document.getElementById('form-confirm-content-' + formId);
                if (contentTarget) {
                    var containerClass = contentTarget.getAttribute('data-summary-container-class') || 'form-summary-container';
                    generateFormSummary(form, containerClass);
                }
                
                // Réinitialiser l'état du bouton Envoyer de la modale
                if (submitButton) {
                    submitButton.classList.remove('is-loading');
                }
            });
        }

        // Bouton Envoyer dans la modale : soumet le formulaire
        if (submitButton) {
            submitButton.addEventListener('click', function() {
                if (submitButton) {
                    submitButton.classList.add('is-loading');
                }
                // Support both HTMX and traditional forms
                if (window.htmx && Array.from(form.attributes).some(attr => attr.name.startsWith('hx-'))) {
                    console.log("HTMX forced form submission");
                    htmx.trigger(form, 'submit');
                } else {
                    console.log("standard HTML form submission");
                    form.submit();
                }
            });
        }
    }

    // Initialise les modales de confirmation pour les nouveaux éléments
    function initFormConfirmSubmitModals() {
        var modals = document.querySelectorAll('.modal.form-confirm-submit-modal');
        
        modals.forEach(function(modal) {
            // Vérifier si déjà initialisé via un attribut data
            if (!modal.hasAttribute('data-initialized')) {
                modal.setAttribute('data-initialized', 'true');
                initModal(modal);
            }
        });

        // Fermer les modales avec les éléments standards Bulma
        (document.querySelectorAll('.modal-background, .modal-card-head .delete') || []).forEach(function($close) {
            if (!$close.hasAttribute('data-close-initialized')) {
                $close.setAttribute('data-close-initialized', 'true');
                var $target = $close.closest('.modal');
                $close.addEventListener('click', function() {
                    closeModal($target);
                });
            }
        });

        // Fermer avec les boutons Annuler (action="cancel")
        (document.querySelectorAll('.button[action="cancel"]') || []).forEach(function($cancel) {
            if (!$cancel.hasAttribute('data-cancel-initialized')) {
                $cancel.setAttribute('data-cancel-initialized', 'true');
                var $target = $cancel.closest('.modal');
                $cancel.addEventListener('click', function() {
                    closeModal($target);
                });
            }
        });
    }

    // Initialiser au chargement de la page
    document.addEventListener('DOMContentLoaded', function() {
        initFormConfirmSubmitModals();

        // Fermer avec la touche Escape (un seul écouteur global)
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeAllModals();
            }
        });
    });

    // Initialiser après HTMX after swap
    document.addEventListener('htmx:afterSwap', function() {
        initFormConfirmSubmitModals();
    });

    // Initialiser après HTMX after settle
    document.addEventListener('htmx:afterSettle', function() {
        initFormConfirmSubmitModals();
    });

    // Exposer pour les tests ou extensions
    window.FormConfirmSubmit = {
        openModal: openModal,
        closeModal: closeModal,
        closeAllModals: closeAllModals,
        highlightInvalidFields: highlightInvalidFields
    };
})();