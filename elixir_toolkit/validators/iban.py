"""
Validator IBAN (International Bank Account Number) pour Django.

Ce module fournit des validators pour la validation des IBAN
selon la norme ISO 13616-1:2007.
"""

import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


IBAN_MIN_LENGTH = 15  # Norvège, le plus court du registre
IBAN_MAX_LENGTH = 34  # Maximum fixé par la norme

# Spécifications IBAN par pays : {code_pays: (longueur, regex_format_bban)}
# Basé sur le registre SWIFT IBAN (https://www.swift.com/standards/data-standards/iban)
_FR_BBAN = r'[0-9]{10}[0-9A-Z]{11}[0-9]{2}'
IBAN_COUNTRY_SPEC = {
    # France
    'FR': (27, _FR_BBAN),
    # Territoires français : en pratique les banques émettent des IBAN "FR",
    # ces codes sont conservés pour compatibilité avec d'anciens IBAN.
    'GF': (27, _FR_BBAN),  # Guyane française
    'GP': (27, _FR_BBAN),  # Guadeloupe
    'MQ': (27, _FR_BBAN),  # Martinique
    'RE': (27, _FR_BBAN),  # La Réunion
    'YT': (27, _FR_BBAN),  # Mayotte
    'PM': (27, _FR_BBAN),  # Saint-Pierre-et-Miquelon
    'WF': (27, _FR_BBAN),  # Wallis-et-Futuna
    'PF': (27, _FR_BBAN),  # Polynésie française
    'NC': (27, _FR_BBAN),  # Nouvelle-Calédonie
    # Monaco
    'MC': (27, _FR_BBAN),
    # Andorre
    'AD': (24, r'[0-9]{8}[A-Z0-9]{12}'),
    # Belgique
    'BE': (16, r'[0-9]{12}'),
    # Allemagne
    'DE': (22, r'[0-9]{18}'),
    # Suisse et Liechtenstein
    'CH': (21, r'[0-9]{5}[A-Z0-9]{12}'),
    'LI': (21, r'[0-9]{5}[A-Z0-9]{12}'),
    # Royaume-Uni
    'GB': (22, r'[A-Z]{4}[0-9]{14}'),
    # Gibraltar
    'GI': (23, r'[A-Z]{4}[A-Z0-9]{15}'),
    # Espagne
    'ES': (24, r'[0-9]{20}'),
    # Italie, Saint-Marin, Vatican
    'IT': (27, r'[A-Z][0-9]{10}[A-Z0-9]{12}'),
    'SM': (27, r'[A-Z][0-9]{10}[A-Z0-9]{12}'),
    'VA': (22, r'[0-9]{18}'),
    # Pays-Bas
    'NL': (18, r'[A-Z]{4}[0-9]{10}'),
    # Luxembourg
    'LU': (20, r'[0-9]{3}[A-Z0-9]{13}'),
    # Suède
    'SE': (24, r'[0-9]{20}'),
    # Norvège
    'NO': (15, r'[0-9]{11}'),
    # Danemark
    'DK': (18, r'[0-9]{14}'),
    # Finlande
    'FI': (18, r'[0-9]{14}'),
    # Autriche
    'AT': (20, r'[0-9]{16}'),
    # Pologne
    'PL': (28, r'[0-9]{24}'),
    # Portugal
    'PT': (25, r'[0-9]{21}'),
    # Irlande (code banque : 4 lettres)
    'IE': (22, r'[A-Z]{4}[0-9]{14}'),
    # Chypre
    'CY': (28, r'[0-9]{8}[A-Z0-9]{16}'),
    # Grèce
    'GR': (27, r'[0-9]{7}[A-Z0-9]{16}'),
    # République tchèque
    'CZ': (24, r'[0-9]{20}'),
    # Hongrie
    'HU': (28, r'[0-9]{24}'),
    # Roumanie
    'RO': (24, r'[A-Z]{4}[A-Z0-9]{16}'),
    # Bulgarie
    'BG': (22, r'[A-Z]{4}[0-9]{6}[A-Z0-9]{8}'),
    # Croatie
    'HR': (21, r'[0-9]{17}'),
    # Slovaquie
    'SK': (24, r'[0-9]{20}'),
    # Slovénie
    'SI': (19, r'[0-9]{15}'),
    # Lituanie
    'LT': (20, r'[0-9]{16}'),
    # Lettonie
    'LV': (21, r'[A-Z]{4}[A-Z0-9]{13}'),
    # Estonie
    'EE': (20, r'[0-9]{16}'),
    # Malte
    'MT': (31, r'[A-Z]{4}[0-9]{5}[A-Z0-9]{18}'),
    # Islande
    'IS': (26, r'[0-9]{22}'),
    # Israël
    'IL': (23, r'[0-9]{19}'),
    # Turquie (5 chiffres banque + 1 chiffre réservé + 16 alphanum.)
    'TR': (26, r'[0-9]{6}[A-Z0-9]{16}'),
    # Russie
    'RU': (33, r'[0-9]{14}[A-Z0-9]{15}'),
    # Ukraine
    'UA': (29, r'[0-9]{6}[A-Z0-9]{19}'),
    # Tunisie
    'TN': (24, r'[0-9]{20}'),
    # Arabie saoudite
    'SA': (24, r'[0-9]{2}[A-Z0-9]{18}'),
    # Émirats arabes unis
    'AE': (23, r'[0-9]{19}'),
    # Qatar
    'QA': (29, r'[A-Z]{4}[A-Z0-9]{21}'),
    # Koweït
    'KW': (30, r'[A-Z]{4}[A-Z0-9]{22}'),
    # Bahreïn
    'BH': (22, r'[A-Z]{4}[A-Z0-9]{14}'),
    # Jordanie (4 lettres + 4 chiffres + 18 alphanum.)
    'JO': (30, r'[A-Z]{4}[0-9]{4}[A-Z0-9]{18}'),
    # Liban
    'LB': (28, r'[0-9]{4}[A-Z0-9]{20}'),
    # Égypte
    'EG': (29, r'[0-9]{25}'),
    # Brésil
    'BR': (29, r'[0-9]{23}[A-Z][A-Z0-9]'),
}


