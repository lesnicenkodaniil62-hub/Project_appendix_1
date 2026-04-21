from typing import Any, Dict, List

import pytest

from src.masks import get_mask_account, get_mask_card_number
from src.processing import filter_by_state, sort_by_date
from src.widget import get_date, mask_account_card


# ==================== ТЕСТЫ ДЛЯ get_mask_card_number ====================
class TestGetMaskCardNumber:
    """Тесты для маскировки номера карты"""

    def test_valid_card_16_digits(self) -> None:
        """Тест корректной карты с 16 цифрами"""
        assert get_mask_card_number("7000792289606361") == "7000 79** **** 6361"

    def test_valid_card_with_spaces(self) -> None:
        """Тест: функция должна работать с номерами без пробелов"""
        # Функция принимает только строку без пробелов по условию
        assert get_mask_card_number("7000792289606361") == "7000 79** **** 6361"

    def test_card_less_than_16_digits(self) -> None:
        """Тест карты с менее чем 16 цифрами"""
        assert get_mask_card_number("7000792289") == "Некорректный номер карты"

    def test_card_with_letters(self) -> None:
        """Тест карты с буквами"""
        assert get_mask_card_number("7000abcd8960efgh") == "Некорректный номер карты"

    def test_invalid_empty_string(self) -> None:
        """Тест пустой строки"""
        assert get_mask_card_number(" ") == "Некорректный номер карты"

    def test_card_with_more_than_16_digits(self) -> None:
        """Тест карты с более чем 16 цифрами"""
        assert get_mask_card_number("70007922896063617") == "Некорректный номер карты"

    def test_card_with_special_chars(self) -> None:
        """Тест карты со спецсимволами"""
        assert get_mask_card_number("7000-7922-8960-6361") == "Некорректный номер карты"


# ==================== ТЕСТЫ ДЛЯ get_mask_account ====================
class TestGetMaskAccount:
    """Тесты для маскировки номера счета"""

    def test_valid_account(self) -> None:
        """Тест корректного счета"""
        assert get_mask_account("73654108430135874305") == "**4305"

    def test_account_with_4_digits(self) -> None:
        """Тест сокращённого счета состоящих из последних 4 цифр"""
        assert get_mask_account("4305") == "**4305"

    def test_account_with_3_digits(self) -> None:
        """Тест счета с менее чем 4 цифрами"""
        assert get_mask_account("123") == "Некорректный номер счета"

    def test_account_with_letters(self) -> None:
        """Тест счета с буквами"""
        assert get_mask_account("abcd4305") == "Некорректный номер счета"

    def test_empty_account(self) -> None:
        """Тест пустого счета"""
        assert get_mask_account("") == "Некорректный номер счета"


# ==================== ТЕСТЫ ДЛЯ mask_account_card ====================
class TestMaskAccountCard:
    """Тесты для функции mask_account_card"""

    def test_visaClassic_card(self) -> None:
        """Тест карты VisaVisa Classic"""
        result = mask_account_card("Visa Classic 6831982476737658")
        assert result == "Visa Classic 6831 98** **** 7658"

    def test_visaPlatinum_card(self) -> None:
        """Тест карты Visa Platinum"""
        result = mask_account_card("Visa Platinum 8990922113665229")
        assert result == "Visa Platinum 8990 92** **** 5229"

    def test_visaGold_card(self) -> None:
        """Тест карты Visa Gold"""
        result = mask_account_card("Visa Gold 5999414228426353")
        assert result == "Visa Gold 5999 41** **** 6353"

    def test_mastercard(self) -> None:
        """Тест карты MasterCard"""
        result = mask_account_card("MasterCard 7158300734726758")
        assert result == "MasterCard 7158 30** **** 6758"

    def test_account_1(self) -> None:
        """Тест счета"""
        result = mask_account_card("Счет 64686473678894779589")
        assert result == "Счет **9589"

    def test_account_2(self) -> None:
        """Тест счета"""
        result = mask_account_card("Счет 35383033474447895560")
        assert result == "Счет **5560"

    def test_account_3(self) -> None:
        """Тест счета"""
        result = mask_account_card("Счет 73654108430135874305")
        assert result == "Счет **4305"

    def test_maestro_card(self) -> None:
        """Тест карты Maestro"""
        result = mask_account_card("Maestro 1596837868705199")
        assert result == "Maestro 1596 83** **** 5199"

    def test_mir_card(self) -> None:
        """Тест карты МИР"""
        result = mask_account_card("МИР 1234567890123456")
        assert result == "МИР 1234 56** **** 3456"

    def test_invalid_format_no_space(self) -> None:
        """Тест строки без пробела"""
        result = mask_account_card("Visa1234567890123456")
        assert result == "Visa1234567890123456"  # Возвращает исходную строку

    def test_invalid_card_number(self) -> None:
        """Тест некорректного номера карты"""
        result = mask_account_card("Visa 1234")
        assert result == "Visa Некорректный номер карты"

    def test_invalid_account_number(self) -> None:
        """Тест некорректного номера счета"""
        result = mask_account_card("Счет 123")
        assert result == "Счет Некорректный номер счета"


