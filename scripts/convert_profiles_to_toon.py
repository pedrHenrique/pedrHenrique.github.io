"""Converte os perfis JSON para TOON em um ambiente Python isolado."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT_FOLDER = Path(__file__).resolve().parent.parent
VENV_FOLDER = Path(__file__).resolve().parent / ".venv"
PROFILE_FILES = ("profile-en.json", "profile-pt-BR.json")
PACKAGE_URL = "git+https://github.com/toon-format/toon-python.git"


def venv_python() -> Path:
    executable = "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    return VENV_FOLDER / executable


def ensure_venv() -> None:
    if not venv_python().exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_FOLDER)])


def ensure_toon_python() -> None:
    if importlib.util.find_spec("toon_format") is None:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", PACKAGE_URL]
        )


def main() -> None:
    ensure_venv()

    if Path(sys.prefix).resolve() != VENV_FOLDER.resolve():
        subprocess.check_call([str(venv_python()), str(Path(__file__).resolve())])
        return

    ensure_toon_python()
    from toon_format import encode

    for filename in PROFILE_FILES:
        source = ROOT_FOLDER / "public" / filename
        destination = source.with_suffix(".toon")

        with source.open(encoding="utf-8") as file:
            data = json.load(file)

        destination.write_text(encode(data) + "\n", encoding="utf-8")
        print(f"Convertido: {destination.relative_to(ROOT_FOLDER)}")


if __name__ == "__main__":
    main()
