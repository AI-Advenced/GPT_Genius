"""
Module de gestion de l'usage des tokens pour GPT Genius.
"""

import base64
import io
import logging
import math
from dataclasses import dataclass
from typing import List, Union

import tiktoken
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from PIL import Image

# Gestion de l'import qui a bougé dans les versions récentes de langchain
try:
    from langchain.callbacks.openai_info import get_openai_token_cost_for_model
except ImportError:
    try:
        from langchain_community.callbacks.openai_info import get_openai_token_cost_for_model
    except ImportError:
        # Fallback si aucune version n'est disponible
        def get_openai_token_cost_for_model(model_name, tokens, is_completion=False):
            """Fallback fonction si l'import échoue."""
            # Coûts approximatifs pour GPT-4 (à ajuster selon les vrais coûts)
            if is_completion:
                return tokens * 0.00006  # ~$0.06 per 1k tokens output
            else:
                return tokens * 0.00003  # ~$0.03 per 1k tokens input

Message = Union[AIMessage, HumanMessage, SystemMessage]

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """
    Dataclass représentant les statistiques d'usage de tokens pour une étape de conversation.
    """
    step_name: str
    in_step_prompt_tokens: int
    in_step_completion_tokens: int
    in_step_total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int


class Tokenizer:
    """
    Tokenizer pour compter les tokens dans le texte.
    """

    def __init__(self, model_name):
        self.model_name = model_name
        self._tiktoken_tokenizer = (
            tiktoken.encoding_for_model(model_name)
            if "gpt-4" in model_name or "gpt-3.5" in model_name
            else tiktoken.get_encoding("cl100k_base")
        )

    def num_tokens(self, txt: str) -> int:
        """
        Obtient le nombre de tokens dans un texte.

        Args:
            txt: Le texte pour compter les tokens

        Returns:
            Le nombre de tokens dans le texte
        """
        return len(self._tiktoken_tokenizer.encode(txt))

    def num_tokens_for_base64_image(
        self, image_base64: str, detail: str = "high"
    ) -> int:
        """
        Calcule la taille des tokens pour une image encodée en base64 basée sur les règles 
        de calcul de tokens d'OpenAI.

        Args:
            image_base64: La chaîne encodée en base64 de l'image
            detail: Le niveau de détail de l'image, 'low' ou 'high'

        Returns:
            La taille des tokens de l'image
        """
        if detail == "low":
            return 85  # Coût fixe pour les images de faible détail

        # Décoder l'image depuis base64
        image_data = base64.b64decode(image_base64)

        # Convertir les données d'octets en image pour l'extraction de taille
        image = Image.open(io.BytesIO(image_data))

        # Calculer l'échelle initiale pour tenir dans 2048 carré tout en maintenant le ratio d'aspect
        max_dimension = max(image.size)
        scale_factor = min(2048 / max_dimension, 1)  # S'assurer qu'on ne met pas à l'échelle vers le haut
        new_width = int(image.size[0] * scale_factor)
        new_height = int(image.size[1] * scale_factor)

        # Mettre à l'échelle de sorte que le côté le plus court soit 768px
        shortest_side = min(new_width, new_height)
        if shortest_side > 768:
            resize_factor = 768 / shortest_side
            new_width = int(new_width * resize_factor)
            new_height = int(new_height * resize_factor)

        # Calculer le nombre de tuiles 512px nécessaires
        width_tiles = math.ceil(new_width / 512)
        height_tiles = math.ceil(new_height / 512)
        total_tiles = width_tiles * height_tiles

        # Chaque tuile coûte 170 tokens, plus un coût de base de 85 tokens pour le détail élevé
        token_cost = total_tiles * 170 + 85

        return token_cost

    def num_tokens_from_messages(self, messages: List[Message]) -> int:
        """
        Obtient le nombre total de tokens utilisés par une liste de messages, comptabilisant 
        le texte et les images encodées en base64.

        Args:
            messages: La liste des messages pour compter les tokens

        Returns:
            Le nombre total de tokens utilisés par les messages
        """
        n_tokens = 0
        for message in messages:
            n_tokens += 4  # Compte pour les tokens de cadrage des messages

            if isinstance(message.content, str):
                # Le contenu est une chaîne simple
                n_tokens += self.num_tokens(message.content)
            elif isinstance(message.content, list):
                # Le contenu est une liste, potentiellement mélangée avec texte et images
                for item in message.content:
                    if item.get("type") == "text":
                        n_tokens += self.num_tokens(item["text"])
                    elif item.get("type") == "image_url":
                        image_detail = item["image_url"].get("detail", "high")
                        image_base64 = item["image_url"].get("url")
                        n_tokens += self.num_tokens_for_base64_image(
                            image_base64, detail=image_detail
                        )

            n_tokens += 2  # Compte pour les tokens de cadrage de la réponse de l'assistant

        return n_tokens


