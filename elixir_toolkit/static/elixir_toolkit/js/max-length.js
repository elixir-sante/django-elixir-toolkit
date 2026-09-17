/**
 * Limite de caractères des champs `[data-max-length]` (posé par `elixir_toolkit.forms.limit_length`)
 * - compteur « n / max caractères » sous les `textarea` et les éditeurs CKEditor, en rouge à la limite
 * - `input` / `textarea` : blocage natif via l'attribut `maxlength`
 * - CKEditor : bloque la frappe et tronque le texte collé au-delà de la limite
 * - contenu déjà trop long (valeur en base, glisser-déposer...) : message d'erreur
 *   et boutons submit du formulaire désactivés
 *
 * Le message d'erreur est surchargeable par champ via `data-max-length-message`.
 */
(function () {
    if (window.ElixirMaxLengthLoaded) return;
    window.ElixirMaxLengthLoaded = true;

    var TEXTAREA = 'textarea[data-max-length]:not(.django_ckeditor_5)';
    var OVER = 'data-max-length-over';
    var DISABLED = 'data-max-length-disabled';
    var SUBMIT = 'button:not([type]), button[type="submit"], input[type="submit"]';
    var initialized = new WeakSet();

    function maxLengthOf(element) {
        return parseInt(element.getAttribute('data-max-length'), 10);
    }

    // Désactive les submit du formulaire tant qu'un de ses champs dépasse sa limite
    function refreshSubmit(form) {
        if (!form) return;
        var over = !!form.querySelector('[' + OVER + ']');
        form.querySelectorAll(SUBMIT).forEach(function (button) {
            if (over && !button.disabled) {
                button.disabled = true;
                button.setAttribute(DISABLED, '');
            } else if (!over && button.hasAttribute(DISABLED)) {
                button.disabled = false;
                button.removeAttribute(DISABLED);
            }
        });
    }

    // Insère compteur et message d'erreur après `anchor`, renvoie la fonction de rafraîchissement
    function createFeedback(element, anchor) {
        var max = maxLengthOf(element);

        var counter = document.createElement('p');
        counter.className = 'help toolkit-max-length__counter';

        var error = document.createElement('p');
        error.className = 'help is-danger is-hidden';
        error.setAttribute('role', 'alert');
        error.textContent = element.getAttribute('data-max-length-message')
            || 'Ce champ est limité à ' + max + ' caractères.';

        anchor.after(counter, error);

        return function update(length) {
            var over = length > max;
            counter.textContent = length + ' / ' + max + ' caractères';
            counter.classList.toggle('has-text-danger', length >= max);
            error.classList.toggle('is-hidden', !over);
            element.toggleAttribute(OVER, over);
            refreshSubmit(element.closest('form'));
        };
    }

    function initTextarea(textarea) {
        if (initialized.has(textarea)) return;
        initialized.add(textarea);

        var update = createFeedback(textarea, textarea.closest('.control') || textarea);
        function refresh() {
            update(textarea.value.length);
        }
        textarea.addEventListener('input', refresh);
        refresh();
    }

    // Nombre de caractères de texte dans des ranges du modèle CKEditor
    function textLength(ranges) {
        var length = 0;
        for (var range of ranges) {
            for (var item of range.getItems()) {
                if (item.is('$textProxy')) length += item.data.length;
            }
        }
        return length;
    }

    function initEditor(editor) {
        var element = editor.sourceElement;
        if (!element || !element.hasAttribute('data-max-length') || initialized.has(element)) return;
        initialized.add(element);

        var max = maxLengthOf(element);
        var model = editor.model;
        var viewDocument = editor.editing.view.document;

        function totalLength() {
            return textLength([model.createRangeIn(model.document.getRoot())]);
        }

        // Caractères encore insérables si le contenu de `ranges` (la sélection) est remplacé
        function remaining(ranges) {
            return max - totalLength() + textLength(ranges);
        }

        viewDocument.on('insertText', function (evt, data) {
            if (data.isComposing) return;
            var ranges = data.selection
                ? Array.from(data.selection.getRanges(), function (range) {
                    return editor.editing.mapper.toModelRange(range);
                })
                : Array.from(model.document.selection.getRanges());
            var allowed = remaining(ranges);
            if (data.text.length <= allowed) return;
            if (allowed > 0) {
                data.text = data.text.slice(0, allowed);
            } else {
                data.preventDefault();
                evt.stop();
            }
        }, { priority: 'highest' });

        viewDocument.on('clipboardInput', function (evt, data) {
            if (data.method === 'drop') return;
            var text = data.dataTransfer.getData('text/plain');
            var allowed = remaining(model.document.selection.getRanges());
            if (text.replace(/\n/g, '').length <= allowed) return;

            evt.stop();
            if (allowed <= 0) return;

            // Tronque au `allowed`-ième caractère, retours à la ligne non comptés
            var kept = 0;
            var end = 0;
            while (end < text.length && kept < allowed) {
                if (text[end] !== '\n') kept++;
                end++;
            }
            var container = document.createElement('div');
            var html = text.slice(0, end).split(/\n+/).map(function (line) {
                container.textContent = line;
                return '<p>' + container.innerHTML + '</p>';
            }).join('');
            model.change(function () {
                model.insertContent(editor.data.parse(html));
            });
        }, { priority: 'highest' });

        // Remplace le compteur mots / caractères de django_ckeditor_5
        var wordCount = document.getElementById(element.id + '_script-word-count');
        if (wordCount) wordCount.hidden = true;

        var update = createFeedback(element, element.closest('.ck-editor-container') || editor.ui.element);
        function refresh() {
            update(totalLength());
        }
        model.document.on('change:data', refresh);
        refresh();
    }

    function init() {
        document.querySelectorAll(TEXTAREA).forEach(initTextarea);
    }

    // Fourni par ckeditor-load-external-plugins.js
    function watchEditors() {
        if (typeof window.elixirOnCkeditorReady === 'function') {
            window.elixirOnCkeditorReady(initEditor);
            return true;
        }
        return false;
    }

    var editorsWatched = watchEditors();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            if (!editorsWatched) editorsWatched = watchEditors();
            init();
        });
    } else {
        init();
    }

    document.addEventListener('htmx:afterSettle', init);
})();
