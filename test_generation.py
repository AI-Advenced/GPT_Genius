#!/usr/bin/env python3
"""
Test de génération de code sans API (simulation).
"""

import tempfile
import os
from gpt_genius.core.prompt import Prompt
from gpt_genius.core.files_dict import FilesDict  
from gpt_genius.core.default.simple_agent import SimpleAgent

def test_without_api():
    """Test du workflow sans vraie API."""
    print("🧪 Test du workflow GPT Genius (simulation sans API)")
    
    # Créer un prompt
    prompt = Prompt("Créer une calculatrice simple en Python")
    print(f"✅ Prompt créé: {prompt.text}")
    
    # Créer un répertoire temporaire
    temp_dir = tempfile.mkdtemp()
    print(f"✅ Répertoire temporaire: {temp_dir}")
    
    try:
        # Simuler des fichiers générés
        files = FilesDict()
        files["calculator.py"] = '''#!/usr/bin/env python3
"""
Calculatrice simple en Python.
"""

class Calculator:
    """Classe pour les opérations de base."""
    
    def add(self, a: float, b: float) -> float:
        """Addition de deux nombres."""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """Soustraction de deux nombres."""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiplication de deux nombres."""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """Division de deux nombres."""
        if b == 0:
            raise ValueError("Division par zéro impossible")
        return a / b

def main():
    """Point d'entrée principal."""
    calc = Calculator()
    
    print("=== Calculatrice Simple ===")
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")  
    print(f"5 * 6 = {calc.multiply(5, 6)}")
    print(f"15 / 3 = {calc.divide(15, 3)}")

if __name__ == "__main__":
    main()
'''
        
        files["requirements.txt"] = "# Aucune dépendance externe requise pour cette calculatrice\n"
        
        files["README.md"] = """# Calculatrice Simple

Une calculatrice Python simple avec les opérations de base.

## Usage

```bash
python calculator.py
```

## Fonctionnalités

- Addition
- Soustraction  
- Multiplication
- Division (avec gestion de la division par zéro)
"""
        
        print(f"✅ Fichiers simulés créés: {len(files)} fichiers")
        
        # Tester la sauvegarde des fichiers
        from gpt_genius.core.default.file_store import FileStore
        
        store = FileStore(temp_dir)
        store.push(files)
        
        # Vérifier que les fichiers existent
        created_files = store.pull()
        print(f"✅ Fichiers sauvegardés et récupérés: {len(created_files)} fichiers")
        
        for filename in created_files.keys():
            filepath = os.path.join(temp_dir, filename)
            if os.path.exists(filepath):
                print(f"  📄 {filename} - ✅ Existant")
            else:
                print(f"  📄 {filename} - ❌ Manquant")
                
        print(f"\n📁 Fichiers créés dans: {temp_dir}")
        print("🎉 Test de simulation réussi!")
        
        return temp_dir
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return None

if __name__ == "__main__":
    result_dir = test_without_api()
    if result_dir:
        print(f"\nVous pouvez examiner les fichiers générés dans: {result_dir}")
        print("Pour tester la calculatrice:")
        print(f"  cd {result_dir}")
        print(f"  python calculator.py")