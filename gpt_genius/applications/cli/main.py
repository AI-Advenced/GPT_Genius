"""
Point d'entrée pour l'outil CLI de GPT Genius.

Ce module sert de point d'entrée pour une interface en ligne de commande (CLI).
Il est conçu pour interagir avec les modèles de langage d'OpenAI.
Le module fournit des fonctionnalités pour :
- Charger les variables d'environnement nécessaires,
- Configurer divers paramètres pour l'interaction IA,
- Gérer la génération ou l'amélioration de projets de code.
"""

import logging
import os
import sys
from pathlib import Path

import openai
import typer
from dotenv import load_dotenv
from termcolor import colored

from gpt_genius.core.ai import AI
from gpt_genius.core.default.disk_execution_env import DiskExecutionEnv
from gpt_genius.core.default.disk_memory import DiskMemory
from gpt_genius.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_genius.core.default.simple_agent import SimpleAgent
from gpt_genius.core.files_dict import FilesDict
from gpt_genius.core.preprompts_holder import PrepromptsHolder
from gpt_genius.core.prompt import Prompt

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]}
)


def load_env_if_needed():
    """
    Charge les variables d'environnement si OPENAI_API_KEY n'est pas déjà définie.

    Cette fonction vérifie si la variable d'environnement OPENAI_API_KEY est définie,
    et si ce n'est pas le cas, elle tente de la charger depuis un fichier .env dans le
    répertoire de travail courant. Elle définit ensuite openai.api_key pour une utilisation
    dans l'application.
    """
    # Nous avons toutes ces vérifications pour des raisons héritées...
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv()
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

    openai.api_key = os.getenv("OPENAI_API_KEY")

    if os.getenv("ANTHROPIC_API_KEY") is None:
        load_dotenv()
    if os.getenv("ANTHROPIC_API_KEY") is None:
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


def load_prompt(
    input_repo: DiskMemory,
    improve_mode: bool,
    prompt_file: str,
) -> Prompt:
    """
    Charge ou demande un prompt à l'utilisateur basé sur le mode.

    Args:
        input_repo: L'objet mémoire disque où les prompts et autres données sont stockés
        improve_mode: Drapeau indiquant si l'application est en mode amélioration
        prompt_file: Le fichier de prompt à utiliser

    Returns:
        Le prompt chargé ou saisi
    """
    if os.path.isdir(prompt_file):
        raise ValueError(
            f"Le chemin vers le prompt, {prompt_file}, existe déjà comme répertoire. Aucun prompt ne peut être lu depuis celui-ci. Veuillez spécifier un fichier de prompt en utilisant --prompt_file"
        )
    prompt_str = input_repo.get(prompt_file)
    if prompt_str:
        print(colored("Utilisation du prompt depuis le fichier:", "green"), prompt_file)
        print(prompt_str)
    else:
        if not improve_mode:
            prompt_str = input(
                "\nQuelle application voulez-vous que GPT Genius génère ?\n"
            )
        else:
            prompt_str = input("\nComment voulez-vous améliorer l'application ?\n")

    return Prompt(prompt_str)


@app.command(
    help="""
        GPT Genius vous permet de :

        \b
        - Spécifier un logiciel en langage naturel
        - Vous asseoir et regarder comme une IA écrit et exécute le code
        - Demander à l'IA d'implémenter des améliorations
    """
)
def main(
    project_path: str = typer.Argument(".", help="chemin"),
    model: str = typer.Option(
        os.environ.get("MODEL_NAME", "gpt-4o"), "--model", "-m", help="chaîne id du modèle"
    ),
    temperature: float = typer.Option(
        0.1,
        "--temperature",
        "-t",
        help="Contrôle la randomité : valeurs plus basses pour des sorties plus focalisées et déterministes",
    ),
    improve_mode: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Améliorer un projet existant en modifiant les fichiers.",
    ),
    azure_endpoint: str = typer.Option(
        "",
        "--azure",
        "-a",
        help="""Endpoint pour votre Service Azure OpenAI (https://xx.openai.azure.com).
            Dans ce cas, le modèle donné est le nom de déploiement choisi dans Azure AI Studio.""",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Activer la journalisation verbeuse pour le débogage."
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Activer le mode débogage pour le débogage."
    ),
    prompt_file: str = typer.Option(
        "prompt",
        "--prompt_file",
        help="Chemin relatif vers un fichier texte contenant un prompt.",
    ),
):
    """
    Le point d'entrée principal pour l'outil CLI qui génère ou améliore un projet.

    Cette fonction configure l'outil CLI, charge les variables d'environnement, initialise
    l'IA, et traite la demande de l'utilisateur pour générer ou améliorer un projet
    basé sur les arguments fournis.

    Args:
        project_path: Le chemin de fichier vers le répertoire du projet
        model: La chaîne ID du modèle pour l'IA
        temperature: Le réglage de température pour les réponses de l'IA
        improve_mode: Drapeau indiquant s'il faut améliorer un projet existant
        azure_endpoint: L'endpoint pour les services Azure OpenAI
        verbose: Drapeau indiquant s'il faut activer la journalisation verbeuse
        debug: Drapeau indiquant s'il faut activer le mode débogage
        prompt_file: Chemin relatif vers un fichier texte contenant un prompt

    Returns:
        None
    """
    if debug:
        import pdb
        sys.excepthook = lambda *_: pdb.pm()

    # Configuration de la journalisation
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    load_env_if_needed()

    ai = AI(
        model_name=model,
        temperature=temperature,
        azure_endpoint=azure_endpoint,
    )

    path = Path(project_path)
    print("Exécution de GPT Genius dans", path.absolute(), "\n")

    prompt = load_prompt(
        DiskMemory(path),
        improve_mode,
        prompt_file,
    )

    preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)
    memory = DiskMemory(memory_path(project_path))
    memory.archive_logs()

    execution_env = DiskExecutionEnv()
    agent = SimpleAgent(
        memory=memory,
        execution_env=execution_env,
        ai=ai,
        preprompts_holder=preprompts_holder,
    )

    if improve_mode:
        print("Mode amélioration pas encore implémenté dans cette version simplifiée.")
        print("Utilisation du mode génération à la place...")
        files_dict = agent.init(prompt)
    else:
        files_dict = agent.init(prompt)

    # Sauvegarder les fichiers
    from gpt_genius.core.default.file_store import FileStore
    files = FileStore(project_path)
    files.push(files_dict)

    if ai.token_usage_log.is_openai_model():
        print("Coût total de l'API : $ ", ai.token_usage_log.usage_cost())
    elif os.getenv("LOCAL_MODEL"):
        print("Coût total de l'API : $ 0.0 car nous utilisons un LLM local.")
    else:
        print("Tokens totaux utilisés : ", ai.token_usage_log.total_tokens())

    print(f"\nFichiers générés dans : {path.absolute()}")


if __name__ == "__main__":
    app()