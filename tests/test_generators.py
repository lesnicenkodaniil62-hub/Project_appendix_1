from typing import Any, Dict, Generator, Iterator, List

import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions

# ====== ФИКСТУРЫ ======


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фикстура с образцом транзакций для тестирования."""
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702",
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {"amount": "79114.93", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188",
        },
        {
            "id": 873106923,
            "state": "EXECUTED",
            "date": "2019-03-23T01:09:46.296404",
            "operationAmount": {"amount": "43318.34", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 44812258784861134719",
            "to": "Счет 74489636417521191160",
        },
        {
            "id": 895315941,
            "state": "EXECUTED",
            "date": "2018-08-19T04:27:37.904916",
            "operationAmount": {"amount": "56883.54", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод с карты на карту",
            "from": "Visa Classic 6831982476737658",
            "to": "Visa Platinum 8990922113665229",
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
            "operationAmount": {"amount": "67314.70", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Перевод организации",
            "from": "Visa Platinum 1246377376343588",
            "to": "Счет 14211924144426031657",
        },
    ]


@pytest.fixture
def empty_transactions() -> List[Dict[str, Any]]:
    """Фикстура с пустым списком транзакций."""
    return []


@pytest.fixture
def invalid_transactions() -> List[Dict[str, Any]]:
    """Фикстура с транзакциями, имеющими некорректную структуру."""
    return [
        {"id": 1, "wrong_key": "test"},  # Нет operationAmount
        {"id": 2, "operationAmount": {"amount": "100"}},  # Нет currency
        {"id": 3, "operationAmount": {"currency": {"code": 123}}},  # code не строка
        {"id": 4, "operationAmount": "not a dict"},  # operationAmount не словарь
        {"id": 5},  # Пустой словарь
    ]


@pytest.fixture
def mixed_transactions() -> List[Dict[str, Any]]:
    """Фикстура со смешанными корректными и некорректными транзакциями."""
    return [
        {"description": "Корректная транзакция 1"},
        {"wrong_field": "Некорректная"},
        {"description": "Корректная транзакция 2"},
        {},
        {"description": "Корректная транзакция 3"},
    ]


# ====== ТЕСТЫ ДЛЯ filter_by_currency ======


def test_filter_by_currency_usd(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест фильтрации транзакций по валюте USD."""
    result: List[Dict[str, Any]] = list(filter_by_currency(sample_transactions, "USD"))
    result_ids: List[int] = [t["id"] for t in result]

    assert len(result) == 3
    assert result_ids == [939719570, 142264268, 895315941]

    # Проверяем, что все отфильтрованные транзакции имеют валюту USD
    for transaction in result:
        assert transaction["operationAmount"]["currency"]["code"] == "USD"


