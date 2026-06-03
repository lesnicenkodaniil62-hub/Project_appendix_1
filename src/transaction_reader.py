import csv
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd

FilePath = Union[str, Path]


def read_transactions_from_csv(file_path: FilePath) -> List[Dict[str, Any]]:
    """Считывает финансовые операции из CSV-файла."""
    transactions: List[Dict[str, Any]] = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            # Пропускаем полностью пустые строки (например, ";;;;;;;;")
            if any(value for value in row.values() if value):
                transactions.append(dict(row))
    return transactions


def read_transactions_from_excel(file_path: FilePath) -> List[Dict[str, Any]]:
    """Считывает финансовые операции из Excel-файла с обработкой ошибок зависимостей."""
    try:
        df = pd.read_excel(file_path)
    except ImportError as exc:
        raise ImportError(
            "Для чтения .xlsx файлов pandas требует пакет 'openpyxl'. " "Установите его: pip install openpyxl"
        ) from exc
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Файл не найден: {file_path}") from exc
    except Exception as exc:
        raise RuntimeError(f"Ошибка при чтении файла {file_path}: {exc}") from exc

    # Замена pandas NA/NaN на Python None для единообразия типов
    df_clean = df.where(df.notna(), None)
    # to_dict возвращает List[Dict], но pandas stubs иногда требуют игнорирования
    records: List[Dict[str, Any]] = df_clean.to_dict(orient="records")  # type: ignore[assignment]

    # Фильтрация строк, где все значения стали None
    return [row for row in records if any(v is not None for v in row.values())]
