#!/usr/bin/env python3
"""
Exemple d'usage basique de GPT Genius.

Ce script montre comment utiliser GPT Genius programmatiquement 
pour générer du code à partir d'un prompt.
"""

import tempfile
from gpt_genius import SimpleAgent, Prompt, AI

def main():
    """Exemple d'usage basique."""
    # Configuration de l'IA
    ai = AI(model_name="gpt-4o", temperature=0.1)
    
    # Création d'un agent avec un répertoire temporaire
    agent = SimpleAgent.with_default_config(
        path=tempfile.mkdtemp(),
        ai=ai
    )
    
    # Création d'un prompt
    prompt = Prompt("Créer une calculatrice simple en Python avec les opérations de base")
    
    try:
        # Génération du code
        print("🚀 Génération du code en cours...")
        files = agent.init(prompt)
        
        # Affichage des résultats
        print("✅ Code généré avec succès!")
        print(f"📁 Nombre de fichiers créés: {len(files)}")
        
        for filename, content in files.items():
            print(f"\n📄 {filename}:")
            print("─" * 50)
            print(content[:200] + "..." if len(content) > 200 else content)
            
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")

if __name__ == "__main__":
    main()