"""
Module Disk Memory pour GPT Genius.

Ce module fournit un système de base de données clé-valeur basé sur les fichiers, 
où les clés sont représentées comme noms de fichiers et les valeurs comme contenu 
de ces fichiers.
"""

import base64
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Union

from gpt_genius.core.base_memory import BaseMemory
from gpt_genius.tools.supported_languages import SUPPORTED_LANGUAGES


class DiskMemory(BaseMemory):
    """
    Un stockage clé-valeur basé sur les fichiers où les clés correspondent aux noms de fichiers 
    et les valeurs au contenu des fichiers.

    Cette classe fournit une interface à une base de données basée sur les fichiers, 
    en exploitant les opérations de fichiers pour faciliter les interactions de type CRUD. 
    Elle permet des vérifications rapides sur l'existence des clés, la récupération de 
    valeurs basées sur les clés, et la définition de nouvelles paires clé-valeur.
    """

    def __init__(self, path: Union[str, Path]):
        """
        Initialise la classe DiskMemory avec un chemin spécifié.

        Args:
            path: Le chemin vers le répertoire où les fichiers de la base de données seront stockés
        """
        self.path: Path = Path(path).absolute()
        self.path.mkdir(parents=True, exist_ok=True)

    def __contains__(self, key: str) -> bool:
        """
        Détermine si la base de données contient un fichier avec la clé spécifiée.

        Args:
            key: La clé (nom de fichier) à vérifier pour l'existence dans la base de données

        Returns:
            True si le fichier existe, False sinon
        """
        return (self.path / key).is_file()

    def __getitem__(self, key: str) -> str:
        """
        Récupère le contenu d'un fichier dans la base de données correspondant à la clé donnée.
        Si le fichier est une image avec une extension .png ou .jpeg, il retourne le contenu 
        au format chaîne encodée en Base64.

        Args:
            key: La clé (nom de fichier) dont le contenu doit être récupéré

        Returns:
            Le contenu du fichier associé à la clé, ou chaîne encodée en Base64 si c'est un fichier .png ou .jpeg

        Raises:
            KeyError: Si le fichier correspondant à la clé n'existe pas dans la base de données
        """
        full_path = self.path / key

        if not full_path.is_file():
            raise KeyError(f"Le fichier '{key}' n'a pu être trouvé dans '{self.path}'")

        if full_path.suffix in [".png", ".jpeg", ".jpg"]:
            with full_path.open("rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                mime_type = "image/png" if full_path.suffix == ".png" else "image/jpeg"
                return f"data:{mime_type};base64,{encoded_string}"
        else:
            with full_path.open("r", encoding="utf-8") as f:
                return f.read()

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Récupère le contenu d'un fichier dans la base de données, ou retourne une valeur par défaut si non trouvé.

        Args:
            key: La clé (nom de fichier) dont le contenu doit être récupéré
            default: La valeur par défaut à retourner si le fichier n'existe pas

        Returns:
            Le contenu du fichier s'il existe, une nouvelle instance DiskMemory si la clé correspond à un répertoire
        """
        item_path = self.path / key
        try:
            if item_path.is_file():
                return self[key]
            elif item_path.is_dir():
                return DiskMemory(item_path)
            else:
                return default
        except:
            return default

    def __setitem__(self, key: Union[str, Path], val: str) -> None:
        """
        Définit ou met à jour le contenu d'un fichier dans la base de données correspondant à la clé donnée.

        Args:
            key: La clé (nom de fichier) où le contenu doit être défini
            val: Le contenu à écrire dans le fichier

        Raises:
            ValueError: Si la clé tente d'accéder à un chemin parent
            TypeError: Si la valeur n'est pas une chaîne
        """
        if str(key).startswith("../"):
            raise ValueError(f"Le nom de fichier {key} a tenté d'accéder au chemin parent.")

        if not isinstance(val, str):
            raise TypeError("val doit être str")

        full_path = self.path / key
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(val, encoding="utf-8")

    def __delitem__(self, key: Union[str, Path]) -> None:
        """
        Supprime un fichier ou répertoire de la base de données correspondant à la clé donnée.

        Args:
            key: La clé (nom de fichier ou nom de répertoire) à supprimer

        Raises:
            KeyError: Si le fichier ou répertoire correspondant à la clé n'existe pas dans la base de données
        """
        item_path = self.path / key
        if not item_path.exists():
            raise KeyError(f"L'élément '{key}' n'a pu être trouvé dans '{self.path}'")

        if item_path.is_file():
            item_path.unlink()
        elif item_path.is_dir():
            shutil.rmtree(item_path)

    def __iter__(self) -> Iterator[str]:
        """
        Itère sur les clés (noms de fichiers) dans la base de données.

        Returns:
            Un itérateur sur la liste triée des clés (noms de fichiers) dans la base de données
        """
        return iter(
            sorted(
                str(item.relative_to(self.path))
                for item in sorted(self.path.rglob("*"))
                if item.is_file()
            )
        )

    def __len__(self) -> int:
        """
        Obtient le nombre de fichiers dans la base de données.

        Returns:
            Le nombre de fichiers dans la base de données
        """
        return len(list(self.__iter__()))

    def _supported_files(self) -> str:
        """Retourne les fichiers avec des extensions supportées."""
        valid_extensions = {
            ext for lang in SUPPORTED_LANGUAGES for ext in lang["extensions"]
        }
        file_paths = [
            str(item)
            for item in self
            if Path(item).is_file() and Path(item).suffix in valid_extensions
        ]
        return "\n".join(file_paths)

    def _all_files(self) -> str:
        """Retourne tous les fichiers."""
        file_paths = [str(item) for item in self if Path(item).is_file()]
        return "\n".join(file_paths)

    def to_path_list_string(self, supported_code_files_only: bool = False) -> str:
        """
        Génère une représentation en chaîne des chemins de fichiers dans la base de données.

        Args:
            supported_code_files_only: Si True, filtre la liste pour inclure seulement 
            les extensions de fichiers de code supportées

        Returns:
            Une chaîne séparée par des nouvelles lignes des chemins de fichiers
        """
        if supported_code_files_only:
            return self._supported_files()
        else:
            return self._all_files()

    def to_dict(self) -> Dict[Union[str, Path], str]:
        """
        Convertit le contenu de la base de données en dictionnaire.

        Returns:
            Un dictionnaire avec les clés comme noms de fichiers et les valeurs comme contenu de fichiers
        """
        return {file_path: self[file_path] for file_path in self}

    def to_json(self) -> str:
        """
        Sérialise le contenu de la base de données en chaîne JSON.

        Returns:
            Une représentation en chaîne JSON du contenu de la base de données
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def log(self, key: Union[str, Path], val: str) -> None:
        """
        Ajoute à un fichier ou le crée et écrit dedans s'il n'existe pas.

        Args:
            key: La clé (nom de fichier) où le contenu doit être ajouté
            val: Le contenu à ajouter au fichier
        """
        if str(key).startswith("../"):
            raise ValueError(f"Le nom de fichier {key} a tenté d'accéder au chemin parent.")

        if not isinstance(val, str):
            raise TypeError("val doit être str")

        full_path = self.path / "logs" / key
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Toucher s'il n'existe pas
        if not full_path.exists():
            full_path.touch()

        with open(full_path, "a", encoding="utf-8") as file:
            file.write(f"\n{datetime.now().isoformat()}\n")
            file.write(val + "\n")

    def archive_logs(self):
        """
        Déplace tous les logs vers le répertoire d'archive basé sur l'horodatage actuel.
        """
        if "logs" in self:
            archive_dir = (
                self.path / f"logs_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            )
            shutil.move(self.path / "logs", archive_dir)