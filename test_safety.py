from app.main import clean_path, sanitize_files
import pytest

def test_rejects_path_traversal():
    with pytest.raises(ValueError):
        clean_path("../secret.txt")

def test_rejects_env_file():
    with pytest.raises(ValueError):
        clean_path(".env")

def test_adds_required_files():
    result = sanitize_files({"main.py": "print('hello')"})
    assert "README.md" in result
    assert ".gitignore" in result
    assert ".env.example" in result
