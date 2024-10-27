import os
import shutil
from pathlib import Path
from typing import Dict, List

def create_structure(base_path: str, version: str) -> None:
    """Creates a standardized project structure for the Broadcast Tools application.
    
    This script generates a basic project scaffold with the following structure:
    - src/
        - Core business logic
        - Configuration
        - Tests
    - docs/
        - Documentation files
    - scripts/
        - Utility scripts
    
    Args:
        base_path: The root directory where the project will be created
        version: Version string for the project (e.g., "v1.0.0")
    
    Project Scope:
        - Basic router analysis functionality
        - Configuration file handling
        - Local development setup
    
    Future Considerations:
        - Advanced analytics
        - Configuration UI
        - Monitoring capabilities
        - Extended documentation
    """
    project_name = f"broadcast-tools-{version}"
    project_path = Path(base_path) / project_name
    
    # Create main project directories
    directories = [
        "src",
        "src/core",
        "src/config",
        "src/tests",
        "docs",
        "scripts"
    ]
    
    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)
    
    # Create basic files
    files = {
        "README.md": """# Broadcast Tools {version}

A tool for router analysis and configuration.

## Setup
1. Clone the repository
2. Install dependencies
3. Run the application

## Project Structure
- src/: Main source code
- docs/: Documentation
- scripts/: Utility scripts

## Usage
[Add usage instructions here]
""".format(version=version),
        
        ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
.env
venv/

# IDE
.vscode/
.idea/

# Logs
*.log

# Local configuration
config.local.ini
""",
        
        "requirements.txt": """# Add your Python dependencies here
""",
        
        "src/__init__.py": "",
        "src/core/__init__.py": "",
        "src/config/__init__.py": "",
        "src/tests/__init__.py": ""
    }
    
    for file_path, content in files.items():
        with open(project_path / file_path, 'w') as f:
            f.write(content)
    
    print(f"Project structure created at: {project_path}")
