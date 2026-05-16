import json
from pathlib import Path
from typing import Any, Dict, List


def read_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает JSON-файл с данными о финансовых транзакциях.

    Аргументы:
        file_path: Путь к JSON-файлу.

    Возвращает:
        Список словарей с данными транзакций,
        или пустой список, если файл пустой, не содержит список или не найден.
    """
    try:
        # Создаём объект пути для работы с файловой системой
        path = Path(file_path)

        # Если файл не существует — возвращаем пустой список
        if not path.exists():
            return []

        # Открываем и читаем файл с кодировкой UTF-8
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Проверяем, что данные являются списком
        if not isinstance(data, list):
            return []

        return data
    except (json.JSONDecodeError, IOError, OSError, PermissionError):
        # При любой ошибке чтения или парсинга возвращаем пустой список
        return []
