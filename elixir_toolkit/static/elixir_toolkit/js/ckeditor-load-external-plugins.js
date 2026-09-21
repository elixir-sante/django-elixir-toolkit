// Load custom 'plugins' added in 'externalPlugins' in CKeditor config
(function () {
    'use strict';

    // `ckeditorRegisterCallback` ne garde qu'un callback par éditeur, occupé par ce loader :
    // `window.elixirOnCkeditorReady(hook)` permet aux autres scripts d'être appelés sur chaque éditeur.
    const readyHooks = window.__elixirCkeditorReadyHooks = window.__elixirCkeditorReadyHooks || [];
    window.elixirOnCkeditorReady = window.elixirOnCkeditorReady || function (hook) {
        readyHooks.push(hook);
        // Éditeurs déjà traités : les suivants passeront par applyExternalPlugins
        Object.values(window.editors || {}).forEach((editor) => {
            if (editor.__elixirExternalPluginsApplied) {
                hook(editor);
            }
        });
    };

    function applyExternalPlugins(editor) {
        if (editor.__elixirExternalPluginsApplied) {
            return;
        }
        editor.__elixirExternalPluginsApplied = true;

        const editorConfig = editor.config._config;
        (editorConfig.externalPlugins || []).forEach((pluginName) => {
            const pluginFn = window[pluginName];
            if (typeof pluginFn === "function") {
                pluginFn(editor); // passe l'éditeur en argument
            } else {
                console.error(`External plugin function "${pluginName}" not found`);
            }
        });

        readyHooks.forEach((hook) => hook(editor));
    }

    function init() {
        document.querySelectorAll('.django_ckeditor_5').forEach(function (el) {
            const editor = window.editors?.[el.id];
            if (editor) {
                applyExternalPlugins(editor);
            } else if (typeof window.ckeditorRegisterCallback === 'function') {
                // ClassicEditor.create() est asynchrone : callback appelé à la création
                window.ckeditorRegisterCallback(el.id, applyExternalPlugins);
            }
        });
    }

    if (window.__elixirCkeditorPluginsLoaderInstalled) {
        init();
        return;
    }
    window.__elixirCkeditorPluginsLoaderInstalled = true;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { init(); });
    } else {
        init();
    }

    document.addEventListener('htmx:afterSettle', function () { init(); });
})();
