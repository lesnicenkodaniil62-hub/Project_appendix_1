import json
from pathlib import Path
from unittest.mock import patch

from src.utils import read_transactions


def test_read_transactions_success(tmp_path: Path) -> None:
    """Тест: успешное чтение валидного JSON-файла со списком транзакций."""
    # Подготовка тестовых данных
    expected_data = [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]
    file_path = tmp_path / "operations.json"
    file_path.write_text(json.dumps(expected_data), encoding="utf-8")

    # Вызов тестируемой функции
    result = read_transactions(str(file_path))

    # Проверка результата
    assert result == expected_data
    assert isinstance(result, list)


def test_read_transactions_file_not_found() -> None:
    """Тест: чтение несуществующего файла возвращает пустой список."""
    result = read_transactions("/non/existent/path.json")

    assert result == []
    assert isinstance(result, list)


def test_read_transactions_empty_file(tmp_path: Path) -> None:
    """Тест: чтение пустого JSON-файла возвращает пустой список."""
    file_path = tmp_path / "empty.json"
    file_path.write_text("", encoding="utf-8")

    result = read_transactions(str(file_path))

    assert result == []


def test_read_transactions_empty_list(tmp_path: Path) -> None:
    """Тест: чтение JSON с пустым списком возвращает пустой список."""
    file_path = tmp_path / "empty_list.json"
    file_path.write_text("[]", encoding="utf-8")

    result = read_transactions(str(file_path))

    assert result == []


def test_read_transactions_not_list(tmp_path: Path) -> None:
    """Тест: чтение JSON с объектом (не списком) возвращает пустой список."""
    file_path = tmp_path / "not_list.json"
    file_path.write_text('{"key": "value"}', encoding="utf-8")

    result = read_transactions(str(file_path))

    assert result == []


def test_read_transactions_invalid_json(tmp_path: Path) -> None:
    """Тест: чтение файла с невалидным JSON возвращает пустой список."""
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{invalid json content}", encoding="utf-8")

    result = read_transactions(str(file_path))

    assert result == []


def test_read_transactions_permission_error() -> None:
    """Тест: обработка ошибки доступа к файлу возвращает пустой список."""
    with patch("src.utils.Path.exists", return_value=True):
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            result = read_transactions("/protected/file.json")
            assert result == []
