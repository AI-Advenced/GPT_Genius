"""
Module pour gérer le stockage de fichiers dans un répertoire temporaire.

Ce module fournit une classe qui gère le stockage de fichiers dans un répertoire temporaire.
Il inclut des méthodes pour uploader des fichiers vers le répertoire et les télécharger 
comme une collection de fichiers.
"""

import tempfile
from pathlib import Path
from typing import Union

from gpt_genius.core.files_dict import FilesDict
from gpt_genius.core.linting import Linting


class FileStore:
    """
    Gère le stockage de fichiers dans un répertoire temporaire, permettant l'upload et le download de fichiers.
    """

    def __init__(self, path: Union[str, Path, None] = None):
        """
        Initialise le FileStore.

        Args:
            path: Chemin optionnel pour le répertoire de travail. 
                  Si None, crée un répertoire temporaire.
        """
        if path is None:
            path = Path(tempfile.mkdtemp(prefix="gpt-genius-"))

        self.working_dir = Path(path)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.id = self.working_dir.name.split("-")[-1]

    def push(self, files: FilesDict):
        """
        Pousse (upload) des fichiers vers le répertoire de travail.

        Args:
            files: Les fichiers à écrire

        Returns:
            L'instance FileStore
        """
        for name, content in files.items():
            path = self.working_dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        return self

    def linting(self, files: FilesDict) -> FilesDict:
        """
        Applique le linting aux fichiers de code.

        Args:
            files: Les fichiers à linter

        Returns:
            Les fichiers après linting
        """
        linting = Linting()
        return linting.lint_files(files)

    def pull(self) -> FilesDict:
        """
        Tire (download) des fichiers depuis le répertoire de travail.

        Returns:
            FilesDict contenant tous les fichiers du répertoire de travail
        """
        files = {}
        for path in self.working_dir.glob("**/*"):
            if path.is_file():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    content = "fichier binaire"
                files[str(path.relative_to(self.working_dir))] = content
        return FilesDict(files)