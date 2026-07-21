"""DriftAdapt Project Bootstrap Script.

Author: DriftAdapt Contributors
Purpose: Automatically initializes the required folder structures for DriftAdapt.
Future Integration: Executed as part of setup or CI workflows to prepare local environment paths.
"""

import sys
from pathlib import Path

# Define required directories relative to the repository root
REQUIRED_DIRECTORIES = [
    "logs",
    "metrics",
    "checkpoints",

    "datasets/raw",
    "datasets/processed",
    "datasets/partitions",
    "datasets/synthetic",
    "experiments/configs",
    "experiments/results",
    "experiments/figures",
    "experiments/reports",
    "configs",
    "tests/unit",
    "tests/integration",
    "tests/system",
    "docs",
    "notebooks",
]


def bootstrap_project() -> int:
    """Creates the necessary directories for the project.

    This function is idempotent. It can be run multiple times safely.
    For each directory, it creates a placeholder '.gitkeep' file to ensure
    git tracks the folder structure even when empty.
    """
    print("Initializing repository directories...")

    # Repository root is the parent directory of 'scripts'
    root_dir = Path(__file__).resolve().parent.parent

    success_count = 0
    created_count = 0

    for dir_path_str in REQUIRED_DIRECTORIES:
        target_dir = root_dir / dir_path_str
        try:
            if not target_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {dir_path_str}")
                created_count += 1
            else:
                # Directory already exists, print debug message
                pass

            # Write .gitkeep inside the directory to preserve structure in git
            gitkeep_file = target_dir / ".gitkeep"
            if not gitkeep_file.exists():
                gitkeep_file.touch()

            success_count += 1
        except Exception as e:
            print(f"Error creating directory {dir_path_str}: {e}", file=sys.stderr)

    print("\nInitialization Summary:")
    print(f"Total required directories: {len(REQUIRED_DIRECTORIES)}")
    print(f"Successfully verified/created: {success_count}")
    print(f"New directories created: {created_count}")

    if success_count == len(REQUIRED_DIRECTORIES):
        print("\nProject bootstrapped successfully!")
        return 0
    else:
        print("\nWarning: Some directories could not be created.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(bootstrap_project())
