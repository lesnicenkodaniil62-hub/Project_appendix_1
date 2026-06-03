import os
from datetime import datetime
from typing import Any, Dict

import requests

# Токен доступа к API, берётся из переменных окружения
API_TOKEN: str = os.getenv("API_LAYER_TOKEN", "API_TOKEN")

# Базовый URL для запросов к API конвертации
BASE_URL: str = "https://api.apilayer.com/exchangerates_data/convert"


def convert_to_rubles(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    Если валюта транзакции — USD или EUR, выполняется запрос к внешнему API
    для получения курса и конвертации. Для RUB и неизвестных валют
    возвращается исходная сумма без изменений.

    Аргументы:
        transaction: Словарь с данными транзакции, содержащий operationAmount.

    Возвращает:
        Сумма в рублях в виде float.
    """
    # Извлекаем информацию о сумме и валюте из транзакции
    operation_amount: Dict[str, Any] = transaction.get("operationAmount", {})
    if not operation_amount:
        return 0.0

    # Получаем строковое значение суммы и код валюты
    amount_str: str = operation_amount.get("amount", "0")
    currency_info: Dict[str, str] = operation_amount.get("currency", {})
    currency_code: str = currency_info.get("code", "RUB")

    # Преобразуем сумму в число с плавающей точкой
    try:
        amount: float = float(amount_str)
    except (ValueError, TypeError):
        return 0.0

    # Если валюта уже рубли — конвертация не требуется
    if currency_code == "RUB":
        return amount

    # Для USD и EUR выполняем запрос к внешнему API
    if currency_code in ("USD", "EUR"):
        # Извлекаем дату транзакции для исторического курса
        date_str: str = _extract_date(transaction.get("date", ""))
        return _fetch_converted_amount(amount, currency_code, date_str)

    # Для неизвестных валют возвращаем исходную сумму
    return amount


def _extract_date(iso_date: str) -> str:
    """
    Извлекает дату в формате ГГГГ-ММ-ДД из ISO-строки даты и времени.

    Аргументы:
        iso_date: Строка даты и времени в формате ISO 8601.

    Возвращает:
        Строка даты в формате ГГГГ-ММ-ДД, или дата по умолчанию при ошибке.
    """
    # Если дата не передана — используем значение по умолчанию
    if not iso_date:
        return "2026-01-01"

    try:
        # Убираем суффикс часового пояса для совместимости с fromisoformat
        clean_date = iso_date.replace("Z", "+00:00")
        # Парсим строку в объект datetime
        dt_object: datetime = datetime.fromisoformat(clean_date)
        # Форматируем дату в нужный вид
        return dt_object.strftime("%Y-%m-%d")
    except ValueError:
        # При ошибке парсинга возвращаем дату по умолчанию
        return "2026-01-01"


def _fetch_converted_amount(amount: float, from_currency: str, date: str) -> float:
    """
    Запрашивает конвертированную сумму через внешний API.

    Аргументы:
        amount: Сумма для конвертации.
        from_currency: Код исходной валюты (USD или EUR).
        date: Дата для получения исторического курса в формате ГГГГ-ММ-ДД.

    Возвращает:
        Конвертированная сумма в рублях, или исходная сумма при ошибке.
    """
    # Формируем URL запроса с параметрами
    url: str = f"{BASE_URL}?to=RUB&from={from_currency}" f"&amount={amount}&date={date}"
    # Используем встроенный dict и разрешаем bytes, что точно соответствует сигнатуре requests
    headers: dict[str, str | bytes] = {"apikey": API_TOKEN}

    try:
        # Выполняем GET-запрос с тайм-аутом 10 секунд
        response = requests.get(url, headers=headers, timeout=10)
        # Вызываем исключение при ошибке статуса ответа
        response.raise_for_status()
        # Парсим ответ как JSON
        result: dict[str, Any] = response.json()
        # Извлекаем конвертированное значение
        converted: float = float(result.get("result", amount))
        return converted
    except (requests.RequestException, ValueError, KeyError, TypeError):
        # При любой ошибке возвращаем исходную сумму как запасной вариант
        return amount
