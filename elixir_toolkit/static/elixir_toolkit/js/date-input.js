/**
 * Champ date du toolkit (ToolkitDateInput)
 * - bascule la classe `is-empty` du wrapper (placeholder grisé, croix masquée)
 * - la croix vide le champ et déclenche `input` / `change` (filtres HTMX, validations...)
 * - suit aussi les affectations JS (`input.value = ''`) et le contenu injecté dynamiquement
 */
(function () {
    if (window.ToolkitDateInputLoaded) return;
    window.ToolkitDateInputLoaded = true;

    var WRAPPER = '.toolkit-date-input';
    var INPUT = WRAPPER + ' > input';
    var CLEAR = '.toolkit-date-input__clear';
    var valueDescriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
    var initialized = new WeakSet();

    function sync(input) {
        var wrapper = input.closest(WRAPPER);
        if (!wrapper) return;
        // badInput : date partiellement saisie, la valeur reste vide mais le champ n'est pas « vide »
        var isEmpty = !input.value && !(input.validity && input.validity.badInput);
        wrapper.classList.toggle('is-empty', isEmpty);
    }

    function initInput(input) {
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
