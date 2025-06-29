import sys
import os
from pathlib import Path

from loguru import logger

# Убедимся, что папка для логов существует
LOG_DIR = Path("/app/logs")
LOG_DIR.mkdir(exist_ok=True, parents=True)


logger.add(
    sys.stderr,  # Вывод в консоль
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    backtrace=True,
    diagnose=True
)

# Файловый лог (ротация по размеру/времени)
logger.add(
    LOG_DIR / "app.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level="DEBUG",
    enqueue=True,  # Асинхронная запись (важно для FastAPI!)
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)