# ==================== ТЕСТЫ ДЛЯ get_date ====================
class TestGetDate:
    """Тесты для функции get_date"""

    def test_standard_date(self) -> None:
        """Тест стандартной даты"""
        result = get_date("2024-03-11T02:26:18.671407")
        assert result == ("11.03.2024" "")

    def test_date_with_different_time(self) -> None:
        """Тест даты с другим временем"""
        result = get_date("2023-12-25T15:30:45.123456")
        assert result == "25.12.2023"

    def test_date_without_milliseconds(self) -> None:
        """Тест даты без миллисекунд"""
        result = get_date("2024-01-01T00:00:00")
        assert result == "01.01.2024"

    def test_date_with_zulu_time(self) -> None:
        """Тест даты с Z в конце"""
        result = get_date("2024-06-15T10:20:30Z")
        assert result == "15.06.2024"

    def test_first_day_of_year(self) -> None:
        """Тест первого дня года"""
        result = get_date("2024-01-01T00:00:00")
        assert result == "01.01.2024"

    def test_last_day_of_year(self) -> None:
        """Тест последнего дня года"""
        result = get_date("2024-12-31T23:59:59")
        assert result == "31.12.2024"


# ==================== ТЕСТЫ ДЛЯ filter_by_state ====================
class TestFilterByState:
    """Тесты для функции filter_by_state"""

    @staticmethod
    def filter_by_state(transaction_1: List[Dict[str, Any]], state: str = "EXECUTED") -> List[Dict[str, Any]]:
        """
        Фильтрует список словарей по значению ключа 'state'.

         Аргументы:
            filter_state: Список словарей с данными транзакций
            state: Значение для фильтрации (по умолчанию 'EXECUTED')

        Возвращается:
            Новый список словарей с указанным значением state
        """
        return [item for item in transaction_1 if item.get("state") == state]

    def test_filter_by_state_default(self) -> None:
        """Тест фильтрации со статусом по умолчанию 'EXECUTED'"""
        transactions: List[Dict[str, Any]] = [
            {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
            {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
            {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
            {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
        ]

        expected: List[Dict[str, Any]] = [
            {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
            {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        ]

        assert filter_by_state(transactions) == expected

    def test_filter_by_state_canceled(self) -> None:
        """Тест фильтрации со статусом 'CANCELED'"""
        transactions: List[Dict[str, Any]] = [
            {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
            {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
            {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
            {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
        ]

        expected: List[Dict[str, Any]] = [
            {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
            {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
        ]

        assert filter_by_state(transactions, "CANCELED") == expected

    def test_filter_by_state_empty_list(self) -> None:
        """Тест фильтрации с пустым списком"""
        transactions: List[Dict[str, Any]] = []
        expected: List[Dict[str, Any]] = []

        assert filter_by_state(transactions) == expected

    def test_filter_by_state_no_matches(self) -> None:
        """Тест фильтрации, когда нет совпадений"""
        transactions: List[Dict[str, Any]] = [
            {"id": 41428829, "state": "PENDING", "date": "2019-07-03T18:35:29.512364"},
            {"id": 939719570, "state": "PENDING", "date": "2018-06-30T02:08:58.425572"},
        ]

        expected: List[Dict[str, Any]] = []

        assert filter_by_state(transactions) == expected


# ==================== ТЕСТЫ ДЛЯ sort_by_date ====================
class TestSortByDate:
    """Тесты для функции sort_by_date"""

    @staticmethod
    def sort_by_date(transaction_2: List[Dict[str, Any]], descending: bool = True) -> List[Dict[str, Any]]:
        """
        Сортирует список словарей по дате (ключ 'date').

        Аргументы:
            sort_date: Список словарей с данными транзакций
            descending: Порядок сортировки. True - убывание (сначала новые),
                       False - возрастание (сначала старые). По умолчанию True.

        Возвращается:
            Новый список, отсортированный по дате
        """
        return sorted(transaction_2, key=lambda x: x.get("date", ""), reverse=descending)

    def test_sort_by_date_descending(self) -> None:
        """Тест сортировки по убыванию (новые сначала)"""
        transactions: List[Dict[str, Any]] = [
            {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
            {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
            {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
            {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
        ]

        expected: List[Dict[str, Any]] = [
            {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
            {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
            {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        ]

        assert sort_by_date(transactions) == expected

    def test_sort_by_date_ascending(self) -> None:
        """Тест сортировки по возрастанию (старые сначала)"""
        transactions: List[Dict[str, Any]] = [
            {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
            {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
            {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
            {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
        ]

        expected: List[Dict[str, Any]] = [
            {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
            {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
            {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        ]

        assert sort_by_date(transactions, descending=False) == expected

    def test_sort_by_date_empty_list(self) -> None:
        """Тест сортировки пустого списка"""
        transactions: List[Dict[str, Any]] = []
        expected: List[Dict[str, Any]] = []

        assert sort_by_date(transactions) == expected

    def test_sort_by_date_missing_date(self) -> None:
        """Тест сортировки, когда у некоторых элементов нет ключа 'date'"""
        transactions: List[Dict[str, Any]] = [
            {"id": 1, "state": "EXECUTED", "date": "2020-01-01"},
            {"id": 2, "state": "EXECUTED"},  # нет даты
            {"id": 3, "state": "EXECUTED", "date": "2019-01-01"},
        ]

        # Элементы без даты получают пустую строку и уходят в начало/конец в зависимости от сортировки
        result: List[Dict[str, Any]] = sort_by_date(transactions)

        assert len(result) == 3
        # Элемент без даты будет первым при сортировке по убыванию
        assert result[0]["id"] == 1
        assert result[1]["id"] == 3
        assert result[2]["id"] == 2


# ==================== ЗАПУСК ТЕСТОВ ====================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
