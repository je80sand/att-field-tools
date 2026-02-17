import sys
from pathlib import Path

# Add project root to Python path so tests can import att_tools.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))