"""Validateur et normalisation des numéros de téléphone français pour Django.

Formats acceptés (espaces, tirets et points ignorés) :
- National : 06 12 34 56 78, 01-23-45-67-89, 0612345678
- International : +33 6 12 34 56 78, +33612345678, 0033612345678

Les valeurs vides ne sont pas validées (c'est le rôle de blank/required).

Les validators Django ne peuvent pas modifier la valeur soumise : ils ne font
que lever une ValidationError. Pour réécrire un numéro (+33... -> 06...),
utiliser `normalize_french_phone_number` dans `Form.clean_<champ>()`,
`Model.clean()` ou `Model.save()`.
"""

import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

# Séparateurs tolérés entre les groupes de chiffres
_PHONE_SEPARATORS = re.compile(r'[\s\-.()]')

# Numéro français après normalisation : 0 suivi de 9 chiffres,
# le second chiffre identifie le type (1-5 fixe, 6-7 mobile, 8-9 spécial)
_FRENCH_PHONE_REGEX = re.compile(r'^0[1-9]\d{8}$')

# Pattern HTML5 (attribut `pattern`) pour la validation navigateur.
# Accepte les mêmes formats que FrenchPhoneNumberValidator : 06...,
# +33 6..., 0033 6..., 33..., avec espaces, tirets ou points.
# Le regex d'un attribut `pattern` est implicitement ancré (^...$) ;
# le message affiché vient de l'attribut `title`.
FRENCH_PHONE_INPUT_PATTERN = r'(?:0033|\+?33|0)\s*[1-9](?:[\s\-.]*\d{2}){4}'

# Message d'aide par défaut pour l'attribut `title` du champ téléphone
FRENCH_PHONE_INPUT_TITLE = (
    'Numéro français : 06 12 34 56 78, +33 6 12 34 56 78, 0033 6 12 34 56 78...'
)


def normalize_french_phone_number(value):
    """Normalise un numéro de téléphone français au format national à 10 chiffres.

    +33 6 12 34 56 78 -> 0612345678
    0033 6 12 34 56 78 -> 0612345678
    06 12 34 56 78 -> 0612345678

    Lève une ValidationError si le numéro n'est pas un numéro français valide.
    Retourne None si la valeur est vide.
    """
    if value is None or value == '':
        return None
    digits = _PHONE_SEPARATORS.sub('', str(value))
    if digits.startswith('00'):
        digits = '+' + digits[2:]
    if digits.startswith('+33'):
        digits = '0' + digits[3:]
    elif digits.startswith('33') and len(digits) == 11:
        digits = '0' + digits[2:]
    if not _FRENCH_PHONE_REGEX.match(digits):
        raise ValidationError(
            "%(value)s n'est pas un numéro de téléphone français valide.",
            code='invalid_phone',
            params={'value': value},
        )
    return digits


@deconstructible
class FrenchPhoneNumberValidator:
    """Valide un numéro de téléphone français (fixe ou mobile).

    Accepte les formats national (06...) et international (+33 6..., 0033 6...),
    avec espaces, tirets ou points comme séparateurs.

    Pour stocker le numéro normalisé (un +33 devient 06...), utiliser
    `normalize_french_phone_number` plutôt que ce validateur.
    """

    message = "%(value)s n'est pas un numéro de téléphone français valide."
    code = 'invalid_phone'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        if value is None or value == '':
            return
        digits = _PHONE_SEPARATORS.sub('', str(value))
        if digits.startswith('00'):
            digits = '+' + digits[2:]
        if digits.startswith('+33'):
            digits = '0' + digits[3:]
        elif digits.startswith('33') and len(digits) == 11:
            digits = '0' + digits[2:]
        if not _FRENCH_PHONE_REGEX.match(digits):
            raise ValidationError(
                self.message,
                code=self.code,
                params={'value': value},
            )

    def __eq__(self, other):
        return (
            isinstance(other, FrenchPhoneNumberValidator) and
            self.message == other.message and
            self.code == other.code
        )

    def __hash__(self):
        return hash((type(self), self.message, self.code))
