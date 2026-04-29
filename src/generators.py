from typing import Any, Dict, Generator, Iterator


def filter_by_currency(transactions: list[Dict[str, Any]], currency_code: str) -> Iterator[Dict[str, Any]]:
    """
    Фильтрует транзакции по заданной валюте.

    Возвращает итератор с транзакциями, у которых валюта операции равна currency_code.

    Транзакции без ключа "operationAmount" или вложенного ключа "currency" игнорируются.

    Аргументы:
        transactions: Список словарей с транзакциями.
        currency_code: Код валюты для фильтрации (например, "USD", "EUR").

    Возвращается:
        Итератор словарей, отфильтрованных по валюте.
    """

    for transaction in transactions:
        has_operation = "operationAmount" in transaction
        if has_operation:
            op_amount = transaction["operationAmount"]
            has_currency = "currency" in op_amount
            if has_currency and op_amount["currency"]["code"] == currency_code:
                yield transaction


def transaction_descriptions(transactions: list[Dict[str, Any]]) -> Iterator[str]:
    """
    Возвращает описания транзакций по очереди.

    Аргументы:
        transactions: список словарей с транзакциями.

    Yields:
        Описание транзакции.
    """
    for transaction in transactions:
        yield transaction.get("description", "")


def card_number_generator(start: int, end: int) -> Generator[str, None, None]:
    """
    Генератор номеров банковских карт в заданном диапазоне.

    Аргументы:
        start: Начальное значение (включительно)
        end: Конечное значение (включительно)
    Возвращается
        Номер карты в формате XXXX XXXX XXXX XXXX
    Условие:
        ValueError: Если start или end вне допустимого диапазона
    """
    if end > 9999999999999999 or start < 1:
        raise ValueError("Номер карты должен быть в диапазоне от 0000 0000 0000 0001 до 9999 9999 9999 9999")
    if start > end:
        raise ValueError("Начальное значение не может быть больше конечного")

    for number in range(start, end + 1):
        # Форматируем номер: 16 цифр с ведущими нулями
        formatted = f"{number:016d}"
        # Добавляем пробелы каждые 4 цифры
        card_number = " ".join(formatted[i : i + 4] for i in range(0, 16, 4))
        yield card_number
