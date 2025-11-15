"""Entry point wrapper for CLI to work as console script."""

import sys
from pathlib import Path

# Add src to path so we can import cli
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from cli import cli

if __name__ == "__main__":
    cli()

