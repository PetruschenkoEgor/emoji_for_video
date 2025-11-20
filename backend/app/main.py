import os

from fastapi import FastAPI, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from backend.app.utils import save_uploaded_file, build_ffmpeg_command, process_video_with_ffmpeg, cleanup_files
from backend.app.validators import validate_file, validate_dependencies, verify_output_file

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "temp_videos")
EMOJI_PATH = os.path.join(BASE_DIR, "emoji", "smiley.png")

# Создаем папку для временных файлов
os.makedirs(TEMP_DIR, exist_ok=True)


@app.post("/api/add-emoji", response_class=FileResponse)
async def add_emoji(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Основной эндпоинт для добавления эмодзи в видео."""

    # Валидация
    validate_file(file)
    validate_dependencies()

    # Сохраняем файл
    input_filename, output_filename = await save_uploaded_file(file, TEMP_DIR)

    try:
        # Подготовка и выполнение команды ffmpeg
        ffmpeg_command = build_ffmpeg_command(input_filename, output_filename, EMOJI_PATH)
        process_video_with_ffmpeg(ffmpeg_command)

        # Проверка результата
        verify_output_file(output_filename)

        # Отправка файла и планирование очистки
        background_tasks.add_task(cleanup_files, input_filename, output_filename)
        return FileResponse(
            output_filename,
            media_type='video/mp4',
            filename=f"emoji_{file.filename}"
        )

    except Exception as e:
        # В случае ошибки сразу очищаем файлы
        background_tasks.add_task(cleanup_files, input_filename, output_filename)
        raise HTTPException(status_code=500, detail=f"Ошибка: {e}")
