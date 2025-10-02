"""
Module agent de base pour GPT Genius.
"""

from abc import ABC, abstractmethod
from gpt_genius.core.files_dict import FilesDict
from gpt_genius.core.prompt import Prompt


class BaseAgent(ABC):
    """
    Classe de base abstraite pour un agent qui interagit avec le code.
    
    Définit l'interface pour les agents capables d'initialiser et d'améliorer 
    le code basé sur un prompt donné. Les implémentations de cette classe 
    sont supposées fournir des méthodes concrètes pour ces actions.
    """

    @abstractmethod
    def init(self, prompt: Prompt) -> FilesDict:
        """
        Initialise un projet à partir d'un prompt.
        
        Args:
            prompt: Le prompt de l'utilisateur
            
        Returns:
            FilesDict contenant les fichiers générés
        """
        pass

    @abstractmethod
    def improve(self, files_dict: FilesDict, prompt: Prompt) -> FilesDict:
        """
        Améliore un projet existant basé sur un prompt.
        
        Args:
            files_dict: Les fichiers existants du projet
            prompt: Le prompt d'amélioration
            
        Returns:
            FilesDict contenant les fichiers mis à jour
        """
        pass