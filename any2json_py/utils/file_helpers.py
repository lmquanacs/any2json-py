from pathlib import Path
from any2json_py.config import get_settings
from any2json_py.exceptions import FileTooLargeError, UnsupportedFormatError

SUPPORTED_FORMATS = {".csv", ".yaml", ".yml", ".xml", ".pdf", ".png", ".jpg", ".jpeg", ".docx", ".txt"}


def validate_file(path: Path) -> None:
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(f"Unsupported format: {path.suffix}")
    settings = get_settings()
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise FileTooLargeError(f"File is {size_mb:.1f} MB, limit is {settings.max_file_size_mb} MB")
