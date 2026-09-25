# elixir_toolkit/nir.py
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class NIRValidator:
    """Valide un numéro de sécurité sociale français (NIR).

    Format attendu : 15 chiffres (ex: 123456789012345).
    Structure :
    - Position 1 : Sexe (1=masculin, 2=féminin)
    - Positions 2-3 : Année de naissance (modulo 100)
    - Positions 4-5 : Mois de naissance (01-12)
    - Positions 6-7 : Département de naissance (01-95 pour métropole, 97-98 pour les outre-mers)
    - Positions 8-10 : Commune de naissance
    - Positions 11-13 : Ordre de naissance dans le mois
    - Positions 14-15 : Clé de contrôle (97 - (NIR_sans_clé % 97))

    La validation vérifie :
    - La longueur (15 caractères)
    - Que tous les caractères sont des chiffres
    - La validité de la clé de contrôle
    - Optionnellement, la cohérence du mois et du département
    """

    def __init__(self, validate_date=True, validate_location=True):
        self.validate_date = validate_date
        self.validate_location = validate_location

    def __call__(self, value):
        if value is None:
            raise ValidationError("Le numéro de sécurité sociale est obligatoire.")

        # Nettoyer la valeur (supprimer espaces et tirets)
        cleaned_value = str(value).replace(" ", "").replace("-", "")

        # Vérifier la longueur
        if len(cleaned_value) != 15:
            raise ValidationError(
                "Le numéro de sécurité sociale doit contenir exactement 15 chiffres."
            )

        # Vérifier que tous les caractères sont des chiffres
        if not cleaned_value.isdigit():
            raise ValidationError(
                "Le numéro de sécurité sociale ne doit contenir que des chiffres."
            )

        # Vérifier la clé de contrôle
        nir_without_key = cleaned_value[:13]
        key = cleaned_value[13:]

        try:
            computed_key = 97 - (int(nir_without_key) % 97)
        except ValueError:
            raise ValidationError(
                "Impossible de calculer la clé de contrôle. Vérifiez le format du numéro."
            )

        if computed_key != int(key):
            raise ValidationError("La clé de contrôle du numéro de sécurité sociale est invalide.")

        # Vérification optionnelle de la date
        if self.validate_date:
            self._validate_date(cleaned_value)

        # Vérification optionnelle du lieu
        if self.validate_location:
            self._validate_location(cleaned_value)

    def _validate_date(self, value):
        """Valide le sexe, l'année et le mois de naissance."""
        sexe = value[0]
        year_str = value[1:3]
        month_str = value[3:5]

        # Vérifier le sexe
        if sexe not in ('1', '2'):
            raise ValidationError("Le premier chiffre doit être 1 (masculin) ou 2 (féminin).")

        # Vérifier le mois (01-12)
        try:
            month = int(month_str)
        except ValueError:
            raise ValidationError("Le mois de naissance est invalide.")

        if month < 1 or month > 12:
            raise ValidationError("Le mois de naissance doit être compris entre 01 et 12.")

    def _validate_location(self, value):
        """Valide le département de naissance."""
        department_str = value[5:7]

        try:
            department = int(department_str)
        except ValueError:
            raise ValidationError("Le département de naissance est invalide.")

        # Départements métropolitains : 01-95 (sauf 20A, 20B qui sont 2A, 2B)
        # Outre-mers : 97-98
        # Notes :
        # - 20A et 20B n'existent pas en NIR (ce sont 2A et 2B)
        # - 97 = DOM (Guadeloupe, Martinique, Guyane, Réunion)
        # - 98 = COM (Polynésie française, Nouvelle-Calédonie, etc.)
        # - 99 = étrangers nés à l'étranger

        # Départements valides : 01-95 (sauf 20), 97, 98, 99
        if department == 20:
            raise ValidationError("Le département 20 n'existe pas (utilisez 2A ou 2B).")

        if not (1 <= department <= 95 or department == 97 or department == 98 or department == 99):
            raise ValidationError(
                "Le département de naissance est invalide. Doit être compris entre 01 et 95, "
                "ou 97, 98 pour les outre-mers, ou 99 pour les étrangers nés à l'étranger."
            )
