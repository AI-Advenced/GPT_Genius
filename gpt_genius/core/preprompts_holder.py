"""
Module pour gérer les preprompts stockés sur disque.
"""

from pathlib import Path
from typing import Dict

from gpt_genius.core.default.disk_memory import DiskMemory


class PrepromptsHolder:
    """
    Un détenteur pour les textes de preprompt qui sont stockés sur disque.

    Cette classe fournit des méthodes pour récupérer les textes de preprompt 
    à partir d'un répertoire spécifié.
    """

    def __init__(self, preprompts_path: Path):
        """
        Initialise le PrepromptsHolder.

        Args:
            preprompts_path: Le chemin vers le répertoire contenant les textes de preprompt
        """
        self.preprompts_path = preprompts_path

    def get_preprompts(self) -> Dict[str, str]:
        """
        Récupère tous les textes de preprompt du répertoire et les retourne comme dictionnaire.

        Returns:
            Dictionnaire avec les noms de fichiers comme clés et le contenu comme valeurs
        """
        preprompts_repo = DiskMemory(self.preprompts_path)
        return {file_name: preprompts_repo[file_name] for file_name in preprompts_repo}