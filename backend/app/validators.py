import os

from fastapi import UploadFile, HTTPException


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG_PATH = os.path.join(BASE_DIR, "bin", "ffmpeg.exe")
EMOJI_PATH = os.path.join(BASE_DIR, "emoji", "smiley.png")


def validate_file(file: UploadFile) -> None:
    """Проверяет валидность загружаемого файла."""
    extensions = ('.mp4', '.mov', '.avi')
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in extensions:
        raise HTTPException(
            status_code=400,
            detail="Загружать можно только видеофайлы форматов .mp4, .mov, .avi"
        )


def validate_dependencies() -> None:
    """Проверяет наличие необходимых зависимостей."""
    if not os.path.exists(EMOJI_PATH):
        raise HTTPException(status_code=500, detail="Эмодзи не найден")

    if not os.path.exists(FFMPEG_PATH):
        raise HTTPException(
            status_code=500,
            detail=f"FFmpeg не найден по пути: {FFMPEG_PATH}"
        )


def verify_output_file(output_path: str) -> None:
    """Проверяет что выходной файл был создан."""
    if not os.path.exists(output_path):
        raise HTTPException(
            status_code=500,
            detail='Выходной файл не был создан'
        )
