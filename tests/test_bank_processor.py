from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.bank_processor import process_bank_operations


@pytest.fixture
def sample_data() -> list[dict[str, Any]]:
    """Фикстура: набор транзакций с валидными, отсутствующими и None значениями description."""
    return [
        {"description": "Food"},
        {"description": "Transport"},
        {"description": "Food"},
        {"description": "Entertainment"},
        {"amount": 100.0},  # Поле description отсутствует
        {"description": None},  # Поле description равно None
    ]


@pytest.fixture
def full_categories() -> list[str]:
    """Фикстура: стандартный список категорий."""
    return ["Food", "Transport", "Utilities"]


@pytest.mark.parametrize(
    "cats, expected",
    [
        pytest.param(["Food", "Transport"], {"Food": 2, "Transport": 1}, id="multiple_present"),
        pytest.param(["Utilities"], {"Utilities": 0}, id="absent_category"),
        pytest.param(["Food"], {"Food": 2}, id="single_category"),
        pytest.param(["Food", "Utilities"], {"Food": 2, "Utilities": 0}, id="mixed"),
    ],
)
def test_counts_correctly(sample_data: list[dict[str, Any]], cats: list[str], expected: dict[str, int]) -> None:
    """Параметризированный тест: проверяет корректность подсчёта для разных наборов категорий."""
    result: dict[str, int] = process_bank_operations(sample_data, cats)
    assert result == expected


def test_order_preserved() -> None:
    """Порядок ключей в результате должен строго совпадать с порядком переданных категорий."""
    data: list[dict[str, Any]] = [{"description": "B"}, {"description": "A"}]
    cats: list[str] = ["C", "A", "B"]
    result: dict[str, int] = process_bank_operations(data, cats)
    assert list(result.keys()) == cats


def test_empty_inputs() -> None:
    """Пустые списки на входе должны вернуть пустой словарь."""
    result: dict[str, int] = process_bank_operations([], [])
    assert result == {}


def test_handles_missing_description_key() -> None:
    """Отсутствие ключа description не вызывает ошибку (dict.get вернёт None)."""
    data: list[dict[str, Any]] = [{"amount": 50}, {"description": "Food"}]
    cats: list[str] = ["Food"]
    result: dict[str, int] = process_bank_operations(data, cats)
    assert result == {"Food": 1}


def test_counter_instantiation_is_mocked() -> None:
    """
    Демонстрация patch/Mock: проверяем, что Counter инициализируется ровно один раз
    и получает итерируемый аргумент (генератор).
    """
    mock_counter_instance: MagicMock = MagicMock()
    # Настраиваем поведение __getitem__: вернёт 1 для "Test", 0 для остальных
    mock_counter_instance.__getitem__.side_effect = lambda key: 1 if key == "Test" else 0

    # Патчим Counter именно в пространстве имён bank_processor
    with patch("src.bank_processor.Counter", return_value=mock_counter_instance) as mock_cls:
        data: list[dict[str, Any]] = [{"description": "Test"}]
        cats: list[str] = ["Test"]

        process_bank_operations(data, cats)

        mock_cls.assert_called_once()
        # Проверяем, что был передан ровно один позиционный аргумент
        call_args: tuple[Any, ...] = mock_cls.call_args[0] if mock_cls.call_args else ()
        assert len(call_args) == 1
        # Убедимся, что аргумент является итерируемым объектом (генератором/итератором)
        assert hasattr(call_args[0], "__iter__") or hasattr(call_args[0], "__next__")
