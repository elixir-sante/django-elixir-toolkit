// Load custom 'plugins' added in 'externalPlugins' in CKeditor config
(function () {
    'use strict';

    function applyExternalPlugins(editor) {
        if (editor.__elixirExternalPluginsApplied) {
            return;
        }
        editor.__elixirExternalPluginsApplied = true;

        const editorConfig = editor.config._config;
        if (!editorConfig.externalPlugins) {
            return;
        }
        editorConfig.externalPlugins.forEach((pluginName) => {
            const pluginFn = window[pluginName];
            if (typeof pluginFn === "function") {
                pluginFn(editor); // passe l'éditeur en argument
            } else {
                console.error(`External plugin function "${pluginName}" not found`);
            }
        });
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
