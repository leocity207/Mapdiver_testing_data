import shutil
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent


def remove_folder(folder: str) -> None:
    path = CURRENT_DIR.parent / folder

    if path.is_dir():
        shutil.rmtree(path)
        print(f"Removed folder: {path}")
    else:
        print(f"Folder not found: {path}")


def remove_file(file: str) -> None:
    path = CURRENT_DIR.parent / file

    if path.is_file():
        path.unlink()
        print(f"Removed file: {path}")
    else:
        print(f"File not found: {path}")


def main():
    folders = [
        "data",
        "styles",
    ]

    files = [
        "app_config.json",
        "map_config.json",
        "network_config.json",
    ]

    for folder in folders:
        remove_folder(folder)

    for file in files:
        remove_file(file)


if __name__ == "__main__":
    main()