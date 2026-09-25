# elixir_toolkit/validators/__init__.py
from html import unescape
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.utils.html import strip_tags
from django.utils.deconstruct import deconstructible


# Import NIRValidator from the nir submodule
from .nir import NIRValidator


# Import IBAN validators
from .iban import (
    IBANValidator,
    FrenchIBANValidator,
    is_valid_iban,
    get_iban_country,
    get_iban_check_digits,
)

# Import file validators
from .file_validators import (
    MaxFileSizeValidator,
    MaxTotalSizeValidator,
    AllowedExtensionsValidator,
    MaxFilesValidator,
)


@deconstructible
class TextMaxLengthValidator(MaxLengthValidator):
    """Limite un texte brut à `limit_value` caractères.

    Les navigateurs envoient les retours à la ligne d'un textarea en CRLF
    mais les comptent pour un seul caractère (attribut `maxlength`) :
    on les compte de la même façon.
    """

    def clean(self, x):
        return len(x.replace("\r\n", "\n"))


@deconstructible
class RichTextMaxLengthValidator(MaxLengthValidator):
    """Limite un contenu HTML (CKEditor) à `limit_value` caractères visibles.

    Les balises sont ignorées et une entité (`&amp;`, `&nbsp;`...) compte pour
    un caractère, comme le compteur affiché sous l'éditeur.
    """

    def clean(self, x):
        return len(unescape(strip_tags(x)))
