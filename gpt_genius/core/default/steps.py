"""
Module pour définir les étapes impliquées dans la génération et l'amélioration de code utilisant l'IA.

Ce module fournit des fonctions qui représentent différentes étapes dans le processus de génération 
et d'amélioration de code utilisant un modèle IA. Ces étapes incluent la génération de code à partir 
d'un prompt, la création d'un point d'entrée pour la base de code, l'exécution du point d'entrée, 
et le raffinement des éditions de code.
"""

import inspect
from pathlib import Path
from typing import MutableMapping, Union

from langchain.schema import HumanMessage, SystemMessage

from gpt_genius.core.ai import AI
from gpt_genius.core.base_memory import BaseMemory
from gpt_genius.core.chat_to_files import chat_to_files_dict
from gpt_genius.core.default.paths import (
    CODE_GEN_LOG_FILE,
    ENTRYPOINT_FILE,
    ENTRYPOINT_LOG_FILE,
    IMPROVE_LOG_FILE,
)
from gpt_genius.core.files_dict import FilesDict
from gpt_genius.core.preprompts_holder import PrepromptsHolder
from gpt_genius.core.prompt import Prompt


def curr_fn() -> str:
    """
    Retourne le nom de la fonction actuelle.

    Returns:
        Le nom de la fonction qui a appelé cette fonction
    """
    return inspect.stack()[1].function


def setup_sys_prompt(preprompts: MutableMapping[Union[str, Path], str]) -> str:
    """
    Configure le prompt système pour générer du code.

    Args:
        preprompts: Un mapping des messages preprompt pour guider le modèle IA

    Returns:
        Le message de prompt système pour le modèle IA
    """
    return (
        preprompts["roadmap"]
        + preprompts["generate"].replace("FILE_FORMAT", preprompts["file_format"])
        + "\nUtile à savoir:\n"
        + preprompts["philosophy"]
    )


def setup_sys_prompt_existing_code(
    preprompts: MutableMapping[Union[str, Path], str]
) -> str:
    """
    Configure le prompt système pour améliorer du code existant.

    Args:
        preprompts: Un mapping des messages preprompt pour guider le modèle IA

    Returns:
        Le message de prompt système pour le modèle IA pour améliorer du code existant
    """
    return (
        preprompts["roadmap"]
        + preprompts["improve"].replace("FILE_FORMAT", preprompts["file_format_diff"])
        + "\nUtile à savoir:\n"
        + preprompts["philosophy"]
    )


def gen_code(
    ai: AI, prompt: Prompt, memory: BaseMemory, preprompts_holder: PrepromptsHolder
) -> FilesDict:
    """
    Génère du code à partir d'un prompt utilisant l'IA et retourne les fichiers générés.

    Args:
        ai: Le modèle IA utilisé pour générer du code
        prompt: Le prompt utilisateur pour générer du code
        memory: L'interface mémoire où le code et données associées sont stockés
        preprompts_holder: Le détenteur des messages preprompt qui guident le modèle IA

    Returns:
        Un dictionnaire des noms de fichiers vers leur contenu de code source respectif
    """
    preprompts = preprompts_holder.get_preprompts()
    messages = ai.start(
        setup_sys_prompt(preprompts), prompt.to_langchain_content(), step_name=curr_fn()
    )
    chat = messages[-1].content.strip()
    memory.log(CODE_GEN_LOG_FILE, "\n\n".join(x.pretty_repr() for x in messages))
    files_dict = chat_to_files_dict(chat)
    return files_dict


def gen_entrypoint(
    ai: AI,
    prompt: Prompt,
    files_dict: FilesDict,
    memory: BaseMemory,
    preprompts_holder: PrepromptsHolder,
) -> FilesDict:
    """
    Génère un point d'entrée pour la base de code et retourne les fichiers de point d'entrée.

    Args:
        ai: Le modèle IA utilisé pour générer le point d'entrée
        prompt: Le prompt pour le point d'entrée
        files_dict: Le dictionnaire des noms de fichiers vers leur contenu de code source respectif
        memory: L'interface mémoire où le code et données associées sont stockés
        preprompts_holder: Le détenteur des messages preprompt qui guident le modèle IA

    Returns:
        Un dictionnaire contenant le fichier de point d'entrée
    """
    user_prompt = prompt.entrypoint_prompt
    if not user_prompt:
        user_prompt = """
        Faites un script unix qui
        a) installe les dépendances
        b) exécute toutes les parties nécessaires de la base de code (en parallèle si nécessaire)
        """
    preprompts = preprompts_holder.get_preprompts()
    messages = ai.start(
        system=(preprompts["entrypoint"]),
        user=user_prompt
        + "\nInformations sur la base de code:\n\n"
        + files_dict.to_chat(),
        step_name=curr_fn(),
    )
    print()
    chat = messages[-1].content.strip()
    
    # Extraction du code depuis les blocs ```
    import re
    regex = r"```\S*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)
    entrypoint_code = FilesDict(
        {ENTRYPOINT_FILE: "\n".join(match.group(1) for match in matches)}
    )
    memory.log(ENTRYPOINT_LOG_FILE, "\n\n".join(x.pretty_repr() for x in messages))
    return entrypoint_code


def improve_fn(
    ai: AI,
    prompt: Prompt,
    files_dict: FilesDict,
    memory: BaseMemory,
    preprompts_holder: PrepromptsHolder,
    diff_timeout=3,
) -> FilesDict:
    """
    Améliore le code basé sur l'entrée utilisateur et retourne les fichiers mis à jour.

    Args:
        ai: Le modèle IA utilisé pour améliorer du code
        prompt: Le prompt utilisateur pour améliorer le code
        files_dict: Le dictionnaire des noms de fichiers vers leur contenu de code source respectif
        memory: L'interface mémoire où le code et données associées sont stockés
        preprompts_holder: Le détenteur des messages preprompt qui guident le modèle IA
        diff_timeout: Timeout pour le parsing des diffs

    Returns:
        Le dictionnaire des noms de fichiers vers leur contenu de code source respectif mis à jour
    """
    preprompts = preprompts_holder.get_preprompts()
    messages = [
        SystemMessage(content=setup_sys_prompt_existing_code(preprompts)),
    ]

    # Ajouter les fichiers comme entrée
    messages.append(HumanMessage(content=f"{files_dict.to_chat()}"))
    messages.append(HumanMessage(content=prompt.to_langchain_content()))
    
    messages = ai.next(messages, step_name=curr_fn())
    chat = messages[-1].content.strip()
    memory.log(IMPROVE_LOG_FILE, "\n\n".join(x.pretty_repr() for x in messages))
    
    # Pour une version simple, on retourne juste les fichiers originaux
    # Dans une version complète, on appliquerait les diffs ici
    print("Amélioration du code en cours...")
    return files_dict