def test_filter_by_currency_rub(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест фильтрации транзакций по валюте RUB."""
    result: List[Dict[str, Any]] = list(filter_by_currency(sample_transactions, "RUB"))
    result_ids: List[int] = [t["id"] for t in result]

    assert len(result) == 2
    assert result_ids == [873106923, 594226727]

    for transaction in result:
        assert transaction["operationAmount"]["currency"]["code"] == "RUB"


def test_filter_by_currency_not_found(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест фильтрации по валюте, отсутствующей в транзакциях."""
    result: List[Dict[str, Any]] = list(filter_by_currency(sample_transactions, "EUR"))
    assert result == []
    assert len(result) == 0


def test_filter_by_currency_empty_list(empty_transactions: List[Dict[str, Any]]) -> None:
    """Тест фильтрации пустого списка транзакций."""
    result: List[Dict[str, Any]] = list(filter_by_currency(empty_transactions, "USD"))
    assert result == []
    assert len(result) == 0


def test_filter_by_currency_generator_property(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест проверки свойств генератора."""
    generator: Iterator[Dict[str, Any]] = filter_by_currency(sample_transactions, "USD")

    # Проверяем, что это генератор
    assert hasattr(generator, "__iter__")
    assert hasattr(generator, "__next__")

    # Проверяем ленивую загрузку
    first_item: Dict[str, Any] = next(generator)
    assert first_item["id"] == 939719570

    second_item: Dict[str, Any] = next(generator)
    assert second_item["id"] == 142264268


def test_filter_by_currency_invalid_structure(invalid_transactions: List[Dict[str, Any]]) -> None:
    """Тест обработки транзакций с некорректной структурой."""
    # Функция не должна выбрасывать исключение, просто пропускать некорректные
    result: List[Dict[str, Any]] = list(filter_by_currency(invalid_transactions, "USD"))
    assert result == []  # Все транзакции некорректны


# ====== ТЕСТЫ ДЛЯ transaction_descriptions ======


def test_transaction_descriptions_normal(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест получения описаний для обычных транзакций."""
    result: List[str] = list(transaction_descriptions(sample_transactions))
    expected: List[str] = [
        "Перевод организации",
        "Перевод со счета на счет",
        "Перевод со счета на счет",
        "Перевод с карты на карту",
        "Перевод организации",
    ]
    assert result == expected
    assert len(result) == 5


def test_transaction_descriptions_empty(empty_transactions: List[Dict[str, Any]]) -> None:
    """Тест получения описаний из пустого списка."""
    result: List[str] = list(transaction_descriptions(empty_transactions))
    assert result == []
    assert len(result) == 0


def test_transaction_descriptions_single_transaction() -> None:
    """Тест получения описания из одной транзакции."""
    single_transaction: List[Dict[str, Any]] = [{"description": "Тестовый перевод"}]
    result: List[str] = list(transaction_descriptions(single_transaction))
    assert result == ["Тестовый перевод"]


def test_transaction_descriptions_missing_description() -> None:
    """Тест получения описания из транзакции без ключа описание."""
    transactions: List[Dict[str, Any]] = [{"id": 1}, {"description": "Есть описание"}, {"amount": 100}]
    result: List[str] = list(transaction_descriptions(transactions))
    assert result == ["", "Есть описание", ""]


def test_transaction_descriptions_mixed(mixed_transactions: List[Dict[str, Any]]) -> None:
    """Тест получения описаний из смешанных транзакций."""
    result: List[str] = list(transaction_descriptions(mixed_transactions))
    expected: List[str] = ["Корректная транзакция 1", "", "Корректная транзакция 2", "", "Корректная транзакция 3"]
    assert result == expected
    assert len(result) == 5


def test_transaction_descriptions_generator_property(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест проверки свойств генератора описаний."""
    generator: Iterator[str] = transaction_descriptions(sample_transactions)

    # Проверяем ленивую генерацию
    first_description: str = next(generator)
    assert first_description == "Перевод организации"

    second_description: str = next(generator)
    assert second_description == "Перевод со счета на счет"


# ====== ТЕСТЫ ДЛЯ card_number_generator ======


def test_card_number_generator_small_range() -> None:
    """Тест генерации карт в небольшом диапазоне."""
    result: List[str] = list(card_number_generator(1, 5))
    expected: List[str] = [
        "0000 0000 0000 0001",
        "0000 0000 0000 0002",
        "0000 0000 0000 0003",
        "0000 0000 0000 0004",
        "0000 0000 0000 0005",
    ]
    assert result == expected
    assert len(result) == 5


def test_card_number_generator_single_value() -> None:
    """Тест генерации одной карты."""
    result: List[str] = list(card_number_generator(10, 10))
    assert result == ["0000 0000 0000 0010"]
    assert len(result) == 1


def test_card_number_generator_with_leading_zeros() -> None:
    """Тест генерации карт с ведущими нулями."""
    result: List[str] = list(card_number_generator(999, 1002))
    expected: List[str] = ["0000 0000 0000 0999", "0000 0000 0000 1000", "0000 0000 0000 1001", "0000 0000 0000 1002"]
    assert result == expected
    assert all(len(card.replace(" ", "")) == 16 for card in result)


def test_card_number_generator_max_value() -> None:
    """Тест генерации максимального значения карты."""
    result: List[str] = list(card_number_generator(9999999999999999, 9999999999999999))
    assert result == ["9999 9999 9999 9999"]


def test_card_number_generator_cross_boundary() -> None:
    """Тест генерации карт при переходе через разряды."""
    result: List[str] = list(card_number_generator(9999, 10001))
    expected: List[str] = ["0000 0000 0000 9999", "0000 0000 0001 0000", "0000 0000 0001 0001"]
    assert result == expected


def test_card_number_generator_format_validation() -> None:
    """Тест проверки форматирования номеров карт."""
    result: List[str] = list(card_number_generator(12345678, 12345678))
    card: str = result[0]

    # Проверяем формат: 4 группы по 4 цифры
    parts: List[str] = card.split()
    assert len(parts) == 4
    assert all(len(part) == 4 for part in parts)
    assert all(part.isdigit() for part in parts)
    assert card == "0000 0000 1234 5678"


def test_card_number_generator_start_less_than_one() -> None:
    """Тест ошибки при start < 1."""
    with pytest.raises(
        ValueError, match="Номер карты должен быть в диапазоне от 0000 0000 0000 0001 до 9999 9999 9999 9999"
    ):
        list(card_number_generator(0, 10))


def test_card_number_generator_negative_start() -> None:
    """Тест ошибки при отрицательном start."""
    with pytest.raises(
        ValueError, match="Номер карты должен быть в диапазоне от 0000 0000 0000 0001 до 9999 9999 9999 9999"
    ):
        list(card_number_generator(-5, 10))


def test_card_number_generator_end_too_large() -> None:
    """Тест ошибки при end превышающем максимальное значение."""
    with pytest.raises(
        ValueError, match="Номер карты должен быть в диапазоне от 0000 0000 0000 0001 до 9999 9999 9999 9999"
    ):
        list(card_number_generator(1, 10000000000000000))


def test_card_number_generator_start_greater_than_end() -> None:
    """Тест ошибки когда start > end."""
    with pytest.raises(ValueError, match="Начальное значение не может быть больше конечного"):
        list(card_number_generator(100, 50))


def test_card_number_generator_large_range() -> None:
    """Тест генерации большого диапазона карт (проверка количества)."""
    result: List[str] = list(card_number_generator(1000, 2000))
    assert len(result) == 1001  # 2000 - 1000 + 1
    assert result[0] == "0000 0000 0000 1000"
    assert result[-1] == "0000 0000 0000 2000"


def test_card_number_generator_generator_property() -> None:
    """Тест проверки свойств генератора."""
    generator: Generator[str, None, None] = card_number_generator(1, 3)

    # Проверяем ленивую генерацию
    assert next(generator) == "0000 0000 0000 0001"
    assert next(generator) == "0000 0000 0000 0002"
    assert next(generator) == "0000 0000 0000 0003"

    # Проверяем, что генератор исчерпан
    with pytest.raises(StopIteration):
        next(generator)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
