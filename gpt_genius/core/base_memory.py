"""
Module de base pour la gestion de la mémoire dans GPT Genius.
"""

from pathlib import Path
from typing import MutableMapping, Union

# Type alias pour la mémoire de base : mapping entre noms de fichiers et contenus
BaseMemory = MutableMapping[Union[str, Path], str]