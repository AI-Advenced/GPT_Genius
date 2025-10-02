#!/usr/bin/env python3

print("Test d'import de GPT Genius...")

try:
    import gpt_genius
    print(f"✅ Import du module principal réussi")
    print(f"Attributs disponibles: {dir(gpt_genius)}")
    
    if hasattr(gpt_genius, '__version__'):
        print(f"Version: {gpt_genius.__version__}")
    else:
        print("❌ Attribut __version__ non trouvé")
        
except Exception as e:
    print(f"❌ Erreur d'import: {e}")

print("\nTest d'import des classes individuelles...")

try:
    from gpt_genius.core.prompt import Prompt
    print("✅ Prompt importé avec succès")
    
    from gpt_genius.core.files_dict import FilesDict  
    print("✅ FilesDict importé avec succès")
    
    from gpt_genius.core.ai import AI
    print("✅ AI importé avec succès")
    
except Exception as e:
    print(f"❌ Erreur d'import des classes: {e}")

print("\nTest création d'objets...")

try:
    prompt = Prompt("test")
    print(f"✅ Prompt créé: {prompt.text}")
    
    files = FilesDict()
    files["test.py"] = "print('hello')"
    print(f"✅ FilesDict créé avec {len(files)} fichier(s)")
    
except Exception as e:
    print(f"❌ Erreur de création d'objets: {e}")

print("\nTest terminé!")