def _normalize_iban(iban):
    """
    Normalise une chaîne IBAN : majuscules, suppression des espaces
    (y compris insécables) et des tirets. Les autres caractères sont
    conservés pour être rejetés par la validation.
    """
    if iban is None:
        return ''
    return re.sub(r'[\s\-]', '', str(iban)).upper()


def validate_iban_structure(iban):
    """
    Valide la structure de base d'un IBAN :
    - uniquement des caractères A-Z / 0-9
    - longueur entre 15 et 34 caractères
    - 2 lettres (code pays) puis 2 chiffres de contrôle compris entre 02 et 98
    """
    iban = _normalize_iban(iban)

    if not iban:
        raise ValidationError("L'IBAN ne peut pas être vide.", code='iban_empty')

    if not re.fullmatch(r'[A-Z0-9]+', iban):
        raise ValidationError(
            "L'IBAN ne doit contenir que des lettres et des chiffres.",
            code='iban_invalid_characters',
        )

    if len(iban) < IBAN_MIN_LENGTH:
        raise ValidationError(
            "L'IBAN est trop court (%(min)d caractères minimum).",
            code='iban_too_short',
            params={'min': IBAN_MIN_LENGTH},
        )

    if len(iban) > IBAN_MAX_LENGTH:
        raise ValidationError(
            "L'IBAN est trop long (%(max)d caractères maximum).",
            code='iban_too_long',
            params={'max': IBAN_MAX_LENGTH},
        )

    country_code = iban[:2]
    if not country_code.isalpha():
        raise ValidationError(
            "L'IBAN doit commencer par un code pays de 2 lettres.",
            code='iban_invalid_country',
        )

    check_digits = iban[2:4]
    if not check_digits.isdigit():
        raise ValidationError(
            "Les caractères 3-4 de l'IBAN doivent être des chiffres de contrôle (0-9).",
            code='iban_invalid_check_digits',
        )

    # 00, 01 et 99 ne sont jamais émis : 01 ≡ 98 et 00 ≡ 97 (mod 97),
    # ils passeraient donc le MOD-97 à tort.
    if not 2 <= int(check_digits) <= 98:
        raise ValidationError(
            "Les chiffres de contrôle de l'IBAN doivent être compris entre 02 et 98.",
            code='iban_invalid_check_digits',
        )

    return iban, country_code


def validate_iban_check_digits(iban, country_code=None):
    """
    Valide les chiffres de contrôle de l'IBAN avec l'algorithme MOD-97 :
    les 4 premiers caractères passent à la fin, les lettres sont converties
    (A=10 ... Z=35), et le nombre obtenu modulo 97 doit valoir 1.
    """
    rearranged = iban[4:] + iban[:4]
    numeric = ''.join(str(int(char, 36)) for char in rearranged)

    if int(numeric) % 97 != 1:
        raise ValidationError(
            "Les chiffres de contrôle de l'IBAN sont invalides.",
            code='iban_checksum',
        )


def validate_iban_country_length(iban, country_code):
    """Valide que la longueur de l'IBAN correspond à celle attendue pour le pays."""
    if country_code in IBAN_COUNTRY_SPEC:
        expected_length, _ = IBAN_COUNTRY_SPEC[country_code]
        if len(iban) != expected_length:
            raise ValidationError(
                "La longueur de l'IBAN pour le pays %(country)s doit être de "
                "%(expected)d caractères, mais %(found)d ont été trouvés.",
                code='iban_length',
                params={
                    'country': country_code,
                    'expected': expected_length,
                    'found': len(iban),
                },
            )


def validate_iban_country_format(iban, country_code):
    """Valide que le BBAN (tout ce qui suit les 4 premiers caractères) respecte le format du pays."""
    if country_code in IBAN_COUNTRY_SPEC:
        _, bban_pattern = IBAN_COUNTRY_SPEC[country_code]
        if not re.fullmatch(bban_pattern, iban[4:]):
            raise ValidationError(
                "Le format de l'IBAN pour le pays %(country)s est invalide.",
                code='iban_format',
                params={'country': country_code},
            )


