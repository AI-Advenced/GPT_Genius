"""
Module pour analyser les transcripts de chat contenant des chemins de fichiers et des blocs de code.

Ce script fournit des fonctionnalités pour analyser les transcripts de chat qui contiennent 
des chemins de fichiers et des blocs de code, appliquer des diffs à ces fichiers, et analyser 
les chaînes de format diff git unifié.
"""

import logging
import re
from typing import Dict

from gpt_genius.core.files_dict import FilesDict

# Initialiser un logger pour ce module
logger = logging.getLogger(__name__)


def chat_to_files_dict(chat: str) -> FilesDict:
    """
    Convertit une chaîne de chat contenant des chemins de fichiers et des blocs de code 
    en un objet FilesDict.

    Args:
        chat: La chaîne de chat contenant des chemins de fichiers et des blocs de code

    Returns:
        Un dictionnaire avec les chemins de fichiers comme clés et les blocs de code comme valeurs
    """
    # Regex pour matcher les chemins de fichiers et blocs de code associés
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files_dict = FilesDict()
    for match in matches:
        # Nettoyer et standardiser le chemin de fichier
        path = re.sub(r'[\:<>"|?*]', "", match.group(1))
        path = re.sub(r"^\[(.*)\]$", r"\1", path)
        path = re.sub(r"^`(.*)`$", r"\1", path)
        path = re.sub(r"[\]\:]$", "", path)

        # Extraire et nettoyer le contenu du code
        content = match.group(2)

        # Ajouter le chemin nettoyé et le contenu au FilesDict
        files_dict[path.strip()] = content.strip()

    return files_dict


def apply_diffs(diffs: Dict[str, any], files: FilesDict) -> FilesDict:
    """
    Applique des diffs aux fichiers fournis.

    Args:
        diffs: Un dictionnaire de diffs à appliquer, indexé par nom de fichier
        files: Les fichiers originaux auxquels les diffs seront appliqués

    Returns:
        Les fichiers mis à jour après application des diffs
    """
    # Pour cette version simplifiée, on retourne juste les fichiers originaux
    # Dans une version complète, on implémenterait l'application réelle des diffs
    logger.info("Application des diffs (fonctionnalité simplifiée)")
    return FilesDict(files.copy())


def parse_diffs(diff_string: str, diff_timeout=3) -> dict:
    """
    Analyse une chaîne diff au format git diff unifié.

    Args:
        diff_string: La chaîne diff à analyser
        diff_timeout: Timeout pour l'analyse

    Returns:
        Un dictionnaire d'objets Diff indexés par nom de fichier
    """
    # Pour cette version simplifiée, on retourne un dictionnaire vide
    # Dans une version complète, on analyserait réellement les diffs
    logger.info("Analyse des diffs (fonctionnalité simplifiée)")
    return {}