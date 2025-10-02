"""
Module IA pour GPT Genius.

Ce module fournit une classe AI qui interface avec les modèles de langage pour effectuer 
diverses tâches comme démarrer une conversation, faire avancer la conversation, et gérer 
la sérialisation des messages. Il inclut aussi des stratégies de backoff pour gérer 
les erreurs de limite de taux de l'API OpenAI.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, List, Optional, Union

import backoff
import openai
import pyperclip

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models.base import BaseChatModel
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    messages_from_dict,
    messages_to_dict,
)
from langchain_anthropic import ChatAnthropic
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from gpt_genius.core.token_usage import TokenUsageLog

# Type hint pour un message de chat
Message = Union[AIMessage, HumanMessage, SystemMessage]

# Configuration du logging
logger = logging.getLogger(__name__)


class AI:
    """
    Une classe qui interface avec les modèles de langage pour la gestion de conversation et la sérialisation des messages.

    Cette classe fournit des méthodes pour démarrer et faire avancer les conversations, gérer la sérialisation 
    des messages, et implémenter des stratégies de backoff pour les erreurs de limite de taux lors de 
    l'interaction avec l'API OpenAI.
    """

    def __init__(
        self,
        model_name="gpt-4o",
        temperature=0.1,
        azure_endpoint=None,
        streaming=True,
        vision=False,
    ):
        """
        Initialise la classe AI.

        Args:
            model_name: Le nom du modèle à utiliser, par défaut "gpt-4o"
            temperature: La température à utiliser pour le modèle, par défaut 0.1
            azure_endpoint: L'endpoint Azure optionnel
            streaming: Utiliser le streaming ou non
            vision: Support de la vision ou non
        """
        self.temperature = temperature
        self.azure_endpoint = azure_endpoint
        self.model_name = model_name
        self.streaming = streaming
        self.vision = (
            ("vision-preview" in model_name)
            or ("gpt-4-turbo" in model_name and "preview" not in model_name)
            or ("claude" in model_name)
            or ("gpt-4o" in model_name)
        )
        self.llm = self._create_chat_model()
        self.token_usage_log = TokenUsageLog(model_name)

        logger.debug(f"Utilisation du modèle {self.model_name}")

    def start(self, system: str, user: Any, *, step_name: str) -> List[Message]:
        """
        Démarre la conversation avec un message système et un message utilisateur.

        Args:
            system: Le contenu du message système
            user: Le contenu du message utilisateur
            step_name: Le nom de l'étape

        Returns:
            La liste des messages dans la conversation
        """
        messages: List[Message] = [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]
        return self.next(messages, step_name=step_name)

    def _extract_content(self, content):
        """
        Extrait le contenu textuel d'un message, supportant les types string et list.
        
        Args:
            content: Le contenu du message, qui peut être une chaîne ou une liste

        Returns:
            Le contenu textuel extrait
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list) and content and "text" in content[0]:
            # Assumant la structure du contenu liste est [{'type': 'text', 'text': 'Du texte'}, ...]
            return content[0]["text"]
        else:
            return ""

    def _collapse_text_messages(self, messages: List[Message]):
        """
        Combine les messages consécutifs du même type en un seul message, où si le contenu 
        du message est de type liste, le contenu du premier élément texte est pris.

        Args:
            messages: La liste des messages à fusionner

        Returns:
            La liste des messages après fusion des messages consécutifs du même type
        """
        collapsed_messages = []
        if not messages:
            return collapsed_messages

        previous_message = messages[0]
        combined_content = self._extract_content(previous_message.content)

        for current_message in messages[1:]:
            if current_message.type == previous_message.type:
                combined_content += "\n\n" + self._extract_content(
                    current_message.content
                )
            else:
                collapsed_messages.append(
                    previous_message.__class__(content=combined_content)
                )
                previous_message = current_message
                combined_content = self._extract_content(current_message.content)

        collapsed_messages.append(previous_message.__class__(content=combined_content))
        return collapsed_messages

    def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        """
        Fait avancer la conversation en envoyant l'historique des messages 
        au LLM et en mettant à jour avec la réponse.

        Args:
            messages: La liste des messages dans la conversation
            prompt: Le prompt à utiliser, par défaut None
            step_name: Le nom de l'étape

        Returns:
            La liste mise à jour des messages dans la conversation
        """
        if prompt:
            messages.append(HumanMessage(content=prompt))

        logger.debug(
            "Création d'une nouvelle complétion de chat : %s",
            "\n".join([m.pretty_repr() for m in messages]),
        )

        if not self.vision:
            messages = self._collapse_text_messages(messages)

        response = self.backoff_inference(messages)

        self.token_usage_log.update_log(
            messages=messages, answer=response.content, step_name=step_name
        )
        messages.append(response)
        logger.debug(f"Complétion de chat terminée : {messages}")

        return messages

    @backoff.on_exception(backoff.expo, openai.RateLimitError, max_tries=7, max_time=45)
    def backoff_inference(self, messages):
        """
        Effectue l'inférence en utilisant le modèle de langage tout en implémentant 
        une stratégie de backoff exponentiel.

        Args:
            messages: Une liste de messages de chat qui seront passés au modèle de langage

        Returns:
            La sortie du modèle de langage après traitement des messages fournis

        Raises:
            openai.error.RateLimitError: Si le nombre de tentatives dépasse le maximum ou 
            si la limite de taux persiste au-delà du temps alloué
        """
        return self.llm.invoke(messages)

    @staticmethod
    def serialize_messages(messages: List[Message]) -> str:
        """
        Sérialise une liste de messages en chaîne JSON.

        Args:
            messages: La liste des messages à sérialiser

        Returns:
            Les messages sérialisés comme chaîne JSON
        """
        return json.dumps(messages_to_dict(messages))

    @staticmethod
    def deserialize_messages(jsondictstr: str) -> List[Message]:
        """
        Désérialise une chaîne JSON en liste de messages.

        Args:
            jsondictstr: La chaîne JSON à désérialiser

        Returns:
            La liste désérialisée de messages
        """
        data = json.loads(jsondictstr)
        # Modifie la propriété implicite is_chunk à TOUJOURS faux
        # car le schéma Message de Langchain est plus strict
        prevalidated_data = [
            {**item, "tools": {**item.get("tools", {}), "is_chunk": False}}
            for item in data
        ]
        return list(messages_from_dict(prevalidated_data))

    def _create_chat_model(self) -> BaseChatModel:
        """
        Crée un modèle de chat avec le nom de modèle et la température spécifiés.

        Returns:
            Le modèle de chat créé
        """
        if self.azure_endpoint:
            return AzureChatOpenAI(
                azure_endpoint=self.azure_endpoint,
                openai_api_version=os.getenv(
                    "OPENAI_API_VERSION", "2024-05-01-preview"
                ),
                deployment_name=self.model_name,
                openai_api_type="azure",
                streaming=self.streaming,
                callbacks=[StreamingStdOutCallbackHandler()],
            )
        elif "claude" in self.model_name:
            return ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                callbacks=[StreamingStdOutCallbackHandler()],
                streaming=self.streaming,
                max_tokens_to_sample=4096,
            )
        elif self.vision:
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                streaming=self.streaming,
                callbacks=[StreamingStdOutCallbackHandler()],
                max_tokens=4096,  # les modèles de vision ont par défaut des limites de tokens faibles
            )
        else:
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                streaming=self.streaming,
                callbacks=[StreamingStdOutCallbackHandler()],
            )


