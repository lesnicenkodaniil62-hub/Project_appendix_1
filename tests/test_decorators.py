import os
from typing import Any, Generator

import pytest

from src.decorators import log


@pytest.fixture
def temp_log_file() -> Generator[str, None, None]:
    """Фикстура для создания временного файла логов."""
    filename: str = "temp_test_log.txt"
    yield filename
    if os.path.exists(filename):
        os.remove(filename)


def test_successful_execution_with_filename(temp_log_file: str) -> None:
    """Тест успешного выполнения функции с указанием файла логов."""

    @log(filename=temp_log_file)
    def add(a: int, b: int) -> int:
        return a + b

    add(1, 2)

    with open(temp_log_file, "r", encoding="utf-8") as f:
        content: str = f.read()

    assert "add ok" in content


def test_successful_execution_without_filename(capsys: Any) -> None:
    """Тест успешного выполнения функции без указания файла (вывод в консоль)."""

    @log()
    def multiply(a: int, b: int) -> int:
        return a * b

    multiply(3, 4)

    captured: Any = capsys.readouterr()
    assert "multiply ok" in captured.out


def test_error_execution_with_filename(temp_log_file: str) -> None:
    """Тест выполнения функции с ошибкой и указанием файла логов."""

    @log(filename=temp_log_file)
    def divide(a: float, b: float) -> float:
        return a / b

    with pytest.raises(ZeroDivisionError):
        divide(1, 0)

    with open(temp_log_file, "r", encoding="utf-8") as f:
        content: str = f.read()

    assert "divide error: ZeroDivisionError" in content
    assert "Inputs: (1, 0), {}" in content


def test_error_execution_without_filename(capsys: Any) -> None:
    """Тест выполнения функции с ошибкой без указания файла (вывод в консоль)."""

    @log()
    def problematic_function() -> None:
        raise ValueError("Something went wrong")

    with pytest.raises(ValueError):
        problematic_function()

    captured: Any = capsys.readouterr()
    assert "problematic_function error: ValueError" in captured.out
    assert "Inputs: (), {}" in captured.out


def test_function_with_kwargs(temp_log_file: str) -> None:
    """Тест функции с именованными аргументами."""

    @log(filename=temp_log_file)
    def greet(name: str, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}!"

    greet("Alice", greeting="Hi")

    with open(temp_log_file, "r", encoding="utf-8") as f:
        content: str = f.read()

    assert "greet ok" in content


def test_function_returning_none(temp_log_file: str) -> None:
    """Тест функции, возвращающей None."""

    @log(filename=temp_log_file)
    def do_nothing() -> None:
        pass

    do_nothing()

    with open(temp_log_file, "r", encoding="utf-8") as f:
        content: str = f.read()

    assert "do_nothing ok" in content
