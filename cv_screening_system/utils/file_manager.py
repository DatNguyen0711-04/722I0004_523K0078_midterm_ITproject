import os
import shutil
from pathlib import Path


def ensure_directories_exist(directories: list[str]) -> None:
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def copy_file(source: str, destination_folder: str) -> str:
    Path(destination_folder).mkdir(parents=True, exist_ok=True)
    filename = os.path.basename(source)
    destination = os.path.join(destination_folder, filename)
    shutil.copy2(source, destination)
    return destination


def get_candidate_name_from_path(file_path: str) -> str:
    filename = os.path.basename(file_path)
    name = os.path.splitext(filename)[0]
    name = name.replace("_", " ").replace("-", " ")
    return name.strip()
