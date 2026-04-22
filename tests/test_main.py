import pytest

from src.masks import get_mask_account, get_mask_card_number
from src.processing import filter_by_state, sort_by_date
from src.widget import get_date, mask_account_card


# ==================== ТЕСТЫ ДЛЯ get_mask_card_number ====================
@pytest.mark.parametrize(
    "string, expected_result",
    [
        ("7000792289606361", "7000 79** **** 6361"),  # Тест корректной карты с 16 цифрами
        ("7000792289", "Некорректный номер карты"),  # Тест карты с менее чем 16 цифрами
        ("7000abcd8960efgh", "Некорректный номер карты"),  # Тест карты с буквами
        (" ", "Некорректный номер карты"),  # Тест пустой строки
        ("70007922896063617", "Некорректный номер карты"),  # Тест карты с более чем 16 цифрами
        ("7000-7922-8960-6361", "Некорректный номер карты"),  # Тест сокращённого счета состоящих из последних 4 цифр
    ],
)
def test_get_mask_card_number(string: str, expected_result: str) -> None:
    assert get_mask_card_number(string) == expected_result


# ==================== ТЕСТЫ ДЛЯ get_mask_account ====================
@pytest.mark.parametrize(
    "string, expected_result",
    [
        ("73654108430135874305", "**4305"),  # Тест корректного счета
        ("4305", "**4305"),  # Тест сокращённого счета состоящих из последних 4 цифр
        ("123", "Некорректный номер счета"),  # Тест счета с менее чем 4 цифрами
        ("abcd4305", "Некорректный номер счета"),  # Тест счета с буквами
        ("", "Некорректный номер счета"),  # Тест пустого счета
    ],
)
def test_get_mask_account(string: str, expected_result: str) -> None:
    assert get_mask_account(string) == expected_result


# ==================== ТЕСТЫ ДЛЯ mask_account_card ====================
@pytest.mark.parametrize(
    "string, expected_result",
    [
        ("Visa Classic 6831982476737658", "Visa Classic 6831 98** **** 7658"),  # Тест карты VisaVisa Classic
        ("Visa Platinum 8990922113665229", "Visa Platinum 8990 92** **** 5229"),  # Тест карты Visa Platinum
        ("Visa Gold 5999414228426353", "Visa Gold 5999 41** **** 6353"),  # Тест карты Visa Gold
        ("MasterCard 7158300734726758", "MasterCard 7158 30** **** 6758"),  # Тест карты MasterCard
        ("Счет 64686473678894779589", "Счет **9589"),  # Тест счета 1
        ("Счет 35383033474447895560", "Счет **5560"),  # Тест счета 2
        ("Счет 73654108430135874305", "Счет **4305"),  # Тест счета 3
        ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),  # Тест карты Maestro
        ("МИР 1234567890123456", "МИР 1234 56** **** 3456"),  # Тест карты МИР
        ("Visa1234567890123456", "Visa1234567890123456"),  # Тест строки без пробела
        ("Visa 1234", "Visa Некорректный номер карты"),  # Тест некорректного номера карты
        ("Счет 123", "Счет Некорректный номер счета"),  # Тест некорректного номера счета
    ],
)
def test_mask_account_card(string: str, expected_result: str) -> None:
    assert mask_account_card(string) == expected_result


# ==================== ТЕСТЫ ДЛЯ get_date ====================
@pytest.mark.parametrize(
    "string, expected_result",
    [
        ("2024-03-11T02:26:18.671407", "11.03.2024"),  # Тест стандартной даты
        ("2023-12-25T15:30:45.123456", "25.12.2023"),  # Тест даты с другим временем
        ("2024-01-01T00:00:00", "01.01.2024"),  # Тест даты без миллисекунд
        ("2024-06-15T10:20:30Z", "15.06.2024"),  # Тест даты с Z в конце
        ("2024-01-01T00:00:00", "01.01.2024"),  # Тест первого дня года
        ("2024-12-31T23:59:59", "31.12.2024"),  # Тест последнего дня года
    ],
)
def test_get_date(string: str, expected_result: str) -> None:
    assert get_date(string) == expected_result


