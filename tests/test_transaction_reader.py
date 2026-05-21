from typing import Any, Dict, List
from unittest.mock import mock_open, patch

import pandas as pd

from src.transaction_reader import read_transactions_from_csv, read_transactions_from_excel


def test_read_transactions_from_csv() -> None:
    """
    Тест функции read_transactions_from_csv с использованием Mock и patch.

    Цель: убедиться, что функция корректно парсит CSV, фильтрует пустые строки
    и возвращает список словарей с транзакциями.

    Стратегия:
    - Файловая система и парсер CSV изолируются через Mock и patch.
    - Тест работает быстро, детерминированно и не зависит от реальных файлов.
    - Проверяется как возвращаемое значение, так и корректность вызовов зависимостей.
    """
    # 1. Ожидаемый результат (контракт функции)
    expected: List[Dict[str, Any]] = [
        {
            "id": "1",
            "state": "EXECUTED",
            "date": "2023-01-01T10:00:00Z",
            "amount": "100",
            "currency_name": "USD",
            "currency_code": "USD",
            "from": "",
            "to": "",
            "description": "Тестовый перевод",
        },
        {
            "id": "2",
            "state": "CANCELED",
            "date": "2023-01-02T12:00:00Z",
            "amount": "200",
            "currency_name": "EUR",
            "currency_code": "EUR",
            "from": "",
            "to": "",
            "description": "Отмена операции",
        },
    ]

    # 2. Изоляция внешнего ввода-вывода и парсера
    # patch подменяет встроенную open на mock_open(), имитирующий работу с файлом
    with patch("src.transaction_reader.open", mock_open()) as mock_file:
        # patch подменяет csv.DictReader, возвращая заранее подготовленные данные
        with patch("src.transaction_reader.csv.DictReader") as mock_dict_reader:
            mock_dict_reader.return_value = expected

            # 3. Вызов тестируемой функции
            result = read_transactions_from_csv("test.csv")

            # 4. Проверки (Assertions)
            # Проверяем, что функция вернула именно те данные, которые мы "скормили" парсеру
            assert result == expected

            # Проверяем, что DictReader был вызван ровно один раз
            mock_dict_reader.assert_called_once()

            # Проверяем, что open был вызван с правильным путём, режимом и кодировкой
            mock_file.assert_called_once_with("test.csv", "r", encoding="utf-8")


def test_read_transactions_from_excel() -> None:
    """
    Тест функции read_transactions_from_excel с использованием Mock и patch.

    Цель: убедиться, что функция корректно читает Excel через pandas,
    преобразует NA/NaN в None, фильтрует пустые строки и возвращает список словарей.

    Стратегия:
    - Реальный парсинг .xlsx отключается через patch pd.read_excel.
    - Возвращается mock DataFrame, содержащий тестовые данные.
    - Проверяется конвертация данных и корректность вызова pandas.
    """
    # 1. Ожидаемый результат (контракт функции)
    expected: List[Dict[str, Any]] = [
        {
            "id": "1",
            "state": "EXECUTED",
            "date": "2023-01-01T10:00:00Z",
            "amount": "100",
            "currency_name": "USD",
            "currency_code": "USD",
            "from": "",
            "to": "",
            "description": "Тестовый перевод",
        },
        {
            "id": "2",
            "state": "CANCELED",
            "date": "2023-01-02T12:00:00Z",
            "amount": "200",
            "currency_name": "EUR",
            "currency_code": "EUR",
            "from": "",
            "to": "",
            "description": "Отмена операции",
        },
    ]

    # Создаём pandas DataFrame из ожидаемых данных.
    # Функция внутри преобразует его обратно в список словарей.
    mock_df = pd.DataFrame(expected)

    # 2. Изоляция чтения файла
    # pd.read_excel заменяется на заглушку, которая сразу возвращает mock_df
    with patch("src.transaction_reader.pd.read_excel", return_value=mock_df) as mock_read_excel:
        # 3. Вызов тестируемой функции
        result = read_transactions_from_excel("test.xlsx")

        # 4. Проверки (Assertions)
        assert result == expected

        # Убеждаемся, что pd.read_excel был вызван ровно один раз с правильным путём
        mock_read_excel.assert_called_once_with("test.xlsx")
