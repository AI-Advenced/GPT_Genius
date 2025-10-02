"""
GPT Genius - Framework d'IA pour la génération et l'amélioration de code automatisées.
"""

__version__ = "0.1.0"
__author__ = "GPT Genius Team"
__email__ = "contact@gpt-genius.com"

# Imports principaux pour une utilisation simple du package
try:
    from gpt_genius.core.ai import AI
    from gpt_genius.core.files_dict import FilesDict  
    from gpt_genius.core.prompt import Prompt
    from gpt_genius.core.base_agent import BaseAgent
    from gpt_genius.core.default.simple_agent import SimpleAgent
except ImportError:
    # Les imports peuvent échouer lors de l'installation
    pass

__all__ = [
    "AI",
    "FilesDict",
    "Prompt", 
    "BaseAgent",
    "SimpleAgent",
    "__version__",
    "__author__",
    "__email__",
]