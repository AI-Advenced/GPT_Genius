"""
Module FilesDict pour la gestion des fichiers de code dans GPT Genius.
"""

from collections import OrderedDict
from pathlib import Path
from typing import Union


class FilesDict(dict):
    """
    Un conteneur basé sur un dictionnaire pour gérer les fichiers de code.

    Cette classe étend le dictionnaire standard pour forcer les clés et valeurs 
    en chaînes de caractères, représentant les noms de fichiers et leur contenu 
    de code correspondant. Elle fournit des méthodes pour formater son contenu 
    pour une interaction basée sur le chat avec un agent IA et pour appliquer 
    des vérifications de type sur les clés et valeurs.
    """

    def __setitem__(self, key: Union[str, Path], value: str):
        """
        Définit le contenu du code pour le nom de fichier donné, en appliquant 
        des vérifications de type sur la clé et la valeur.

        Args:
            key: Le nom du fichier comme clé pour le contenu du code
            value: Le contenu du code à associer avec le nom de fichier

        Raises:
            TypeError: Si la clé n'est pas une chaîne ou un Path, ou si la valeur n'est pas une chaîne
        """
        if not isinstance(key, (str, Path)):
            raise TypeError("Les clés doivent être des chaînes ou des Path's")
        if not isinstance(value, str):
            raise TypeError("Les valeurs doivent être des chaînes")
        super().__setitem__(str(key), value)

    def to_chat(self):
        """
        Formate les éléments de l'objet (supposant des paires nom de fichier et contenu)
        en une chaîne adaptée à l'affichage de chat.

        Returns:
            Une représentation en chaîne des fichiers
        """
        chat_str = ""
        for file_name, file_content in self.items():
            lines_dict = file_to_lines_dict(file_content)
            chat_str += f"File: {file_name}\n"
            for line_number, line_content in lines_dict.items():
                chat_str += f"{line_number} {line_content}\n"
            chat_str += "\n"
        return f"```\n{chat_str}```"

    def to_log(self):
        """
        Formate les éléments de l'objet (supposant des paires nom de fichier et contenu)
        en une chaîne adaptée à l'affichage de log.

        Returns:
            Une représentation en chaîne des fichiers
        """
        log_str = ""
        for file_name, file_content in self.items():
            log_str += f"File: {file_name}\n"
            log_str += file_content
            log_str += "\n"
        return log_str


def file_to_lines_dict(file_content: str) -> dict:
    """
    Convertit le contenu d'un fichier en un dictionnaire où chaque numéro de ligne 
    est une clé et le contenu de ligne correspondant est la valeur.

    Args:
        file_content: Le contenu du fichier

    Returns:
        Un dictionnaire avec les numéros de ligne comme clés et les contenus de ligne comme valeurs
    """
    lines_dict = OrderedDict(
        {
            line_number: line_content
            for line_number, line_content in enumerate(file_content.split("\n"), 1)
        }
    )
    return lines_dict