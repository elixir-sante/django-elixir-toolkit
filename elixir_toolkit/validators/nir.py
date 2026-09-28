# elixir_toolkit/nir.py
import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


_NIR_REGEX = re.compile(
    r'^(?P<sexe>[0-9])'
    r'(?P<annee>[0-9]{2})'
    r'(?P<mois>[0-9]{2})'
    r'(?P<dept>[0-9]{2}|2[AB])'
    r'(?P<commune>[0-9]{3})'
    r'(?P<ordre>[0-9]{3})'
    r'(?P<cle>[0-9]{2})$'
)

# Pour le calcul de la clé, 2A et 2B sont remplacés par 19 et 18
_CORSICA_KEY_SUBSTITUTION = {'2A': '19', '2B': '18'}


@deconstructible
class NIRValidator:
    """Valide un numéro de sécurité sociale français (NIR).

    Format : 15 caractères (ex : 1 85 05 78 006 084 36).
    Structure :
    - Position 1 : Sexe (1 = masculin, 2 = féminin ; 7/8 = NIA provisoire si autorisé)
    - Positions 2-3 : Année de naissance (modulo 100)
    - Positions 4-5 : Mois de naissance (01-12, ou mois fictifs si strict_month=False)
    - Positions 6-7 : Département (01-99, 2A/2B pour la Corse depuis 1976,
                    20 pour la Corse avant 1976, 97/98 outre-mer, 99 étranger)
    - Positions 8-10 : Commune de naissance (ou pays si né à l'étranger)
    - Positions 11-13 : Numéro d'ordre (001-999)
    - Positions 14-15 : Clé de contrôle = 97 - (NIR_sans_clé % 97)

    Les espaces, tirets et points sont ignorés.
    Les valeurs vides ne sont pas validées (c'est le rôle de blank/required).
    """

    def __init__(self, validate_date=True, validate_location=True,
                allow_temporary=False, strict_month=True):
        self.validate_date = validate_date
        self.validate_location = validate_location
        self.allow_temporary = allow_temporary
        self.strict_month = strict_month

    def __call__(self, value):
        if value is None or value == '':
            return

        cleaned = re.sub(r'[\s\-.]', '', str(value)).upper()

        if len(cleaned) != 15:
            raise ValidationError(
                "Le numéro de sécurité sociale doit contenir exactement 15 caractères.",
                code='nir_length',
            )

        match = _NIR_REGEX.match(cleaned)
        if not match:
            raise ValidationError(
                "Le numéro de sécurité sociale ne doit contenir que des chiffres "
                "(ou 2A/2B pour le département corse).",
                code='nir_format',
            )

        parts = match.groupdict()

        # Clé de contrôle
        dept_for_key = _CORSICA_KEY_SUBSTITUTION.get(parts['dept'], parts['dept'])
        numeric = cleaned[:5] + dept_for_key + cleaned[7:13]
        computed_key = 97 - (int(numeric) % 97)

        if computed_key != int(parts['cle']):
            raise ValidationError(
                "La clé de contrôle du numéro de sécurité sociale est invalide.",
                code='nir_key',
            )

        if self.validate_date:
            self._validate_sex_and_date(parts)

        if self.validate_location:
            self._validate_location(parts)

    def _validate_sex_and_date(self, parts):
        """Valide le sexe et le mois de naissance."""
        allowed_sexes = ('1', '2', '7', '8') if self.allow_temporary else ('1', '2')
        if parts['sexe'] not in allowed_sexes:
            raise ValidationError(
                "Le premier chiffre doit être 1 (masculin) ou 2 (féminin).",
                code='nir_sex',
            )

        month = int(parts['mois'])
        valid_month = 1 <= month <= 12
        if not self.strict_month:
            # Mois fictifs attribués quand l'état civil est incomplet
            valid_month = valid_month or 20 <= month <= 42 or 50 <= month <= 99

        if not valid_month:
            raise ValidationError(
                "Le mois de naissance doit être compris entre 01 et 12.",
                code='nir_month',
            )

    def _validate_location(self, parts):
        """Valide le département et le numéro d'ordre."""
        dept = parts['dept']
        if dept not in _CORSICA_KEY_SUBSTITUTION and not 1 <= int(dept) <= 99:
            raise ValidationError(
                "Le département de naissance est invalide.",
                code='nir_department',
            )

        if parts['ordre'] == '000':
            raise ValidationError(
                "Le numéro d'ordre de naissance est invalide.",
                code='nir_order',
            )

    def __eq__(self, other):
        return (
            type(self) is type(other) and
            self.validate_date == other.validate_date and
            self.validate_location == other.validate_location and
            self.allow_temporary == other.allow_temporary and
            self.strict_month == other.strict_month
        )

    def __hash__(self):
        return hash((type(self), self.validate_date, self.validate_location,
                    self.allow_temporary, self.strict_month))