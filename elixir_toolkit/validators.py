# elixir_toolkit/validators.py
from django.core.exceptions import ValidationError

class FileConstraintsValidator:
    def __init__(self, max_size=5*1024*1024, max_total_size=5*1024*1024, allowed_extensions=None, max_files=100):
        self.max_size = max_size  # En octets (ex: 5 Mo)
        self.max_total_size = max_total_size
        self.allowed_extensions = [e.lower() for e in (allowed_extensions or ['pdf', 'png', 'jpg', 'jpeg'])]
        self.max_files = max_files

    def __call__(self, files):
        # Supporte un fichier unique ou une liste de fichiers
        if not isinstance(files, (list, tuple)):
            files = [files]

        if len(files) > self.max_files:
            raise ValidationError(f"Vous ne pouvez pas joindre plus de {self.max_files} fichiers.")

        total_size = 0
        for file in files:
            # Vérif taille unitaire
            if file.size > self.max_size:
                raise ValidationError(f"Le fichier '{file.name}' dépasse la taille maximale autorisée de {self.max_size // (1024*1024)} Mo.")
            
            # Vérif extension
            ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
            if ext not in self.allowed_extensions:
                raise ValidationError(f"L'extension '.{ext}' n'est pas autorisée. Formats acceptés : {', '.join(self.allowed_extensions).upper()}")
            
            total_size += file.size

        # Vérif taille totale cumulée
        if total_size > self.max_total_size:
            raise ValidationError(f"La taille totale des fichiers ({total_size // (1024*1024)} Mo) dépasse la limite autorisée de {self.max_total_size // (1024*1024)} Mo.")