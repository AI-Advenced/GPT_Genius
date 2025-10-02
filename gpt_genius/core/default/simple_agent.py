"""
Module pour définir un agent simple qui utilise l'IA pour gérer la génération et l'amélioration de code.

Ce module fournit une classe qui représente un agent capable d'initialiser et d'améliorer 
une base de code en utilisant l'IA. Il gère les interactions avec le modèle IA, la mémoire, 
et l'environnement d'exécution pour générer et raffiner le code basé sur les prompts utilisateur.
"""

import tempfile
from typing import Optional

from gpt_genius.core.ai import AI
from gpt_genius.core.base_agent import BaseAgent
from gpt_genius.core.base_execution_env import BaseExecutionEnv
from gpt_genius.core.base_memory import BaseMemory
from gpt_genius.core.default.disk_execution_env import DiskExecutionEnv
from gpt_genius.core.default.disk_memory import DiskMemory
from gpt_genius.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_genius.core.default.steps import gen_code, gen_entrypoint, improve_fn
from gpt_genius.core.files_dict import FilesDict
from gpt_genius.core.preprompts_holder import PrepromptsHolder
from gpt_genius.core.prompt import Prompt


class SimpleAgent(BaseAgent):
    """
    Un agent qui utilise l'IA pour générer et améliorer le code basé sur un prompt donné.

    Cet agent est capable d'initialiser une base de code à partir d'un prompt et d'améliorer 
    une base de code existante basée sur l'entrée utilisateur. Il utilise un modèle IA pour 
    générer et raffiner le code, et il interagit avec un dépôt et un environnement d'exécution 
    pour gérer et exécuter le code.
    """

    def __init__(
        self,
        memory: BaseMemory,
        execution_env: BaseExecutionEnv,
        ai: AI = None,
        preprompts_holder: PrepromptsHolder = None,
    ):
        """
        Initialise le SimpleAgent.

        Args:
            memory: L'interface mémoire où le code et données associées sont stockés
            execution_env: L'environnement d'exécution où le code est exécuté
            ai: Le modèle IA utilisé pour générer et améliorer le code
            preprompts_holder: Le détenteur des messages preprompt qui guident le modèle IA
        """
        self.preprompts_holder = preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH)
        self.memory = memory
        self.execution_env = execution_env
        self.ai = ai or AI()

    @classmethod
    def with_default_config(
        cls, path: str, ai: AI = None, preprompts_holder: PrepromptsHolder = None
    ):
        """
        Crée une instance de SimpleAgent avec la configuration par défaut.

        Args:
            path: Le chemin de base pour l'agent
            ai: Instance AI optionnelle
            preprompts_holder: Détenteur de preprompts optionnel

        Returns:
            Une instance de SimpleAgent configurée
        """
        return cls(
            memory=DiskMemory(memory_path(path)),
            execution_env=DiskExecutionEnv(),
            ai=ai,
            preprompts_holder=preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH),
        )

    def init(self, prompt: Prompt) -> FilesDict:
        """
        Initialise un nouveau projet à partir d'un prompt.

        Args:
            prompt: Le prompt utilisateur pour la génération

        Returns:
            FilesDict contenant le code généré
        """
        files_dict = gen_code(self.ai, prompt, self.memory, self.preprompts_holder)
        entrypoint = gen_entrypoint(
            self.ai, prompt, files_dict, self.memory, self.preprompts_holder
        )
        combined_dict = {**files_dict, **entrypoint}
        files_dict = FilesDict(combined_dict)
        return files_dict

    def improve(
        self,
        files_dict: FilesDict,
        prompt: Prompt,
        execution_command: Optional[str] = None,
    ) -> FilesDict:
        """
        Améliore le code existant basé sur un prompt.

        Args:
            files_dict: Les fichiers de code existants
            prompt: Le prompt d'amélioration
            execution_command: Commande d'exécution optionnelle

        Returns:
            FilesDict contenant le code amélioré
        """
        files_dict = improve_fn(
            self.ai, prompt, files_dict, self.memory, self.preprompts_holder
        )
        return files_dict


def default_config_agent():
    """
    Crée une instance de SimpleAgent avec la configuration par défaut.

    Returns:
        Une instance de SimpleAgent avec un répertoire temporaire comme chemin de base
    """
    return SimpleAgent.with_default_config(tempfile.mkdtemp())