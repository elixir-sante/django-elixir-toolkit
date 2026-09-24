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