def serialize_messages(messages: List[Message]) -> str:
    """Fonction utilitaire pour sérialiser les messages."""
    return AI.serialize_messages(messages)


class ClipboardAI(AI):
    """
    Version clipboard de l'IA pour des tests ou des cas d'usage spéciaux.
    """
    
    def __init__(self, **_):
        self.vision = False
        self.token_usage_log = TokenUsageLog("clipboard_llm")

    @staticmethod
    def serialize_messages(messages: List[Message]) -> str:
        return "\n\n".join([f"{m.type}:\n{m.content}" for m in messages])

    @staticmethod
    def multiline_input():
        print("Entrez/Collez votre contenu. Ctrl-D ou Ctrl-Z (Windows) pour sauvegarder.")
        content = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            content.append(line)
        return "\n".join(content)

    def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        """
        Pas encore complètement supporté.
        """
        if prompt:
            messages.append(HumanMessage(content=prompt))

        logger.debug(f"Création d'une nouvelle complétion de chat : {messages}")

        msgs = self.serialize_messages(messages)
        pyperclip.copy(msgs)
        Path("clipboard.txt").write_text(msgs)
        print(
            "Messages copiés dans le presse-papiers et écrits dans clipboard.txt,",
            len(msgs),
            "caractères au total",
        )

        response = self.multiline_input()

        messages.append(AIMessage(content=response))
        logger.debug(f"Complétion de chat terminée : {messages}")

        return messages