"""
Module d'environnement d'exécution de base pour GPT Genius.
"""

from abc import ABC, abstractmethod
from subprocess import Popen
from typing import Optional, Tuple
from gpt_genius.core.files_dict import FilesDict


class BaseExecutionEnv(ABC):
    """
    Classe de base abstraite pour un environnement d'exécution capable d'exécuter du code.

    Cette classe définit l'interface pour les environnements d'exécution qui peuvent exécuter 
    des commandes, gérer des processus, et gérer l'upload/download de fichiers.
    """

    @abstractmethod
    def run(self, command: str, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        """
        Exécute une commande dans l'environnement d'exécution.
        
        Args:
            command: La commande à exécuter
            timeout: Timeout optionnel en secondes
            
        Returns:
            Tuple (stdout, stderr, return_code)
        """
        raise NotImplementedError

    @abstractmethod
    def popen(self, command: str) -> Popen:
        """
        Exécute une commande dans l'environnement d'exécution et retourne un Popen.
        
        Args:
            command: La commande à exécuter
            
        Returns:
            Objet Popen pour gérer le processus
        """
        raise NotImplementedError

    @abstractmethod
    def upload(self, files: FilesDict) -> "BaseExecutionEnv":
        """
        Upload des fichiers vers l'environnement d'exécution.
        
        Args:
            files: Les fichiers à uploader
            
        Returns:
            L'instance de l'environnement d'exécution
        """
        raise NotImplementedError

    @abstractmethod
    def download(self) -> FilesDict:
        """
        Télécharge les fichiers depuis l'environnement d'exécution.
        
        Returns:
            FilesDict contenant les fichiers téléchargés
        """
        raise NotImplementedError