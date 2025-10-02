"""
Module définissant les chemins de système de fichiers utilisés par l'application.

Ce module contient des définitions de chemins de système de fichiers qui sont utilisés 
à travers l'application pour localiser et gérer divers fichiers et répertoires, 
tels que les logs, la mémoire, et les preprompts.
"""

import os
from pathlib import Path

META_DATA_REL_PATH = ".gptgenius"
MEMORY_REL_PATH = os.path.join(META_DATA_REL_PATH, "memory")
CODE_GEN_LOG_FILE = "all_output.txt"
IMPROVE_LOG_FILE = "improve.txt"
DIFF_LOG_FILE = "diff_errors.txt"
DEBUG_LOG_FILE = "debug_log_file.txt"
ENTRYPOINT_FILE = "run.sh"
ENTRYPOINT_LOG_FILE = "gen_entrypoint_chat.txt"
PREPROMPTS_PATH = Path(__file__).parent.parent.parent / "preprompts"


def memory_path(path):
    """
    Construit le chemin complet vers le répertoire de mémoire basé sur un chemin de base donné.

    Args:
        path: Le chemin de base auquel ajouter le répertoire de mémoire

    Returns:
        Le chemin complet vers le répertoire de mémoire
    """
    return os.path.join(path, MEMORY_REL_PATH)


def metadata_path(path):
    """
    Construit le chemin complet vers le répertoire de métadonnées basé sur un chemin de base donné.

    Args:
        path: Le chemin de base auquel ajouter le répertoire de métadonnées

    Returns:
        Le chemin complet vers le répertoire de métadonnées
    """
    return os.path.join(path, META_DATA_REL_PATH)