# ==================== ТЕСТЫ ДЛЯ filter_by_state ====================


@pytest.mark.parametrize(
    "test_input, state, expected",
    [
        # Тест 1: Фильтрация по умолчанию (state="EXECUTED")
        (
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ],
            "EXECUTED",
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
            ],
        ),
        # Тест 2: Фильтрация по статусу "CANCELED"
        (
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ],
            "CANCELED",
            [
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ],
        ),
        # Тест 3: Пустой список
        ([], "EXECUTED", []),
        # Тест 4: Нет элементов с указанным статусом
        (
            [{"id": 1, "state": "PENDING", "date": "2023-01-01"}, {"id": 2, "state": "PENDING", "date": "2023-01-02"}],
            "EXECUTED",
            [],
        ),
        # Тест 5: Список с отсутствующим ключом 'state'
        (
            [{"id": 1, "date": "2023-01-01"}, {"id": 2, "state": "EXECUTED", "date": "2023-01-02"}],
            "EXECUTED",
            [{"id": 2, "state": "EXECUTED", "date": "2023-01-02"}],
        ),
    ],
)
def test_filter_by_state(test_input: list, state: str, expected: list) -> None:
    """Тестирует функцию filter_by_state с различными параметрами"""
    assert filter_by_state(test_input, state) == expected


# Тест для проверки значения по умолчанию
def test_filter_by_state_default() -> None:
    """Проверяет, что функция использует 'EXECUTED' как значение по умолчанию"""
    test_data = [{"id": 1, "state": "EXECUTED"}, {"id": 2, "state": "CANCELED"}]
    expected = [{"id": 1, "state": "EXECUTED"}]
    assert filter_by_state(test_data) == expected


# ==================== ТЕСТЫ ДЛЯ sort_by_date ====================


@pytest.mark.parametrize(
    "test_input, descending, expected",
    [
        # Тест 1: Сортировка по убыванию (по умолчанию) - сначала новые
        (
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ],
            True,
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
            ],
        ),
        # Тест 2: Сортировка по возрастанию - сначала старые
        (
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ],
            False,
            [
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
            ],
        ),
        # Тест 3: Пустой список
        ([], True, []),
        ([], False, []),
        # Тест 4: Список с одним элементом
        ([{"id": 1, "date": "2023-01-01"}], True, [{"id": 1, "date": "2023-01-01"}]),
        # Тест 5: Элементы с одинаковыми датами
        (
            [{"id": 1, "date": "2023-01-01"}, {"id": 2, "date": "2023-01-01"}, {"id": 3, "date": "2023-01-01"}],
            True,
            [{"id": 1, "date": "2023-01-01"}, {"id": 2, "date": "2023-01-01"}, {"id": 3, "date": "2023-01-01"}],
        ),
        # Тест 6: Отсутствие ключа 'date' у некоторых элементов
        (
            [{"id": 1, "date": "2023-01-02"}, {"id": 2, "name": "no date"}, {"id": 3, "date": "2023-01-01"}],
            True,
            [{"id": 1, "date": "2023-01-02"}, {"id": 3, "date": "2023-01-01"}, {"id": 2, "name": "no date"}],
        ),
    ],
)
def test_sort_by_date(test_input: list, descending: bool, expected: list) -> None:
    """Тестирует функцию sort_by_date с различными параметрами"""
    assert sort_by_date(test_input, descending) == expected


# Тест для проверки значения по умолчанию (descending=True)
def test_sort_by_date_default() -> None:
    """Проверяет, что функция использует descending=True как значение по умолчанию"""
    test_data = [{"id": 1, "date": "2023-01-01"}, {"id": 2, "date": "2023-01-02"}]
    expected = [{"id": 2, "date": "2023-01-02"}, {"id": 1, "date": "2023-01-01"}]
    assert sort_by_date(test_data) == expected


# ==================== ЗАПУСК ТЕСТОВ ====================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
