"""
Validator IBAN (International Bank Account Number) pour Django.

Ce module fournit des validators pour la validation des IBAN
selon la norme ISO 13616-1:2007.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


# Spécifications IBAN par pays : {code_pays: (longueur, regex_format_bban)}
# Basé sur le registre SWIFT IBAN (https://www.swift.com/standards/data-standards/iban)
IBAN_COUNTRY_SPEC = {
    # France et territoires français
    'FR': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),
    'GF': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),  # Guyane française
    'GP': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),  # Guadeloupe
    'MQ': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),  # Martinique
    'RE': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),  # La Réunion
    'YT': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),  # Mayotte
    'MC': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),  # Monaco
    'PM': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),  # Saint-Pierre-et-Miquelon
    'WF': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),  # Wallis-et-Futuna
    'PF': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),  # Polynésie française
    'NC': (23, r'^[0-9]{10}[0-9A-Z]{11}$'),  # Nouvelle-Calédonie
    # Belgique
    'BE': (16, r'^[0-9]{12}$'),
    # Allemagne
    'DE': (22, r'^[0-9]{18}$'),
    # Suisse et Liechtenstein
    'CH': (21, r'^[0-9]{5}[A-Z0-9]{12}$'),
    'LI': (21, r'^[0-9]{5}[A-Z0-9]{12}$'),
    # Royaume-Uni
    'GB': (22, r'^[A-Z]{4}[0-9]{14}$'),
    # Espagne
    'ES': (24, r'^[0-9]{20}$'),
    # Italie
    'IT': (27, r'^[A-Z][0-9]{10}[A-Z0-9]{16}$'),
    # Pays-Bas
    'NL': (18, r'^[A-Z]{4}[0-9]{14}$'),
    # Luxembourg
    'LU': (20, r'^[0-9]{3}[A-Z0-9]{17}$'),
    # Suède
    'SE': (24, r'^[0-9]{21}$'),
    # Norvège
    'NO': (15, r'^[0-9]{11}$'),
    # Danemark
    'DK': (18, r'^[0-9]{14}$'),
    # Finlande
    'FI': (18, r'^[0-9]{14}$'),
    # Autriche
    'AT': (20, r'^[0-9]{16}$'),
    # Pologne
    'PL': (28, r'^[0-9]{24}$'),
    # Portugal
    'PT': (25, r'^[0-9]{21}$'),
    # Irlande
    'IE': (22, r'^[A-Z0-9]{4}[0-9]{14}$'),
    # Chypre
    'CY': (28, r'^[0-9]{8}[A-Z0-9]{16}$'),
    # Grèce
    'GR': (27, r'^[0-9]{7}[A-Z0-9]{16}$'),
    # République tchèque
    'CZ': (24, r'^[0-9]{20}$'),
    # Hongrie
    'HU': (28, r'^[0-9]{24}$'),
    # Roumanie
    'RO': (24, r'^[A-Z]{4}[A-Z0-9]{16}$'),
    # Bulgarie
    'BG': (22, r'^[A-Z]{4}[0-9]{6}[A-Z0-9]{8}$'),
    # Croatie
    'HR': (21, r'^[0-9]{17}$'),
    # Slovaquie
    'SK': (24, r'^[0-9]{20}$'),
    # Slovénie
    'SI': (19, r'^[0-9]{15}$'),
    # Lituanie
    'LT': (20, r'^[0-9]{16}$'),
    # Lettonie
    'LV': (21, r'^[A-Z]{4}[A-Z0-9]{13}$'),
    # Estonie
    'EE': (20, r'^[0-9]{16}$'),
    # Malte
    'MT': (31, r'^[A-Z]{4}[0-9]{5}[A-Z0-9]{18}$'),
    # Islande
    'IS': (26, r'^[0-9]{22}$'),
    # Israël
    'IL': (23, r'^[0-9]{19}$'),
    # Turquie
    'TR': (26, r'^[0-9]{5}[A-Z0-9]{17}$'),
    # Russie
    'RU': (23, r'^[0-9][0-9A-Z]{22}$'),
    # Ukraine
    'UA': (29, r'^[0-9]{6}[A-Z0-9]{19}$'),
    # Maroc
    'MA': (28, r'^[0-9]{24}$'),
    # Algérie
    'DZ': (24, r'^[0-9]{20}$'),
    # Tunisie
    'TN': (24, r'^[0-9]{20}$'),
    # Arabie saoudite
    'SA': (24, r'^[0-9]{2}[A-Z0-9]{18}$'),
    # Émirats arabes unis
    'AE': (23, r'^[0-9]{19}$'),
    # Qatar
    'QA': (29, r'^[A-Z0-9]{4}[A-Z0-9]{21}$'),
    # Koweït
    'KW': (30, r'^[A-Z]{4}[0-9]{22}$'),
    # Bahreïn
    'BH': (22, r'^[A-Z]{4}[A-Z0-9]{14}$'),
    # Jordanie
    'JO': (30, r'^[A-Z]{4}[0-9]{22}$'),
    # Liban
    'LB': (28, r'^[0-9]{4}[A-Z0-9]{20}$'),
    # Égypte
    'EG': (29, r'^[0-9]{4}[A-Z0-9]{21}$'),
    # Canada (utilisation pseudo-IBAN pour usage national)
    'CA': (29, r'^[0-9]{25}$'),
    # Australie (utilisation pseudo-IBAN)
    'AU': (31, r'^[0-9]{27}$'),
    # Brésil (utilisation pseudo-IBAN)
    'BR': (29, r'^[0-9]{8}[0-9A-Z]{20}$'),
}


def _normalize_iban(iban):
    """
    Normalise une chaîne IBAN en :
    1. Convertissant en majuscules
    2. Supprimant tous les espaces et caractères spéciaux
    """
    if not iban:
        return ''
    # Convertir en majuscules et supprimer les caractères non alphanumériques
    normalized = re.sub(r'[^A-Z0-9]', '', iban.upper())
    return normalized


def _mod97(data):
    """
    Calcule le MOD-97 d'une représentation sous forme de chaîne d'un nombre.
    C'est l'algorithme utilisé pour la validation IBAN.
    """
    # Convertir les lettres en nombres (A=10, B=11, ..., Z=35)
    numeric = []
    for char in data:
        if char.isdigit():
            numeric.append(int(char))
        else:
            # Convertir la lettre en sa valeur numérique (A=10, B=11, etc.)
            value = ord(char) - ord('A') + 10
            numeric.extend([int(d) for d in str(value)])
    
    # Traiter le nombre par blocs pour le calcul MOD-97
    # Utiliser l'algorithme : traiter 9 chiffres à la fois
    remainder = 0
    for i in range(0, len(numeric), 9):
        chunk = numeric[i:i+9]
        # Compléter avec des zéros si nécessaire
        while len(chunk) < 9:
            chunk.insert(0, 0)
        # Convertir en entier
        num = int(''.join(map(str, chunk)))
        # Calculer le reste
        remainder = (remainder * (10 ** len(chunk)) + num) % 97
    
    return remainder


def validate_iban_structure(iban):
    """
    Valide la structure de base d'un IBAN :
    - Doit contenir au moins 4 caractères (code pays + chiffres de contrôle)
    - Doit commencer par 2 lettres (code pays)
    - Doit avoir 2 chiffres suivant le code pays (chiffres de contrôle)
    """
    iban = _normalize_iban(iban)
    
    if not iban:
        raise ValidationError("L'IBAN ne peut pas être vide.")
    
    if len(iban) < 4:
        raise ValidationError("L'IBAN est trop court. La longueur minimale est de 4 caractères.")
    
    # Vérifier le code pays (les 2 premiers caractères doivent être des lettres)
    country_code = iban[:2]
    if not country_code.isalpha():
        raise ValidationError("L'IBAN doit commencer par un code pays de 2 lettres.")
    
    # Vérifier les chiffres de contrôle (les 2 caractères suivants doivent être des chiffres)
    check_digits = iban[2:4]
    if not check_digits.isdigit():
        raise ValidationError("Les caractères 3-4 de l'IBAN doivent être des chiffres de contrôle (0-9).")
    
    return iban, country_code


def validate_iban_check_digits(iban, country_code):
    """
    Valide les chiffres de contrôle de l'IBAN en utilisant l'algorithme MOD-97.
    """
    # Déplacer les 4 premiers caractères à la fin
    rearranged = iban[4:] + iban[:4]
    
    # Convertir en représentation numérique
    # Remplacer les lettres par leurs valeurs numériques (A=10, B=11, ..., Z=35)
    numeric_str = ''
    for char in rearranged:
        if char.isdigit():
            numeric_str += char
        else:
            value = ord(char) - ord('A') + 10
            numeric_str += str(value)
    
    # Le résultat doit être divisible par 97 (reste = 1)
    # En réalité, l'IBAN est valide si MOD-97 de la chaîne réarrangée vaut 1
    remainder = int(numeric_str) % 97
    
    if remainder != 1:
        raise ValidationError("Les chiffres de contrôle de l'IBAN sont invalides.")


def validate_iban_country_length(iban, country_code):
    """
    Valide que la longueur de l'IBAN correspond à la longueur attendue pour le pays.
    """
    if country_code in IBAN_COUNTRY_SPEC:
        expected_length, _ = IBAN_COUNTRY_SPEC[country_code]
        if len(iban) != expected_length:
            raise ValidationError(
                "La longueur de l'IBAN pour le pays %s doit être de %d caractères, mais %d ont été trouvés." % (
                    country_code,
                    expected_length,
                    len(iban)
                )
            )


def validate_iban_country_format(iban, country_code):
    """
    Valide que l'IBAN correspond au format BBAN du pays.
    """
    if country_code in IBAN_COUNTRY_SPEC:
        _, bban_pattern = IBAN_COUNTRY_SPEC[country_code]
        # Le BBAN est tout ce qui suit le code pays et les chiffres de contrôle
        bban = iban[4:]
        if not re.match(bban_pattern, bban):
            raise ValidationError(
                "Le format de l'IBAN pour le pays %s est invalide." % country_code
            )


@deconstructible
class IBANValidator:
    """
    Validator pour IBAN (International Bank Account Number).
    
    Valide :
    1. La structure de base (code pays, chiffres de contrôle)
    2. La longueur spécifique au pays
    3. Le format BBAN spécifique au pays (optionnel, peut être désactivé)
    4. Les chiffres de contrôle (algorithme MOD-97)
    
    Utilisation :
        from elixir_toolkit.validators import IBANValidator
        
        class MonModele(models.Model):
            iban = models.CharField(
                max_length=34,
                validators=[IBANValidator()])
            
        # Ou avec des options :
        iban = models.CharField(
            max_length=34,
            validators=[IBANValidator(validate_format=True)])
            
        # Avec options ++ : 
        iban = models.CharField(
            max_length=34,
            validators=[IBANValidator(
                validate_length=True,
                validate_format=True,
                allowed_countries=['FR', 'BE']
            )]
        )

            
    """
    
    message = "Veuillez entrer un IBAN valide."
    message_length = "La longueur de l'IBAN pour le pays %(country)s doit être de %(expected)d caractères."
    message_check_digits = "Les chiffres de contrôle de l'IBAN sont invalides."
    message_structure = "La structure de l'IBAN est invalide."
    message_country = "Le code pays %(country)s n'est pas pris en charge."
    
    code = 'invalid_iban'
    
    def __init__(self, validate_length=True, validate_format=False, allowed_countries=None):
        """
        Initialise le validator IBAN.
        
        Args:
            validate_length: Si True, valide que la longueur de l'IBAN correspond à celle attendue pour le pays.
            validate_format: Si True, valide que la partie BBAN correspond au format regex du pays.
            allowed_countries: Liste optionnelle des codes pays autorisés (codes ISO à 2 lettres).
                              Si None, tous les pays dans IBAN_COUNTRY_SPEC sont autorisés.
        """
        self.validate_length = validate_length
        self.validate_format = validate_format
        self.allowed_countries = allowed_countries
    
    def __call__(self, value):
        """
        Valide la valeur IBAN.
        
        Args:
            value: La chaîne IBAN à valider.
            
        Raises:
            ValidationError: Si l'IBAN est invalide.
        """
        iban = _normalize_iban(value)
        
        if not iban:
            raise ValidationError(self.message, code=self.code)
        
        try:
            # Étape 1 : Valider la structure de base
            iban, country_code = validate_iban_structure(iban)
            
            # Étape 2 : Vérifier si le pays est autorisé
            if self.allowed_countries is not None:
                if country_code not in self.allowed_countries:
                    raise ValidationError(
                        self.message_country % {'country': country_code},
                        code=self.code
                    )
            
            # Étape 3 : Valider la longueur spécifique au pays
            if self.validate_length:
                if country_code not in IBAN_COUNTRY_SPEC:
                    # Pays inconnu, mais on peut toujours valider les chiffres de contrôle
                    pass
                else:
                    validate_iban_country_length(iban, country_code)
            
            # Étape 4 : Valider le format BBAN spécifique au pays
            if self.validate_format:
                if country_code in IBAN_COUNTRY_SPEC:
                    validate_iban_country_format(iban, country_code)
            
            # Étape 5 : Valider les chiffres de contrôle (algorithme MOD-97)
            validate_iban_check_digits(iban, country_code)
            
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(self.message, code=self.code) from e
    
    def __eq__(self, other):
        return (
            isinstance(other, IBANValidator) and
            self.validate_length == other.validate_length and
            self.validate_format == other.validate_format and
            self.allowed_countries == other.allowed_countries
        )
    
    def __repr__(self):
        return f"IBANValidator(validate_length={self.validate_length}, validate_format={self.validate_format}, allowed_countries={self.allowed_countries})"


@deconstructible
class FrenchIBANValidator(IBANValidator):
    """
    Validator spécifique pour les IBAN français.
    
    Les IBAN français ont toujours 23 caractères et commencent par 'FR'.
    Ce validator garantit que l'IBAN est pour la France et le valide en conséquence.
    """
    
    message = "Veuillez entrer un IBAN français valide."
    code = 'invalid_french_iban'
    
    def __init__(self):
        super().__init__(
            validate_length=True,
            validate_format=True,
            allowed_countries=['FR']
        )


def is_valid_iban(iban, allowed_countries=None):
    """
    Fonction utilitaire pour vérifier si un IBAN est valide.
    
    Args:
        iban: La chaîne IBAN à valider.
        allowed_countries: Liste optionnelle des codes pays autorisés.
        
    Returns:
        bool: True si l'IBAN est valide, False sinon.
    """
    try:
        validator = IBANValidator(
            validate_length=True,
            validate_format=False,
            allowed_countries=allowed_countries
        )
        validator(iban)
        return True
    except ValidationError:
        return False


def get_iban_country(iban):
    """
    Extrait et retourne le code pays d'un IBAN.
    
    Args:
        iban: La chaîne IBAN.
        
    Returns:
        str: Le code pays à 2 lettres, ou None si invalide.
    """
    iban = _normalize_iban(iban)
    if len(iban) >= 2 and iban[:2].isalpha():
        return iban[:2]
    return None


def get_iban_check_digits(iban):
    """
    Extrait et retourne les chiffres de contrôle d'un IBAN.
    
    Args:
        iban: La chaîne IBAN.
        
    Returns:
        str: Les 2 chiffres de contrôle, ou None si invalide.
    """
    iban = _normalize_iban(iban)
    if len(iban) >= 4 and iban[:2].isalpha() and iban[2:4].isdigit():
        return iban[2:4]
    return None
