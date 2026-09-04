# elixir_toolkit/validators.py
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class MaxFileSizeValidator:
    def __init__(self, max_size=5 * 1024 * 1024):
        self.max_size = max_size

    def __call__(self, files):
        if not isinstance(files, (list, tuple)):
            files = [files]
        for file in files:
            if file.size > self.max_size:
                raise ValidationError(
                    f"Le fichier '{file.name}' dépasse la taille maximale autorisée de {self.max_size // (1024 * 1024)} Mo."
                )


@deconstructible
class MaxTotalSizeValidator:
    def __init__(self, max_total_size=5 * 1024 * 1024):
        self.max_total_size = max_total_size

    def __call__(self, files):
        if not isinstance(files, (list, tuple)):
            files = [files]
        total_size = sum(file.size for file in files)
        if total_size > self.max_total_size:
            raise ValidationError(
                f"La taille totale des fichiers ({total_size // (1024 * 1024)} Mo) dépasse la limite autorisée de {self.max_total_size // (1024 * 1024)} Mo."
            )


@deconstructible
class AllowedExtensionsValidator:
    def __init__(self, allowed_extensions=None):
        self.allowed_extensions = [e.lower() for e in (allowed_extensions or ['pdf', 'png', 'jpg', 'jpeg'])]

    def __call__(self, files):
        if not isinstance(files, (list, tuple)):
            files = [files]
        for file in files:
            ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
            if ext not in self.allowed_extensions:
                raise ValidationError(
                    f"L'extension '.{ext}' n'est pas autorisée. Formats acceptés : {', '.join(self.allowed_extensions).upper()}"
                )


@deconstructible
class MaxFilesValidator:
    def __init__(self, max_files=100):
        self.max_files = max_files

    def __call__(self, files):
        if not isinstance(files, (list, tuple)):
            files = [files]
        if len(files) > self.max_files:
            raise ValidationError(f"Vous ne pouvez pas joindre plus de {self.max_files} fichiers.")
