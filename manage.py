#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def _project_venv_python() -> Path:
    base_dir = Path(__file__).resolve().parent
    if os.name == "nt":
        return base_dir / ".venv" / "Scripts" / "python.exe"
    return base_dir / ".venv" / "bin" / "python"


def _maybe_reexec_in_project_venv() -> None:
    current_python = Path(sys.executable).resolve()
    venv_python = _project_venv_python()
    if os.environ.get("DJANGO_MANAGEPY_VENV_REEXEC") == "1":
        return
    if not venv_python.exists():
        return
    if current_python == venv_python.resolve():
        return

    os.environ["DJANGO_MANAGEPY_VENV_REEXEC"] = "1"
    os.execv(str(venv_python), [str(venv_python), *sys.argv])


def main():
    """Run administrative tasks."""
    _maybe_reexec_in_project_venv()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
