"""
Module de linting pour GPT Genius.

Ce module fournit des fonctionnalités de linting pour améliorer la qualité du code généré.
"""

import black
from gpt_genius.core.files_dict import FilesDict


class Linting:
    """
    Classe pour gérer le linting de différents types de fichiers.
    """
    
    def __init__(self):
        # Dictionnaire pour contenir les méthodes de linting pour différents types de fichiers
        self.linters = {".py": self.lint_python}

    def lint_python(self, content, config):
        """
        Lint des fichiers Python en utilisant la bibliothèque `black`, gérant toutes les exceptions 
        silencieusement et les loggant. Cette fonction tente de formater le code et retourne le code 
        formaté si réussi. Si une erreur survient pendant le formatage, elle log l'erreur et 
        retourne le contenu original.

        Args:
            content: Le contenu du fichier Python à formater
            config: Configuration pour black

        Returns:
            Le contenu linté ou le contenu original si erreur
        """
        try:
            # Essayer de formater le contenu en utilisant black
            linted_content = black.format_str(content, mode=black.FileMode(**config))
        except black.NothingChanged:
            # Si rien n'a changé, log l'info et retourne le contenu original
            print("\nInfo: Aucun changement n'a été fait pendant le formatage.\n")
            linted_content = content
        except Exception as error:
            # Si toute autre exception survient, log l'erreur et retourne le contenu original
            print(f"\nErreur: Ne peut pas formater à cause de {error}\n")
            linted_content = content
        return linted_content

    def lint_files(self, files_dict: FilesDict, config: dict = None) -> FilesDict:
        """
        Lint des fichiers basés sur leur extension en utilisant les fonctions de linting enregistrées.

        Args:
            files_dict: Le dictionnaire des noms de fichiers vers leur contenu de code source respectif
            config: Un dictionnaire optionnel d'options de configuration pour les outils de linting

        Returns:
            Le dictionnaire des noms de fichiers vers leur contenu de code source respectif après linting
        """
        if config is None:
            config = {}

        for filename, content in files_dict.items():
            extension = filename[
                filename.rfind(".") :
            ].lower()  # S'assurer de l'insensibilité à la casse
            if extension in self.linters:
                original_content = content
                linted_content = self.linters[extension](content, config)
                if linted_content != original_content:
                    print(f"Linté {filename}.")
                else:
                    print(f"Aucun changement fait pour {filename}.")
                files_dict[filename] = linted_content
            else:
                print(f"Aucun linter enregistré pour {filename}.")
        return files_dict