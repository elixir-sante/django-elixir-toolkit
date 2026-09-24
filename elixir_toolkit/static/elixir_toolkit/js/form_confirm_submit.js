/**
 * Form Confirm Submit - JavaScript
 * Gère les modales de confirmation de soumission de formulaire
 * Utilise des boutons type="button" pour éviter le blocage par la validation HTML5 native
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
            var value = input.value;
            
            // Pour les champs file, récupérer le(s) nom(s) du/des fichier(s)
            if (input.type === 'file') {
                if (input.files && input.files.length > 0) {
                    if (input.multiple) {
                        // Fichiers multiples : joindre tous les noms
                        value = Array.from(input.files).map(function(f) { return f.name; }).join(', ');
                    } else {
                        // Fichier unique
                        value = input.files[0].name;
                    }
                } else {
                    value = '';
                }
            }
            
            // Pour les champs date, formater avec toLocaleDateString
            if (input.type === 'date' && value) {
                value = new Date(value).toLocaleDateString("fr");
            }
            
            // Ignorer les champs vides
            if (!name || value === '') {
                return;
            }
            
            // Trouver le label associé
            var labelText = name;
            
            // 1. Chercher label avec for=id
            var inputId = input.getAttribute('id');
            if (inputId) {
                var labelFor = formElement.querySelector('label[for="' + inputId + '"]');
                if (labelFor) {
                    labelText = labelFor.textContent.trim();
                }
            }
            
            // 2. Chercher dans la structure Bulma : parent .field > .label
            if (labelText === name) {
                var fieldParent = input.closest('.field');
                if (fieldParent) {
                    var labelEl = fieldParent.querySelector('.label');
                    if (labelEl) {
                        labelText = labelEl.textContent.trim();
                    }
                }
            }
            
            // Créer un item de synthèse
            var item = document.createElement('div');
            item.className = 'form-summary-item';
            
            var labelSpan = document.createElement('span');
            labelSpan.className = 'form-summary-label';
            labelSpan.textContent = labelText;
            
            var valueSpan = document.createElement('span');
            valueSpan.className = 'form-summary-value';
            valueSpan.textContent = value;
            
            item.appendChild(labelSpan);
            item.appendChild(valueSpan);
            summaryList.appendChild(item);
        });
        
        summaryContainer.appendChild(summaryList);
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
                form.submit();
            });
        }
    }

    // Initialiser au chargement de la page
    document.addEventListener('DOMContentLoaded', function() {
        // Trouver toutes les modales de confirmation
        var modals = document.querySelectorAll('.modal.form-confirm-submit-modal');
        
        modals.forEach(function(modal) {
            initModal(modal);
        });

        // Fermer les modales avec les éléments standards Bulma
        (document.querySelectorAll('.modal-background, .modal-card-head .delete') || []).forEach(function($close) {
            var $target = $close.closest('.modal');
            $close.addEventListener('click', function() {
                closeModal($target);
            });
        });

        // Fermer avec la touche Escape
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeAllModals();
            }
        });

        // Fermer avec les boutons Annuler (action="cancel")
        (document.querySelectorAll('.button[action="cancel"]') || []).forEach(function($cancel) {
            var $target = $cancel.closest('.modal');
            $cancel.addEventListener('click', function() {
                closeModal($target);
            });
        });
    });

    // Exposer pour les tests ou extensions
    window.FormConfirmSubmit = {
        openModal: openModal,
        closeModal: closeModal,
        closeAllModals: closeAllModals,
        highlightInvalidFields: highlightInvalidFields
    };
})();
