import json
import logging
from pathlib import Path
from typing import Any, Dict, List

# 1. Создание логгера
utils_logger: logging.Logger = logging.getLogger("utils")
# УРОВЕНЬ ЛОГГЕРА: принимаем сообщения от DEBUG и выше
utils_logger.setLevel(logging.DEBUG)

# Настройка путей
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
LOGS_DIR: Path = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 2. Handler с перезаписью файла (mode="w")
utils_file_handler: logging.FileHandler = logging.FileHandler(LOGS_DIR / "utils.log", mode="w", encoding="utf-8")
utils_file_handler.setLevel(logging.DEBUG)

# 3. Formatter: время | модуль | УРОВЕНЬ | сообщение
utils_formatter: logging.Formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
utils_file_handler.setFormatter(utils_formatter)
utils_logger.addHandler(utils_file_handler)


def read_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Читает JSON-файл с данными о финансовых транзакциях."""
    path: Path = Path(file_path)

    # DEBUG: детальная отладка (попадёт в лог, т.к. порог >= DEBUG)
    utils_logger.debug("Начало чтения файла: %s", file_path)

    if not path.exists():
        # ERROR: критичная ошибка, блокирующая работу (уровень >= ERROR)
        utils_logger.error("Файл не найден: %s", file_path)
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data: Any = json.load(file)
    except (json.JSONDecodeError, IOError, OSError, PermissionError) as exc:
        # ERROR: ошибка чтения или парсинга
        utils_logger.error("Ошибка при обработке файла %s: %s", file_path, exc)
        return []

    if not isinstance(data, list):
        # ERROR: неверная структура данных
        utils_logger.error("Неверный формат данных в файле %s (ожидается список)", file_path)
        return []

    # INFO: успешное выполнение основной операции
    transactions: List[Dict[str, Any]] = data
    utils_logger.info("Успешно загружено %d транзакций из %s", len(transactions), file_path)
    return transactions
