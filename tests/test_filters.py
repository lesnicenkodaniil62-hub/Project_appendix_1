import re
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.filters import process_bank_search


@pytest.fixture
def sample_transactions() -> list[dict[str, Any]]:
    """Фикстура: общий набор тестовых транзакций."""
    return [
        {"description": "Payment for coffee"},
        {"description": "GROCERY STORE"},
        {"description": "Bank transfer"},
        {"description": "Price is $10.00"},
        {"id": 123, "amount": 500.0},  # Поле description отсутствует
        {"description": None},  # Поле description равно None
    ]


@pytest.mark.parametrize(
    "query, expected_len",
    [
        ("coffee", 1),  # Точное вхождение
        ("grocery", 1),  # Регистронезависимый поиск
        ("bank", 1),  # Поиск подстроки
        ("$10.00", 1),  # Спецсимволы regex экранируются re.escape
        ("nonexistent", 0),  # Совпадений нет
    ],
)
def test_parametrized_search(sample_transactions: list[dict[str, Any]], query: str, expected_len: int) -> None:
    """Параметризированный тест: проверяет разные сценарии поиска."""
    result = process_bank_search(sample_transactions, query)
    assert len(result) == expected_len


def test_empty_search_returns_original_object(sample_transactions: list[dict[str, Any]]) -> None:
    """Пустой запрос должен вернуть исходный список без изменений."""
    result = process_bank_search(sample_transactions, "")
    assert result is sample_transactions


def test_handles_missing_and_none_description(sample_transactions: list[dict[str, Any]]) -> None:
    """Транзакции без description или с None не должны вызывать ошибку."""
    result = process_bank_search(sample_transactions, "zzz_unique")
    assert len(result) == 0


def test_re_compile_called_with_escaped_pattern_and_flag() -> None:
    """
    Пример использования patch/Mock: проверяем, что re.compile вызывается
    с экранированной строкой и флагом re.IGNORECASE.
    """
    mock_pattern = MagicMock()
    mock_pattern.search.return_value = True

    # Патчим re.compile именно в пространстве имён модуля filters
    with patch("src.filters.re.compile", return_value=mock_pattern) as mock_compile:
        dummy_data: list[dict[str, Any]] = [{"description": "test"}]
        process_bank_search(dummy_data, "query$special")

        # Проверяем аргументы вызова re.compile
        mock_compile.assert_called_once_with("query\\$special", re.IGNORECASE)
