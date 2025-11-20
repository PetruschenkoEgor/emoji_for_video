import os
import subprocess
import uuid

from fastapi import UploadFile, HTTPException


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG_PATH = os.path.join(BASE_DIR, "bin", "ffmpeg.exe")

MAX_FILE_SIZE = 11 * 1024 * 1024


async def save_uploaded_file(file: UploadFile, temp_dir: str) -> tuple[str, str]:
    """Сохраняет загруженный файл и возвращает пути."""

    input_id = uuid.uuid4().hex
    input_filename = os.path.join(temp_dir, f"{input_id}_input.mp4")
    output_filename = os.path.join(temp_dir, f"{input_id}_output.mp4")

    try:
        content = await file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail='Загружаемый файл не может быть больше 11МБ'
            )

        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail='Загружаемый файл не может быть пустым'
            )

        with open(input_filename, 'wb') as f:
            f.write(content)

        return input_filename, output_filename

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Ошибка сохранения файла: {str(e)}'
        )


def build_ffmpeg_command(input_path: str, output_path: str, emoji_path: str) -> list[str]:
    """Создает команду для ffmpeg."""
    return [
        FFMPEG_PATH,
        "-i", input_path,
        "-i", emoji_path,
        "-filter_complex",
        "[1]scale=200:200,"
        "format=rgba,"
        "geq=lum='p(X,Y)':a='if(lt((X-100)^2+(Y-100)^2,10000),255,0)'[circle];"
        "[0][circle]overlay=(W-w)/2:(H-h)/2",
        "-c:a", "copy",
        "-y",
        output_path
    ]


def process_video_with_ffmpeg(ffmpeg_command: list[str], timeout: int = 30) -> None:
    """Запускает обработку видео через ffmpeg."""
    try:
        result = subprocess.run(
            ffmpeg_command,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail='Ошибка обработки видео')

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail='Таймаут обработки видео')

    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Неизвестная ошибка: {e}')


def cleanup_files(input_path: str, output_path: str) -> None:
    """Удаляет временные файлы после отправки ответа."""
    try:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
    except Exception as e:
        print(f"Ошибка очистки временных файлов: {e}")