class TokenUsageLog:
    """
    Représente un journal des statistiques d'usage de tokens pour une conversation.
    """

    def __init__(self, model_name):
        self.model_name = model_name
        self._cumulative_prompt_tokens = 0
        self._cumulative_completion_tokens = 0
        self._cumulative_total_tokens = 0
        self._log = []
        self._tokenizer = Tokenizer(model_name)

    def update_log(self, messages: List[Message], answer: str, step_name: str) -> None:
        """
        Met à jour le journal d'usage des tokens avec le nombre de tokens utilisés dans l'étape actuelle.

        Args:
            messages: La liste des messages dans la conversation
            answer: La réponse de l'IA
            step_name: Le nom de l'étape
        """
        prompt_tokens = self._tokenizer.num_tokens_from_messages(messages)
        completion_tokens = self._tokenizer.num_tokens(answer)
        total_tokens = prompt_tokens + completion_tokens

        self._cumulative_prompt_tokens += prompt_tokens
        self._cumulative_completion_tokens += completion_tokens
        self._cumulative_total_tokens += total_tokens

        self._log.append(
            TokenUsage(
                step_name=step_name,
                in_step_prompt_tokens=prompt_tokens,
                in_step_completion_tokens=completion_tokens,
                in_step_total_tokens=total_tokens,
                total_prompt_tokens=self._cumulative_prompt_tokens,
                total_completion_tokens=self._cumulative_completion_tokens,
                total_tokens=self._cumulative_total_tokens,
            )
        )

    def log(self) -> List[TokenUsage]:
        """
        Obtient le journal d'usage des tokens.

        Returns:
            Un journal des détails d'usage des tokens par étape dans la conversation
        """
        return self._log

    def format_log(self) -> str:
        """
        Formate le journal d'usage des tokens comme une chaîne CSV.

        Returns:
            Le journal d'usage des tokens formaté comme une chaîne CSV
        """
        result = "step_name,prompt_tokens_in_step,completion_tokens_in_step,total_tokens_in_step,total_prompt_tokens,total_completion_tokens,total_tokens\n"
        for log in self._log:
            result += f"{log.step_name},{log.in_step_prompt_tokens},{log.in_step_completion_tokens},{log.in_step_total_tokens},{log.total_prompt_tokens},{log.total_completion_tokens},{log.total_tokens}\n"
        return result

    def is_openai_model(self) -> bool:
        """
        Vérifie si le modèle est un modèle OpenAI.

        Returns:
            True si le modèle est un modèle OpenAI, False sinon
        """
        return "gpt" in self.model_name.lower()

    def total_tokens(self) -> int:
        """
        Retourne le nombre total de tokens utilisés dans la conversation.

        Returns:
            Le nombre total de tokens utilisés dans la conversation
        """
        return self._cumulative_total_tokens

    def usage_cost(self) -> float | None:
        """
        Retourne le coût total en USD de l'usage de l'API.

        Returns:
            Coût en USD
        """
        if not self.is_openai_model():
            return None

        try:
            result = 0
            for log in self.log():
                result += get_openai_token_cost_for_model(
                    self.model_name, log.total_prompt_tokens, is_completion=False
                )
                result += get_openai_token_cost_for_model(
                    self.model_name, log.total_completion_tokens, is_completion=True
                )
            return result
        except Exception as e:
            logger.error(f"Erreur lors du calcul du coût d'usage : {e}")
            return None