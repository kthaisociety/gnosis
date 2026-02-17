import sys
from pathlib import Path

from dotenv import load_dotenv

# Load eval service .env for tests
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Add src directory to sys.path so tests can find the eval package
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
