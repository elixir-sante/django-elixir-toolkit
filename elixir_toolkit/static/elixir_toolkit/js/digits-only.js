/**
 * Saisie numérique des champs `[data-digits-only]`
 * - supprime tout caractère autre qu'un chiffre (frappe, collage, glisser-déposer)
 * - conserve la position du curseur
 * - délégation sur `document` : couvre aussi le contenu injecté dynamiquement (HTMX)
 *
 * Confort de saisie uniquement : garder un validateur côté serveur.
 */
(function () {
    if (window.ElixirDigitsOnlyLoaded) return;
    window.ElixirDigitsOnlyLoaded = true;

    var NON_DIGITS = /\D/g;

    document.addEventListener('input', function (event) {
        var input = event.target;
        if (!input.matches || !input.matches('[data-digits-only]')) return;

        var value = input.value;
        var digits = value.replace(NON_DIGITS, '');
        if (digits === value) return;

        // Curseur : nombre de chiffres situés avant lui dans la saisie brute
        var caret = input.selectionStart;
        var position = caret === null ? digits.length : value.slice(0, caret).replace(NON_DIGITS, '').length;

        input.value = digits;
        if (caret !== null) input.setSelectionRange(position, position);
    });
})();
