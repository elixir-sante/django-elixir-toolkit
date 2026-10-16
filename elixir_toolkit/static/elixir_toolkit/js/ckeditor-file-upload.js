/**
 * Bouton « Insérer un fichier » de CKEditor (config `custom_page`).
 *
 * Remplace le plugin FileUploader, retiré de django-ckeditor-5 (>= 0.2.19).
 * Plugin externe (voir `externalPlugins` dans CKEDITOR_5_CONFIGS), appelé par
 * ckeditor-load-external-plugins.js une fois l'éditeur créé.
 *
 * Le fichier passe par l'adaptateur d'upload de la toolkit (MyUploadAdapterPlugin,
 * même URL que les images), puis un lien vers le fichier est inséré à la position
 * du curseur.
 */
function MyFileUploadPlugin(editor) {
    'use strict';

    const ICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'
        + '<path d="M11.5 1h-7A1.5 1.5 0 0 0 3 2.5v15A1.5 1.5 0 0 0 4.5 19h11a1.5 1.5 0 0 0 1.5-1.5v-11L11.5 1zm0 1.8 3.7 3.7h-3.7V2.8zm4 14.7h-11v-15H10V8h5.5v9.5z"/>'
        + '<path d="M6.5 11h7v1.5h-7zm0 3h7v1.5h-7z"/></svg>';

    // Sélecteur de fichier masqué, ouvert par le bouton
    const input = document.createElement('input');
    input.type = 'file';
    input.hidden = true;
    input.dataset.ckeditorFileUpload = editor.sourceElement.id;
    document.body.appendChild(input);

    // La classe ButtonView n'est pas exposée par le bundle CKEditor : on reprend
    // celle du premier bouton de la barre (« Annuler »)
    const toolbar = editor.ui.view.toolbar;
    const button = new toolbar.items.first.constructor(editor.locale);
    button.set({ label: 'Insérer un fichier', icon: ICON, tooltip: true });
    button.on('execute', () => input.click());
    toolbar.items.add(button);

    input.addEventListener('change', () => {
        const file = input.files[0];
        input.value = '';
        if (!file) {
            return;
        }
        const repository = editor.plugins.get('FileRepository');
        const loader = repository.createLoader(file);
        loader.upload()
            .then((response) => editor.model.change((writer) => {
                editor.model.insertContent(writer.createText(file.name, { linkHref: response.default }));
            }))
            .catch((error) => globalThis.alert(`Le fichier n'a pas pu être ajouté. ${error}`))
            .finally(() => repository.destroyLoader(loader));
    });
}
