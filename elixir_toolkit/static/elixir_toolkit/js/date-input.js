/**
 * Champ date natif (`input[type="date"]`)
 * - construit le wrapper et la croix de réinitialisation (aucun widget ni template Django requis)
 * - bascule la classe `is-empty` du wrapper (placeholder grisé, croix masquée)
 * - la croix vide le champ et déclenche `input` / `change` (filtres HTMX, validations...)
 * - suit les affectations JS (`input.value = ''`) et le contenu injecté dynamiquement
 *
 * Le libellé de la croix est surchargeable par champ via `data-clear-label`.
 */
(function () {
    if (window.ElixirDateInputLoaded) return;
    window.ElixirDateInputLoaded = true;

    var INPUT = 'input[type="date"]';
    var WRAPPER = '.toolkit-date-input';
    var CLEAR = '.toolkit-date-input__clear';
    var DEFAULT_CLEAR_LABEL = 'Effacer la date';
    var valueDescriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
    var initialized = new WeakSet();

    function sync(input) {
        var wrapper = input.closest(WRAPPER);
        if (!wrapper) return;
        // badInput : date partiellement saisie, la valeur reste vide mais le champ n'est pas « vide »
        var isEmpty = !input.value && !(input.validity && input.validity.badInput);
        wrapper.classList.toggle('is-empty', isEmpty);
    }

    function wrap(input) {
        var parent = input.parentElement;
        if (!parent || parent.classList.contains('toolkit-date-input')) return;

        var wrapper = document.createElement('span');
        wrapper.className = 'toolkit-date-input';
        parent.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        var label = input.getAttribute('data-clear-label') || DEFAULT_CLEAR_LABEL;
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'delete is-small toolkit-date-input__clear';
        button.setAttribute('aria-label', label);
        button.setAttribute('title', label);
        wrapper.appendChild(button);
    }

    function initInput(input) {
        wrap(input);
        // Classe Bulma, que le champ soit rendu par crispy ou écrit à la main
        input.classList.add('input');

        if (!initialized.has(input)) {
            initialized.add(input);
            Object.defineProperty(input, 'value', {
                configurable: true,
                get: function () {
                    return valueDescriptor.get.call(this);
                },
                set: function (value) {
                    valueDescriptor.set.call(this, value);
                    sync(this);
                }
            });
        }
        sync(input);
    }

    function init(root) {
        if (root.matches && root.matches(INPUT)) {
            initInput(root);
            return;
        }
        if (root.querySelectorAll) {
            root.querySelectorAll(INPUT).forEach(initInput);
        }
    }

    document.addEventListener('input', function (e) {
        if (e.target.matches && e.target.matches(INPUT)) sync(e.target);
    });

    document.addEventListener('change', function (e) {
        if (e.target.matches && e.target.matches(INPUT)) sync(e.target);
    });

    // Chrome ne déclenche pas `input` tant que la date est incomplète :
    // sans ce listener, la couleur ne repasse en normal qu'une fois la date entière saisie.
    document.addEventListener('keyup', function (e) {
        if (e.target.matches && e.target.matches(INPUT)) sync(e.target);
    });

    document.addEventListener('click', function (e) {
        var button = e.target.closest && e.target.closest(CLEAR);
        if (!button) return;
        e.preventDefault();

        var input = button.closest(WRAPPER).querySelector('input');
        if (!input || input.disabled || input.readOnly) return;

        input.value = '';
        sync(input);
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.focus();
    });

    document.addEventListener('reset', function (e) {
        var form = e.target;
        // Les valeurs sont restaurées après l'événement reset
        setTimeout(function () { init(form); }, 0);
    });

    function start() {
        init(document);
        new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                mutation.addedNodes.forEach(function (node) {
                    if (node.nodeType === 1) init(node);
                });
            });
        }).observe(document.documentElement, { childList: true, subtree: true });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
