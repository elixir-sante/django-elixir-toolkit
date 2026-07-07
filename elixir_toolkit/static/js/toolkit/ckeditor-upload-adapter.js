
class MyUploadAdapter {
    constructor(loader, uploadUrl, csrfToken) {
        this.loader = loader;
        this.uploadUrl = uploadUrl;
        this.csrfToken = csrfToken;
    }

    upload() {
        // Notifier début upload (désactivation bouton)
        document.dispatchEvent(new CustomEvent('uploadStarted'));

        return this.loader.file.then(file => new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', this.uploadUrl, true);
            xhr.setRequestHeader('X-CSRFToken', this.csrfToken);
            xhr.responseType = 'json';

            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    const percent = (event.loaded / event.total) * 100;
                    this.loader.uploadTotal = event.total;
                    this.loader.uploaded = event.loaded;

                    // Affichage barre de progression
                    const container = document.getElementById('uploadProgressContainer');
                    const bar = document.getElementById('uploadProgressBar');
                    const text = document.getElementById('uploadProgressText');
                    if (!container || !bar || !text) {
                        return;
                    }
                    container.style.display = 'block';
                    text.style.display = 'block';

                    bar.style.width = percent + '%';
                    text.textContent = `Téléchargement en cours : ${percent.toFixed(0)}%`;
                }
            };

            xhr.onload = () => {
                // Notifier fin upload (réactivation bouton)
                document.dispatchEvent(new CustomEvent('uploadFinished'));

                if (xhr.status === 201 || xhr.status === 200) {
                    // Cacher la barre après un délai
                    setTimeout(() => {
                        const container = document.getElementById('uploadProgressContainer');
                        const text = document.getElementById('uploadProgressText');
                        if (container) container.style.display = 'none';
                        if (text) text.style.display = 'none';
                    }, 1500);

                    resolve({ default: xhr.response.url });
                } else {
                    reject(`Erreur lors du téléchargement : ${xhr.statusText}`);
                }
            };

            xhr.onerror = () => {
                document.dispatchEvent(new CustomEvent('uploadFinished'));
                reject('Erreur réseau.');
            };

            const data = new FormData();
            data.append('upload', file);

            xhr.send(data);
        }));
    }

    abort() {
        // Optionnel : gérer annulation si nécessaire
    }
}

function MyUploadAdapterPlugin(editor) {
    const uploadUrl = window.CKEDITOR_UPLOAD_URL;
    const csrfToken = window.CKEDITOR_CSRF_TOKEN;
    if (!uploadUrl) {
        throw new Error(
            "CKEditor upload URL is not defined. " +
            "Please make sure to include `window.CKEDITOR_UPLOAD_URL` in your template."
        );
    }
    if (!csrfToken) {
        throw new Error(
            "CKEditor CSRF_TOKEN is not defined. " +
            "Please make sure to include `window.CKEDITOR_CSRF_TOKEN` in your template."
        );
    }
    editor.plugins.get('FileRepository').createUploadAdapter = (loader) => {
        return new MyUploadAdapter(loader, uploadUrl, csrfToken);
    };
    console.log("MyUploadAdapterPlugin plugin loaded.");
}

// Gestion activation / désactivation du bouton submit pendant upload
if (!window.__elixirCkeditorUploadListenersInstalled) {
    window.__elixirCkeditorUploadListenersInstalled = true;

    document.addEventListener('uploadStarted', () => {
        const submitButton = document.querySelector('form input[type="submit"].button');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.classList.add('is-loading'); // optionnel, effet Bulma
        }
    });

    document.addEventListener('uploadFinished', () => {
        const submitButton = document.querySelector('form input[type="submit"].button');
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.classList.remove('is-loading');
        }
    });
}
