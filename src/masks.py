import logging
from pathlib import Path

# 1. Создание отдельного логгера для модуля masks
masks_logger: logging.Logger = logging.getLogger("masks")
# Порог срабатывания: DEBUG и выше
masks_logger.setLevel(logging.DEBUG)

# Определение путей к папке logs в корне проекта
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
LOGS_DIR: Path = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 2. FileHandler с перезаписью файла (mode="w")
masks_file_handler: logging.FileHandler = logging.FileHandler(LOGS_DIR / "masks.log", mode="w", encoding="utf-8")
masks_file_handler.setLevel(logging.DEBUG)

# 3. Formatter: время | модуль | УРОВЕНЬ | сообщение
masks_formatter: logging.Formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
masks_file_handler.setFormatter(masks_formatter)
masks_logger.addHandler(masks_file_handler)


def get_mask_card_number(card_number: str) -> str:
    """Маскирует номер банковской карты (ровно 16 цифр)."""
    # DEBUG: отладочная информация о входе в функцию
    masks_logger.debug("Получен номер карты для обработки: %s", card_number)

    if not card_number or not card_number.isdigit() or len(card_number) != 16:
        # ERROR: некорректные входные данные
        masks_logger.error("Некорректный номер карты: %s", card_number)
        return "Некорректный номер карты"

    # Формат: XXXX XX** **** XXXX (пробел только после первых 4 цифр)
    result: str = f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"

    # 🟢 INFO: успешное выполнение
    masks_logger.info("Карта успешно замаскирована: %s", result)
    return result


def get_mask_account(account: str) -> str:
    """Маскирует номер банковского счета."""
    # DEBUG: отладочная информация о входе в функцию
    masks_logger.debug("Получен номер счета для обработки: %s", account)

    if not account.isdigit() or len(account) < 4:
        # ERROR: некорректные входные данные
        masks_logger.error("Некорректный номер счета: %s", account)
        return "Некорректный номер счета"

    result: str = f"**{account[-4:]}"

    # INFO: успешное выполнение
    masks_logger.info("Счет успешно замаскирован: %s", result)
    return result
