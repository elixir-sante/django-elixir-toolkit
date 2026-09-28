# elixir_toolkit/validators/file_validators.py
import os

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


def _as_list(files):
    """Accepte un fichier seul, une liste/tuple de fichiers ou une valeur vide."""
    if not files:
        return []
    if isinstance(files, (list, tuple)):
        return [f for f in files if f]
    return [files]


def _format_size(size):
    """Formate une taille en octets de façon lisible (ex : 512 Ko, 5,5 Mo)."""
    if size >= 1024 * 1024:
        value, unit = size / (1024 * 1024), "Mo"
    elif size >= 1024:
        value, unit = size / 1024, "Ko"
    else:
        return f"{size} octets"
    return f"{value:.1f}".rstrip("0").rstrip(".").replace(".", ",") + f" {unit}"


def _file_name(file):
    return os.path.basename(getattr(file, "name", "") or "")


class _ComparableValidator:
    """
    Django compare les validators lors de makemigrations : sans __eq__,
    une nouvelle migration est générée à chaque exécution.
    """
    _compare_attrs = ()

    def __eq__(self, other):
        return type(self) is type(other) and all(
            getattr(self, a) == getattr(other, a) for a in self._compare_attrs
        )

    def __hash__(self):
        return hash((type(self),) + tuple(
            tuple(v) if isinstance(v, list) else v
            for v in (getattr(self, a) for a in self._compare_attrs)
        ))


@deconstructible
class MaxFileSizeValidator(_ComparableValidator):
    _compare_attrs = ("max_size",)

    def __init__(self, max_size=5 * 1024 * 1024):
        self.max_size = max_size

    def __call__(self, files):
        for file in _as_list(files):
            if file.size > self.max_size:
                raise ValidationError(
                    "Le fichier '%(name)s' (%(size)s) dépasse la taille maximale autorisée de %(max)s.",
                    code="file_too_large",
                    params={
                        "name": _file_name(file),
                        "size": _format_size(file.size),
                        "max": _format_size(self.max_size),
                    },
                )


@deconstructible
class MaxTotalSizeValidator(_ComparableValidator):
    _compare_attrs = ("max_total_size",)

    def __init__(self, max_total_size=5 * 1024 * 1024):
        self.max_total_size = max_total_size

    def __call__(self, files):
        total_size = sum(file.size for file in _as_list(files))
        if total_size > self.max_total_size:
            raise ValidationError(
                "La taille totale des fichiers (%(total)s) dépasse la limite autorisée de %(max)s.",
                code="total_size_exceeded",
                params={
                    "total": _format_size(total_size),
                    "max": _format_size(self.max_total_size),
                },
            )


@deconstructible
class AllowedExtensionsValidator(_ComparableValidator):
    _compare_attrs = ("allowed_extensions",)

    def __init__(self, allowed_extensions=None):
        # Accepte 'pdf' comme '.PDF'
        self.allowed_extensions = [
            e.lower().lstrip(".")
            for e in (allowed_extensions or ["pdf", "png", "jpg", "jpeg"])
        ]

    def __call__(self, files):
        allowed = ", ".join(self.allowed_extensions).upper()
        for file in _as_list(files):
            name = _file_name(file)
            ext = os.path.splitext(name)[1].lstrip(".").lower()
            if not ext:
                raise ValidationError(
                    "Le fichier '%(name)s' n'a pas d'extension. Formats acceptés : %(allowed)s",
                    code="missing_extension",
                    params={"name": name, "allowed": allowed},
                )
            if ext not in self.allowed_extensions:
                raise ValidationError(
                    "L'extension '.%(ext)s' n'est pas autorisée. Formats acceptés : %(allowed)s",
                    code="invalid_extension",
                    params={"ext": ext, "allowed": allowed},
                )


@deconstructible
class MaxFilesValidator(_ComparableValidator):
    _compare_attrs = ("max_files",)

    def __init__(self, max_files=100):
        self.max_files = max_files

    def __call__(self, files):
        if len(_as_list(files)) > self.max_files:
            raise ValidationError(
                "Vous ne pouvez pas joindre plus de %(max)d fichiers.",
                code="too_many_files",
                params={"max": self.max_files},
            )
