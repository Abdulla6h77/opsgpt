from pathlib import Path
import sys


# Ensure project root is importable so sibling top-level packages (e.g. `ai`) resolve
# whether the app is launched from project root or from the backend directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
project_root_str = str(PROJECT_ROOT)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)
