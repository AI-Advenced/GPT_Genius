"""
Tests pour les modules core de GPT Genius.
"""

import pytest
import tempfile
from pathlib import Path

from gpt_genius.core.prompt import Prompt
from gpt_genius.core.files_dict import FilesDict
from gpt_genius.core.default.disk_memory import DiskMemory
from gpt_genius.core.default.file_store import FileStore


class TestPrompt:
    """Tests pour la classe Prompt."""
    
    def test_create_prompt(self):
        """Test de création d'un prompt basique."""
        text = "Créer une application Python"
        prompt = Prompt(text)
        
        assert prompt.text == text
        assert prompt.image_urls is None
        assert prompt.entrypoint_prompt == ""
    
    def test_prompt_with_images(self):
        """Test de création d'un prompt avec images."""
        text = "Analyser cette image"
        images = {"image1": "data:image/png;base64,abc123"}
        prompt = Prompt(text, image_urls=images)
        
        assert prompt.text == text
        assert prompt.image_urls == images
    
    def test_to_dict(self):
        """Test de conversion en dictionnaire."""
        prompt = Prompt("test", entrypoint_prompt="run tests")
        result = prompt.to_dict()
        
        assert result["text"] == "test"
        assert result["entrypoint_prompt"] == "run tests"
        assert result["image_urls"] is None


class TestFilesDict:
    """Tests pour la classe FilesDict."""
    
    def test_create_files_dict(self):
        """Test de création d'un FilesDict."""
        files = FilesDict()
        files["main.py"] = "print('Hello World')"
        
        assert files["main.py"] == "print('Hello World')"
        assert len(files) == 1
    
    def test_type_validation(self):
        """Test de validation des types."""
        files = FilesDict()
        
        # Doit accepter string et Path
        files["test.py"] = "code"
        files[Path("test2.py")] = "code2"
        
        # Doit rejeter les types incorrects
        with pytest.raises(TypeError):
            files[123] = "code"
        
        with pytest.raises(TypeError):
            files["test.py"] = 123
    
    def test_to_chat(self):
        """Test de conversion pour chat."""
        files = FilesDict()
        files["main.py"] = "def hello():\n    print('Hello')"
        
        result = files.to_chat()
        assert "File: main.py" in result
        assert "def hello():" in result
        assert "```" in result


class TestDiskMemory:
    """Tests pour la classe DiskMemory."""
    
    def test_create_memory(self):
        """Test de création d'une mémoire disque."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = DiskMemory(temp_dir)
            assert memory.path == Path(temp_dir).absolute()
    
    def test_store_and_retrieve(self):
        """Test de stockage et récupération."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = DiskMemory(temp_dir)
            
            # Stocker un fichier
            memory["test.txt"] = "contenu de test"
            
            # Vérifier qu'il existe
            assert "test.txt" in memory
            assert memory["test.txt"] == "contenu de test"
    
    def test_iteration(self):
        """Test d'itération."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = DiskMemory(temp_dir)
            
            memory["file1.txt"] = "contenu1"
            memory["file2.txt"] = "contenu2"
            
            files = list(memory)
            assert len(files) == 2
            assert "file1.txt" in files
            assert "file2.txt" in files


class TestFileStore:
    """Tests pour la classe FileStore."""
    
    def test_create_file_store(self):
        """Test de création d'un FileStore."""
        store = FileStore()
        assert store.working_dir.exists()
        assert store.working_dir.is_dir()
    
    def test_push_and_pull(self):
        """Test de push et pull de fichiers."""
        store = FileStore()
        
        # Créer des fichiers
        files = FilesDict()
        files["main.py"] = "print('Hello World')"
        files["requirements.txt"] = "numpy>=1.0.0"
        
        # Push
        store.push(files)
        
        # Vérifier que les fichiers existent
        assert (store.working_dir / "main.py").exists()
        assert (store.working_dir / "requirements.txt").exists()
        
        # Pull
        pulled_files = store.pull()
        assert "main.py" in pulled_files
        assert "requirements.txt" in pulled_files
        assert pulled_files["main.py"] == "print('Hello World')"


def test_package_import():
    """Test que le package peut être importé correctement."""
    import gpt_genius
    
    assert hasattr(gpt_genius, 'AI')
    assert hasattr(gpt_genius, 'Prompt')
    assert hasattr(gpt_genius, 'FilesDict')
    assert hasattr(gpt_genius, 'SimpleAgent')
    assert gpt_genius.__version__ == "0.1.0"