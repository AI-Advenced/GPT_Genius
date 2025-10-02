"""
Module de gestion des prompts pour GPT Genius.
"""

import json
from typing import Dict, Optional


class Prompt:
    """
    Classe pour gérer les prompts avec support d'images et de contenus structurés.
    """
    
    def __init__(
        self,
        text: str,
        image_urls: Optional[Dict[str, str]] = None,
        entrypoint_prompt: str = "",
    ):
        """
        Initialise un prompt.
        
        Args:
            text: Le texte principal du prompt
            image_urls: Dictionnaire optionnel d'URLs d'images {nom: url}
            entrypoint_prompt: Prompt spécifique pour le point d'entrée
        """
        self.text = text
        self.image_urls = image_urls
        self.entrypoint_prompt = entrypoint_prompt

    def __repr__(self):
        return f"Prompt(text={self.text!r}, image_urls={self.image_urls!r})"

    def to_langchain_content(self):
        """
        Convertit le prompt en format compatible avec LangChain.
        
        Returns:
            Liste de contenus formatés pour LangChain
        """
        content = [{"type": "text", "text": f"Request: {self.text}"}]

        if self.image_urls:
            for name, url in self.image_urls.items():
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": url,
                        "detail": "low",
                    },
                }
                content.append(image_content)

        return content

    def to_dict(self):
        """
        Convertit le prompt en dictionnaire.
        
        Returns:
            Dictionnaire contenant les données du prompt
        """
        return {
            "text": self.text,
            "image_urls": self.image_urls,
            "entrypoint_prompt": self.entrypoint_prompt,
        }

    def to_json(self):
        """
        Convertit le prompt en JSON.
        
        Returns:
            Chaîne JSON représentant le prompt
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)