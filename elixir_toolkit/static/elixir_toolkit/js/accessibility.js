/**
 * Accessibilité générique (WCAG 2.1 AA), indépendante des composants :
 * - 4.1.2 : nom accessible sur les boutons « croix » (button.delete) des
 *   notifications / messages (rendus par crispy hors du périmètre du toolkit)
 */
(function () {
    if (window.ElixirAccessibilityLoaded) return;
    window.ElixirAccessibilityLoaded = true;

    function labelDeleteButtons(root) {
        (root || document)
            .querySelectorAll('button.delete:not([aria-label]):not([aria-labelledby])')
            .forEach(function (btn) {
                btn.setAttribute('aria-label', 'Fermer');
            });
    }

    // Selectize mesure la largeur des libellés via un conteneur caché ajouté au
    // <body> (Selectize.$testInput) : purement visuel, hors du contenu -> aria-hidden
    function hideMeasureContainers() {
        if (window.Selectize && Selectize.$testInput) {
            var parent = Selectize.$testInput.parent()[0];
            if (parent && !parent.hasAttribute('aria-hidden')) {
                parent.setAttribute('aria-hidden', 'true');
            }
        }
    }

    // Django pose aria-describedby="{auto_id}_error" sur les champs en erreur, mais
    // crispy-bulma rend les erreurs avec id="error_N_{auto_id}" : on rétablit le lien
    // (3.3.1 / 4.1.3) et on retire les tokens qui ne référencent rien.
    function fixDescribedby(root) {
        (root || document).querySelectorAll('[aria-describedby]').forEach(function (el) {
            var tokens = (el.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
            var valid = tokens.filter(function (t) { return document.getElementById(t); });
            tokens.filter(function (t) { return !document.getElementById(t); }).forEach(function (t) {
                var m = t.match(/^(.*)_error$/);
                if (!m) return;
                document.querySelectorAll('[id^="error_"][id$="_' + m[1] + '"]').forEach(function (err) {
                    if (valid.indexOf(err.id) === -1) valid.push(err.id);
                });
            });
            if (valid.length) el.setAttribute('aria-describedby', valid.join(' '));
            else el.removeAttribute('aria-describedby');
        });
    }

    function init(root) {
        labelDeleteButtons(root);
        hideMeasureContainers();
        fixDescribedby(root);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { init(document); });
    } else {
        init(document);
    }

    document.addEventListener('htmx:afterSettle', function () { init(document); });

    // Contenu injecté hors HTMX (scripts tiers, modales...)
    new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (node) {
                if (node.nodeType === 1) init(node);
            });
        });
    }).observe(document.documentElement, { childList: true, subtree: true });
})();
