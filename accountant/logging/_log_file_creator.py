from datetime import datetime
from pathlib import Path


def create_log_file(folder: Path):
    def _create_folder(folder: Path):
        if not folder.exists():
            folder.mkdir(parents=True)

    file_name = f"accountant_{datetime.now().strftime('%d-%b-%Y')}.log"
    _create_folder(folder)
    path = folder / file_name
    if not path.exists():
        path.touch()

    return path
