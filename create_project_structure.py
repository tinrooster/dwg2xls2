import os
import shutil
from pathlib import Path

def create_structure(base_path: str, version: str):
    """Create project folder structure"""
    
    # Base project paths
    project_root = Path(base_path) / f"broadcast-tools-{version}"
    backend_path = project_root / "backend"
    frontend_path = project_root / "frontend"

    # Backend structure
    backend_dirs = [
        "app/core",
        "app/api",
        "app/tests",
        "app/config",
    ]

    # Frontend structure
    frontend_dirs = [
        "src/components/RouterAnalysis",
        "src/components/Layout",
        "src/assets",
        "src/utils",
        "src/types",
    ]

    # Create directories
    for dir_path in backend_dirs:
        os.makedirs(backend_path / dir_path, exist_ok=True)

    for dir_path in frontend_dirs:
        os.makedirs(frontend_path / dir_path, exist_ok=True)

    # Create backend files
    backend_files = {
        "main.py": """from fastapi import FastAPI

app = FastAPI()
""",
        "requirements.txt": """fastapi
uvicorn
pydantic
""",
        "app/__init__.py": "",
        "app/core/__init__.py": "",
        "app/api/__init__.py": "",
        "app/config/__init__.py": "",
    }

    for file_path, content in backend_files.items():
        with open(backend_path / file_path, 'w') as f:
            f.write(content)

    # Create frontend files
    frontend_files = {
        "package.json": """{"name": "broadcast-tools-frontend","version": "0.1.0","private": true,"dependencies": {"@types/node": "^16.0.0","@types/react": "^17.0.0","@types/react-dom": "^17.0.0","antd": "^4.16.13","react": "^17.0.2","react-dom": "^17.0.2","typescript": "^4.4.3"}}""",
        "tsconfig.json": """{"compilerOptions": {"target": "es5","lib": ["dom", "dom.iterable", "esnext"],"allowJs": true,"skipLibCheck": true,"esModuleInterop": true,"allowSyntheticDefaultImports": true,"strict": true,"forceConsistentCasingInFileNames": true,"module": "esnext","moduleResolution": "node","resolveJsonModule": true,"isolatedModules": true,"noEmit": true,"jsx": "react-jsx"},"include": ["src"]}""",
        "src/index.tsx": """import React from 'react';import ReactDOM from 'react-dom';import App from './App';ReactDOM.render(<React.StrictMode><App /></React.StrictMode>,document.getElementById('root'));""",
        "src/App.tsx": """import React from 'react';const App: React.FC = () => {return (<div><h1>Broadcast Router Analysis</h1></div>);};export default App;"""
    }

    for file_path, content in frontend_files.items():
        with open(frontend_path / file_path, 'w') as f:
            f.write(content)

    # Create README
    readme_content = f"# Broadcast Tools {version}\n\n## Setup\n\n### Backend\n```\ncd backend\npip install -r requirements.txt\npython main.py\n```\n\n### Frontend\n```\ncd frontend\npm install\npm start\n```"
    
    with open(project_root / "README.md", 'w') as f:
        f.write(readme_content)

    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
.env
venv/

# Node
node_modules/
build/
.env.local
.env.
"""

    with open(project_root / ".gitignore", 'w') as f:
        f.write(gitignore_content)
