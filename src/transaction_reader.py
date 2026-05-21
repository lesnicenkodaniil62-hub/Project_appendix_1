import csv
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd

FilePath = Union[str, Path]


def read_transactions_from_csv(file_path: FilePath) -> List[Dict[str, Any]]:
    """Считывает финансовые операции из CSV-файла.
    Возвращает список словарей с транзакциями."""
    transactions: List[Dict[str, Any]] = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            # Пропускаем полностью пустые строки (например, ";;;;;;;;")
            if any(value for value in row.values() if value):
                transactions.append(dict(row))
    return transactions


def read_transactions_from_excel(file_path: FilePath) -> List[Dict[str, Any]]:
    """Считывает финансовые операции из Excel-файла.
    Возвращает список словарей с транзакциями."""
    df = pd.read_excel(file_path)
    # Заменяем pandas NA/NaN на Python None для единообразия типов
    df_clean = df.where(df.notna(), None)
    records: List[Dict[str, Any]] = df_clean.to_dict(orient="records")

    # Фильтрация строк, где все значения стали None
    return [row for row in records if any(v is not None for v in row.values())]
