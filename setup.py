#!/usr/bin/env python3
"""Setup script for STL repair tool."""

import subprocess
import sys
from pathlib import Path


def main():
    """Install the STL repair tool."""
    project_root = Path(__file__).parent

    print("Installing STL Repair...")

    try:
        # Install the package in development mode
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=project_root,
            check=True,
        )

        print("✅ STL Repair installed successfully!")
        print("\nUsage:")
        print("  Use the wrapper script: ./stl-repair-blender.sh input.stl")
        print("  Or run within Blender Python environment directly")

    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