@deconstructible
class IBANValidator:
    """
    Validator pour IBAN (International Bank Account Number).

    Valide :
    1. La structure de base (caractères, longueur, code pays, chiffres de contrôle)
    2. Le pays (liste autorisée, pays connu)
    3. La longueur spécifique au pays
    4. Le format BBAN spécifique au pays (optionnel)
    5. Les chiffres de contrôle (algorithme MOD-97)

    Utilisation :
        from elixir_toolkit.validators import IBANValidator

        class MonModele(models.Model):
            iban = models.CharField(max_length=34, validators=[IBANValidator()])

        # Avec options :
        iban = models.CharField(
            max_length=34,
            validators=[IBANValidator(
                validate_length=True,
                validate_format=True,
                allowed_countries=['FR', 'BE'],
            )]
        )
    """

    message = "Veuillez entrer un IBAN valide."
    message_country = "Le code pays %(country)s n'est pas pris en charge."
    message_country_not_allowed = "Les IBAN du pays %(country)s ne sont pas acceptés."

    code = 'invalid_iban'

    def __init__(self, validate_length=True, validate_format=False,
                allowed_countries=None, allow_unknown_countries=False):
        """
        Args:
            validate_length: vérifie la longueur attendue pour le pays.
            validate_format: vérifie le BBAN avec la regex du pays.
            allowed_countries: codes ISO à 2 lettres autorisés (insensible à la casse).
                            None = tous les pays de IBAN_COUNTRY_SPEC.
            allow_unknown_countries: si True, un pays absent de IBAN_COUNTRY_SPEC
                                    est accepté (seul le MOD-97 est alors vérifié).
        """
        self.validate_length = validate_length
        self.validate_format = validate_format
        self.allowed_countries = (
            [c.upper() for c in allowed_countries] if allowed_countries is not None else None
        )
        self.allow_unknown_countries = allow_unknown_countries

    def __call__(self, value):
        iban = _normalize_iban(value)

        if not iban:
            raise ValidationError(self.message, code=self.code)

        iban, country_code = validate_iban_structure(iban)

        if self.allowed_countries is not None and country_code not in self.allowed_countries:
            raise ValidationError(
                self.message_country_not_allowed,
                code='iban_country_not_allowed',
                params={'country': country_code},
            )

        known_country = country_code in IBAN_COUNTRY_SPEC
        if not known_country and not self.allow_unknown_countries:
            raise ValidationError(
                self.message_country,
                code='iban_unknown_country',
                params={'country': country_code},
            )

        if known_country and self.validate_length:
            validate_iban_country_length(iban, country_code)

        if known_country and self.validate_format:
            validate_iban_country_format(iban, country_code)

        validate_iban_check_digits(iban, country_code)

    def __eq__(self, other):
        return (
            type(self) is type(other) and
            self.validate_length == other.validate_length and
            self.validate_format == other.validate_format and
            self.allowed_countries == other.allowed_countries and
            self.allow_unknown_countries == other.allow_unknown_countries
        )

    def __hash__(self):
        return hash((
            type(self), self.validate_length, self.validate_format,
            tuple(self.allowed_countries) if self.allowed_countries is not None else None,
            self.allow_unknown_countries,
        ))

    def __repr__(self):
        return (
            f"{type(self).__name__}(validate_length={self.validate_length}, "
            f"validate_format={self.validate_format}, "
            f"allowed_countries={self.allowed_countries}, "
            f"allow_unknown_countries={self.allow_unknown_countries})"
        )


@deconstructible
class FrenchIBANValidator(IBANValidator):
    """
    Validator spécifique pour les IBAN français.

    Les IBAN français comptent 27 caractères et commencent par 'FR'.
    Longueur et format BBAN sont vérifiés.
    """

    message = "Veuillez entrer un IBAN français valide."
    message_country_not_allowed = "Seuls les IBAN français (FR) sont acceptés."
    code = 'invalid_french_iban'

    def __init__(self):
        super().__init__(
            validate_length=True,
            validate_format=True,
            allowed_countries=['FR'],
        )


def is_valid_iban(iban, allowed_countries=None):
    """Retourne True si l'IBAN est valide, False sinon."""
    try:
        IBANValidator(
            validate_length=True,
            validate_format=False,
            allowed_countries=allowed_countries,
        )(iban)
        return True
    except ValidationError:
        return False


def get_iban_country(iban):
    """Retourne le code pays à 2 lettres d'un IBAN, ou None si invalide."""
    iban = _normalize_iban(iban)
    if len(iban) >= 2 and re.fullmatch(r'[A-Z]{2}', iban[:2]):
        return iban[:2]
    return None


def get_iban_check_digits(iban):
    """Retourne les 2 chiffres de contrôle d'un IBAN, ou None si invalide."""
    iban = _normalize_iban(iban)
    if len(iban) >= 4 and re.fullmatch(r'[A-Z]{2}[0-9]{2}', iban[:4]):
        return iban[2:4]
    return None
