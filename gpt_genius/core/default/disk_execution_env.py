"""
Module pour gérer l'environnement d'exécution sur le disque local.

Ce module fournit une classe qui gère l'exécution du code stocké sur le système 
de fichiers local. Il inclut des méthodes pour uploader des fichiers vers 
l'environnement d'exécution, exécuter des commandes, et capturer la sortie.
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple, Union

from gpt_genius.core.base_execution_env import BaseExecutionEnv
from gpt_genius.core.default.file_store import FileStore
from gpt_genius.core.files_dict import FilesDict


class DiskExecutionEnv(BaseExecutionEnv):
    """
    Un environnement d'exécution qui exécute le code sur le système de fichiers local 
    et capture la sortie de l'exécution.

    Cette classe est responsable d'exécuter le code qui est stocké sur le disque. 
    Elle s'assure que le fichier de point d'entrée nécessaire existe et exécute 
    ensuite le code en utilisant un sous-processus. Si l'exécution est interrompue 
    par l'utilisateur, elle gère l'interruption gracieusement.
    """

    def __init__(self, path: Union[str, Path, None] = None):
        self.files = FileStore(path)

    def upload(self, files: FilesDict) -> "DiskExecutionEnv":
        """
        Upload des fichiers vers l'environnement d'exécution.

        Args:
            files: Les fichiers à uploader

        Returns:
            L'instance de l'environnement d'exécution
        """
        self.files.push(files)
        return self

    def download(self) -> FilesDict:
        """
        Télécharge les fichiers depuis l'environnement d'exécution.

        Returns:
            FilesDict contenant les fichiers téléchargés
        """
        return self.files.pull()

    def popen(self, command: str) -> subprocess.Popen:
        """
        Exécute une commande dans l'environnement d'exécution et retourne un Popen.

        Args:
            command: La commande à exécuter

        Returns:
            Objet Popen pour gérer le processus
        """
        p = subprocess.Popen(
            command,
            shell=True,
            cwd=self.files.working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return p

    def run(self, command: str, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        """
        Exécute une commande dans l'environnement d'exécution.

        Args:
            command: La commande à exécuter
            timeout: Timeout optionnel en secondes

        Returns:
            Tuple (stdout, stderr, return_code)
        """
        start = time.time()
        print("\n--- Début de l'exécution ---")
        # pendant l'exécution, imprime aussi stdout et stderr
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.files.working_dir,
            text=True,
            shell=True,
        )
        print("$", command)
        stdout_full, stderr_full = "", ""

        try:
            while p.poll() is None:
                assert p.stdout is not None
                assert p.stderr is not None
                stdout = p.stdout.readline()
                stderr = p.stderr.readline()
                if stdout:
                    print(stdout, end="")
                    stdout_full += stdout
                if stderr:
                    print(stderr, end="")
                    stderr_full += stderr
                if timeout and time.time() - start > timeout:
                    print("Timeout!")
                    p.kill()
                    raise TimeoutError()
        except KeyboardInterrupt:
            print()
            print("Arrêt de l'exécution.")
            print("Exécution arrêtée.")
            p.kill()
            print()
            print("--- Fin d'exécution ---\n")

        return stdout_full, stderr_full, p.returncode