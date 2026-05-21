import pytest
from typing import List, Dict, Any
from unittest.mock import patch, mock_open

import pandas as pd

from src.transaction_reader import read_transactions_from_csv, read_transactions_from_excel


def test_read_transactions_from_csv() -> None:
    """
    Тест успешного чтения CSV-файла с использованием Mock и patch.
    Цель: убедиться, что функция корректно инициализирует DictReader,
    фильтрует пустые строки и возвращает список словарей без потерь данных.
    """
    # 1. Подготовка эталонных данных (контракт функции)
    # Имитируем результат работы csv.DictReader после парсинга реального CSV
    expected: List[Dict[str, Any]] = [
        {
            "id": "1", "state": "EXECUTED", "date": "2023-01-01T10:00:00Z",
            "amount": "100", "currency_name": "USD", "currency_code": "USD",
            "from": "", "to": "", "description": "Тестовый перевод"
        },
        {
            "id": "2", "state": "CANCELED", "date": "2023-01-02T12:00:00Z",
            "amount": "200", "currency_name": "EUR", "currency_code": "EUR",
            "from": "", "to": "", "description": "Отмена операции"
        }
    ]

    # 2. Изоляция файлового ввода-вывода
    # patch подменяет встроенную open() на mock_open(). 
    # create=True требуется, так как open не является атрибутом модуля src, а встроенной функцией.
    with patch("src.transaction_reader.open", mock_open(), create=True):
        # 3. Изоляция CSV-парсера
        # DictReader заменяется на заглушку, которая при итерации отдаёт наш expected
        with patch("src.transaction_reader.csv.DictReader") as mock_dict_reader:
            mock_dict_reader.return_value = expected

            # 4. Вызов тестируемой функции
            result = read_transactions_from_csv("test.csv")

            # 5. Проверки (Assertions)
            # Проверяем, что бизнес-логика не исказила данные
            assert result == expected, "Функция вернула неверный список транзакций"
            # Проверяем, что парсер был вызван ровно один раз (отсутствие лишних циклов)
            mock_dict_reader.assert_called_once()


def test_read_transactions_from_excel() -> None:
    """
    Тест успешного чтения Excel-файла с использованием Mock и patch.
    Цель: проверить цепочку pd.read_excel → замена NaN на None → конвертация в dict → фильтрация.
    """
    # 1. Подготовка эталонных данных
    expected: List[Dict[str, Any]] = [
        {
            "id": "1", "state": "EXECUTED", "date": "2023-01-01T10:00:00Z",
            "amount": "100", "currency_name": "USD", "currency_code": "USD",
            "from": "", "to": "", "description": "Тестовый перевод"
        },
        {
            "id": "2", "state": "CANCELED", "date": "2023-01-02T12:00:00Z",
            "amount": "200", "currency_name": "EUR", "currency_code": "EUR",
            "from": "", "to": "", "description": "Отмена операции"
        }
    ]

    # Создаём pandas DataFrame из тестовых данных. Он будет имитировать результат чтения .xlsx
    mock_df = pd.DataFrame(expected)

    # 2. Изоляция чтения файла
    # pd.read_excel подменяется заглушкой, возвращающей готовый DataFrame.
    # Реальный .xlsx и библиотека openpyxl не задействуются.
    with patch("src.transaction_reader.pd.read_excel", return_value=mock_df) as mock_read_excel:
        # 3. Вызов тестируемой функции
        result = read_transactions_from_excel("test.xlsx")

        # 4. Проверки
        assert result == expected, "DataFrame некорректно преобразован в список словарей"
        # Убеждаемся, что pd.read_excel был вызван с правильным путём и ровно 1 раз
        mock_read_excel.assert_called_once_with("test.xlsx")


def test_read_transactions_from_excel_import_error() -> None:
    """
    Тест обработки отсутствующей зависимости openpyxl.
    Цель: проверить, что сырое ImportError от pandas перехватывается и
    переопределяется в понятное пользователю сообщение с инструкцией по установке.
    """
    # side_effect заставляет mock вызвать исключение вместо возврата значения
    with patch("src.transaction_reader.pd.read_excel", side_effect=ImportError("No module named 'openpyxl'")):
        # pytest.raises ловит исключение и проверяет его тип и сообщение
        with pytest.raises(ImportError, match="Для чтения .xlsx файлов pandas требует пакет 'openpyxl'"):
            read_transactions_from_excel("test.xlsx")


def test_read_transactions_from_excel_file_not_found() -> None:
    """
    Тест обработки отсутствующего файла на диске.
    Цель: убедиться, что FileNotFoundError не проглатывается, а пробрасывается
    с уточняющим сообщением о пути к файлу.
    """
    with patch("src.transaction_reader.pd.read_excel", side_effect=FileNotFoundError("test.xlsx")):
        with pytest.raises(FileNotFoundError, match="Файл не найден"):
            read_transactions_from_excel("test.xlsx")


def test_read_transactions_from_excel_runtime_error() -> None:
    """
    Тест обработки непредвиденных ошибок парсинга (повреждённый файл, битые структуры).
    Цель: проверить, что любые другие исключения оборачиваются в RuntimeError,
    сохраняя исходную причину для логирования.
    """
    with patch("src.transaction_reader.pd.read_excel", side_effect=ValueError("Corrupted Excel structure")):
        with pytest.raises(RuntimeError, match="Ошибка при чтении файла"):
            read_transactions_from_excel("test.xlsx")