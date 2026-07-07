CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'pdf', 'jpg', 'png']
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "authenticated"

_LINK_DECORATORS = {
    'decorators': {
        'openInNewTab': {
            'mode': 'manual',
            'label': 'Ouvrir dans un nouvel onglet',
            'attributes': {
                'target': '_blank',
                'rel': 'noopener noreferrer',
            }
        }
    }
}

_HEADING_OPTIONS = [
    {'model': 'paragraph', 'title': 'Paragraphe'},
    {
        'model': 'Titre',
        'view': {'name': 'h1', 'classes': 'title'},
        'title': 'Titre',
        'converterPriority': 'high',
    },
    {
        'model': 'Sous-titre',
        'view': {'name': 'h2', 'classes': 'subtitle'},
        'title': 'Sous-titre',
        'converterPriority': 'high',
    },
    {
        'model': 'Bouton primaire',
        'view': {'name': 'div', 'classes': ['button', 'is-primary']},
        'title': 'Bouton primaire',
        'converterPriority': 'high',
    },
    {
        'model': 'Bouton secondaire',
        'view': {'name': 'div', 'classes': 'button'},
        'title': 'Bouton secondaire',
        'converterPriority': 'high',
    },
]

_TABLE_TOOLBAR = {
    'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                       'tableProperties', 'tableCellProperties'],
}

_FONT_COLOR = {
    'colorPicker': True,
    'columns': 5,
    'documentColors': 10,
}

CKEDITOR_5_CONFIGS = {
    'default': {
        'licenseKey': 'GPL',
        'toolbar': [],
        'language': 'fr',
    },
    'extends': {
        'licenseKey': 'GPL',
        'toolbar': ["undo", "redo", '|', 'heading', '|', 'bold', 'italic',
                    'fontColor', 'numberedList', 'bulletedList', 'alignment',
                    '|', 'link', 'insertTable'],
        'language': 'fr',
        'alignment': {
            'options': ['left', 'center', 'right', 'justify']
        },
        'fontColor': _FONT_COLOR,
        'linkPickerUrl': '/ckeditor/internal-links/',
        'table': _TABLE_TOOLBAR,
        'link': _LINK_DECORATORS,
        'heading': {
            'options': _HEADING_OPTIONS,
        },
    },
    'custom_page': {
        'licenseKey': 'GPL',
        # Chargés par {% ckeditor_post %}
        'externalPlugins': [
            'MyUploadAdapterPlugin',
            'MyClipboardIframePlugin',
            'MyClipboardBlockquotePlugin',
        ],
        'removePlugins': ['SimpleUploadAdapter'],
        'toolbar': [
            "undo", "redo",
            '|',
            'heading',
            'bold', 'italic',
            'fontColor',
            'numberedList', 'bulletedList',
            'alignment',
            'insertTable',
            '|',
            'link', 'insertImage', 'fileUpload',
            'htmlEmbed',
            'MediaEmbed'
        ],
        'language': 'fr',
        'alignment': {
            'options': ['left', 'center', 'right', 'justify']
        },
        'fontColor': _FONT_COLOR,
        'link': _LINK_DECORATORS,
        'heading': {
            'options': _HEADING_OPTIONS,
        },
        'image': {
            'styles': ['block', 'alignLeft', 'alignRight'],
            'toolbar': [
                'imageTextAlternative',
                'imageStyle:block',
                'imageStyle:alignLeft',
                'imageStyle:alignRight',
            ],
            'insert': {
                'type': 'block',
            }
        },
        'htmlEmbed': {
            'sanitizeHtml': False
        },
        'mediaEmbed': {
            'previewsInData': False,
        },
        'table': _TABLE_TOOLBAR,
    },
    'light': {
        'licenseKey': 'GPL',
        'toolbar': ['bulletedList'],
        'language': 'fr',
        'removePlugins': ['ImageToolbar'],
    },
    'description_only': {
        'licenseKey': 'GPL',
        'toolbar': [''],
        'language': 'fr',
        'removePlugins': ['ImageToolbar'],
    },
    'lightandlink': {
        'licenseKey': 'GPL',
        'toolbar': ['bulletedList', 'link'],
        'language': 'fr',
        'removePlugins': ['ImageToolbar'],
        'link': _LINK_DECORATORS,
    },
}
