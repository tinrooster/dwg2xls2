import os
import pathlib
from typing import Dict, Union

# Type alias for our nested structure
ProjectStructure = Dict[str, Union[str, Dict]]

def create_project_structure() -> None:
    """
    Creates the project directory structure and empty files for the dwg2xls application.
    Handles existing directories and provides feedback on the creation process.
    """
    # Base directory structure
    structure: ProjectStructure = {
        "src/dwg2xls": {
            "__init__.py": "",
            "core": {
                "__init__.py": "",
                "autocad": {
                    "__init__.py": "",
                    "base_connector.py": "",
                    "dcom_connector.py": "",
                    "lt_connector.py": ""
                },
                "excel": {
                    "__init__.py": "",
                    "exporter.py": ""
                }
            },
            "gui": {
                "__init__.py": "",
                "widgets": {
                    "__init__.py": "",
                    "drawing_preview.py": "",
                    "field_mapping.py": ""
                },
                "main_window.py": "",
                "styles.py": ""
            },
            "utils": {
                "__init__.py": "",
                "logger.py": "",
                "config.py": "",
                "exceptions.py": ""  # Added for custom exceptions
            },
            "main.py": "",
            "requirements.txt": "",  # Added for dependencies
            "README.md": ""  # Added for project documentation
        }
    }

    def create_directories(base_path: pathlib.Path, structure: ProjectStructure) -> None:
        """
        Recursively creates directories and files based on the provided structure.
        
        Args:
            base_path: The root path to create the structure in
            structure: Dictionary representing the directory/file structure
        """
        try:
            for name, content in structure.items():
                path = base_path / name
                if isinstance(content, dict):
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"Created directory: {path}")
                    create_directories(path, content)
                else:
                    if not path.exists():
                        path.touch()
                        print(f"Created file: {path}")
                    else:
                        print(f"File already exists: {path}")
        except PermissionError:
            print(f"Error: Permission denied while creating {path}")
        except OSError as e:
            print(f"Error creating {path}: {e}")

    # Create the structure
    try:
        base_dir = pathlib.Path(".")
        create_directories(base_dir, structure)
        print("\nProject structure created successfully!")
    except Exception as e:
        print(f"\nError creating project structure: {e}")

if __name__ == "__main__":
    create_project_structure()
