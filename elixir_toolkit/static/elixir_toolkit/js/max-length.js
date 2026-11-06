/**
 * Limite de caractères des champs `[data-max-length]` (posé sur tout `forms.CharField` avec `max_length`, cf. `elixir_toolkit/apps.py`)
 * - compteur « n / max caractères » sous les `textarea`, les éditeurs CKEditor et les `input`
 *   portant `data-max-length-counter`, en rouge à la limite
 * - `data-max-length-ignore-spaces` : espaces exclus du décompte (ex. IBAN saisi par groupes de 4)
 * - `input` / `textarea` : blocage natif via l'attribut `maxlength` ; sans `maxlength`
 *   (cas `data-max-length-ignore-spaces`), frappe bloquée et texte collé tronqué en JS
 * - CKEditor : bloque la frappe et tronque le texte collé au-delà de la limite
 * - contenu déjà trop long (valeur en base, glisser-déposer...) : message d'erreur
 *   et boutons submit du formulaire désactivés
 *
 * Le message d'erreur est surchargeable par champ via `data-max-length-message`.
 */
(function () {
    if (window.ElixirMaxLengthLoaded) return;
    window.ElixirMaxLengthLoaded = true;

    var FIELDS = 'textarea[data-max-length]:not(.django_ckeditor_5), input[data-max-length][data-max-length-counter]';
    var SPACES = /\s/g;
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

        // 1.3.1 / 3.3.1 : compteur et erreur reliés au champ par aria-describedby
        var baseId = element.id || element.getAttribute('name') || 'field';
        counter.id = baseId + '-max-length-counter';
        error.id = baseId + '-max-length-error';
        var extra = counter.id + ' ' + error.id;
        var describedby = element.getAttribute('aria-describedby');
        element.setAttribute('aria-describedby', describedby ? describedby + ' ' + extra : extra);

        anchor.after(counter, error);

        return function update(length) {
            var over = length > max;
            counter.textContent = length + ' / ' + max + ' caractères';
            // is-danger (comme le message d'erreur) et pas has-text-danger : contraste 1.4.3
            counter.classList.toggle('is-danger', length >= max);
            error.classList.toggle('is-hidden', !over);
            element.toggleAttribute(OVER, over);
            refreshSubmit(element.closest('form'));
        };
    }

    function initField(field) {
        if (initialized.has(field)) return;
        initialized.add(field);

        var update = createFeedback(field, field.closest('.control') || field);
        var ignoreSpaces = field.hasAttribute('data-max-length-ignore-spaces');
        function count(text) {
            return (ignoreSpaces ? text.replace(SPACES, '') : text).length;
        }
        function refresh() {
            update(count(field.value));
        }
        field.addEventListener('input', refresh);
        // Pas de `maxlength` natif (il compterait les espaces) : blocage équivalent en JS
        if (!field.hasAttribute('maxlength')) blockOverflow(field, maxLengthOf(field), count);
        refresh();
    }

    // Bloque la frappe et tronque le texte collé au-delà de `max` (décompte par `count`),
    // comme le ferait l'attribut `maxlength`. Le glisser-déposer reste signalé par l'erreur.
    function blockOverflow(field, max, count) {
        field.addEventListener('beforeinput', function (event) {
            var type = event.inputType || '';
            if (event.isComposing || type.indexOf('insert') !== 0 || type === 'insertFromDrop') return;
            var text = event.data;
            if (text == null && event.dataTransfer) text = event.dataTransfer.getData('text/plain');
            var start = field.selectionStart;
            var end = field.selectionEnd;
            if (text == null || start === null) return;

            var value = field.value;
            var allowed = max - count(value.slice(0, start) + value.slice(end));
            if (count(text) <= allowed) return;

            event.preventDefault();
            if (allowed <= 0) return;
            // Garde le début du texte jusqu'à `allowed` caractères comptés
            var cut = 0;
            while (cut < text.length && count(text.slice(0, cut + 1)) <= allowed) cut++;
            field.setRangeText(text.slice(0, cut), start, end, 'end');
            field.dispatchEvent(new Event('input', { bubbles: true }));
        });
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
        document.querySelectorAll(FIELDS).forEach(initField);
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
