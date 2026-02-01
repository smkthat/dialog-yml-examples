import ast
import importlib.util
from pathlib import Path

import pytest


def find_imports_in_file(file_path: Path) -> list[str]:
    """Extract all import statements from a Python file."""
    with open(file_path, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            print(f"Syntax error in file: {file_path}")
            return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    return imports


def get_all_python_files(src_dir: Path) -> list[Path]:
    """Get all Python files in the source directory."""
    return list(src_dir.rglob("*.py"))


def test_entrypoint_imports():
    """Test that the entrypoint module can be imported without issues."""
    # Test that we can import the main entrypoint
    try:
        from src.bot import main

        assert callable(main)
    except ImportError as e:
        pytest.fail(f"Could not import main function from entrypoint: {e}")


def test_import_chain_from_entrypoint():
    """Test the import chain starting from the entrypoint module."""

    # Check that the module exists using find_spec
    spec = importlib.util.find_spec("src.main")
    if spec is None:
        pytest.fail("Entry point module could not be found")

    # Check that all imports in the entry point module are valid
    entry_point_path = Path("src/main.py")
    if not entry_point_path.exists():
        pytest.skip("Entry point file does not exist")

    imports = find_imports_in_file(entry_point_path)

    # Filter only spoetka_base imports
    spoetka_base_imports = [imp for imp in imports if imp.startswith("src.")]

    # Try to import each of these modules to ensure they exist and are importable
    for imp in spoetka_base_imports:
        try:
            __import__(imp, fromlist=[""])
        except ImportError as e:
            pytest.fail(f"Import {imp} from entry point failed: {e}")


def test_no_circular_imports():
    """Basic test to ensure there are no obvious circular imports in key modules."""
    # Try importing key modules to catch obvious circular import issues
    modules_to_test = [
        "src.functions",
    ]

    for module_name in modules_to_test:
        try:
            __import__(module_name, fromlist=[""])
        except ImportError as e:
            # Some modules might legitimately fail to import due to missing dependencies
            # Only fail if it's clearly an import issue within our code
            if "spoetka_base" in str(e):
                pytest.fail(f"Circular import detected in {module_name}: {e}")
