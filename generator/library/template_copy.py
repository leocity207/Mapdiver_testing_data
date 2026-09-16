import shutil
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

FOLDERS_TO_COPY_TO_DATA = [
    "calendar_patterns",
    "stop_patterns"
]

IMAGES = [
    Path("images") / "map.svg",
    Path("images") / "logo.svg",
    Path("images") / "favicon.ico",
    Path("images") / "train-animation.svg",
]

META_FILES = [
    "calendar_patterns.json",
    "landmarks.json",
    "networks.json",
    "operators.json",
    "organisers.json",
    "stop_patterns.json",
    "territories.json",
]

STYLES_FOLDER = Path("styles")

CONFIGS_FILES = [
    "app_config.json",
    "map_config.json",
    "network_config.json",
]

def copy_template_files(output_dir: str) -> None:
    """
    Copy the template files into the output directory.

    Existing files with the same name are overwritten.
    """
    output_path = Path(output_dir)
    if not output_path.is_dir():
        raise ValueError(f"Output folder does not exist: {output_dir}")

    (output_path / "data").mkdir(parents=True, exist_ok=True)
    for folder in FOLDERS_TO_COPY_TO_DATA:
        copy_folder(TEMPLATE_DIR / folder, output_path / "data" / folder)

    (output_path / "images").mkdir(parents=True, exist_ok=True)
    for image in IMAGES:
        shutil.copyfile(TEMPLATE_DIR / image, output_path / image)
        
    for meta_file in META_FILES:
        shutil.copyfile(TEMPLATE_DIR / "meta" / meta_file, output_path / "data"  / meta_file)
    
    for config_file in CONFIGS_FILES:
        shutil.copyfile(TEMPLATE_DIR / Path("configs") /config_file, output_path / config_file)
    
    copy_folder(TEMPLATE_DIR /  STYLES_FOLDER, output_path / STYLES_FOLDER)


def copy_folder(input_folder: str, output_folder: str) -> None:
    """
    Copy the entire contents of input_folder into output_folder.

    Existing files with the same name are overwritten.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)

    if not input_path.is_dir():
        raise ValueError(f"Input folder does not exist: {input_folder}")

    shutil.copytree(
        input_path,
        output_path,
        dirs_exist_ok=True
    )
