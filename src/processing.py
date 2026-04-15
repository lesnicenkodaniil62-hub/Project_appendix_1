def filter_by_state(transaction_1: list, state: str = "EXECUTED") -> list:
    """
    Фильтрует список словарей по значению ключа 'state'.

    Аргументы:
        filter_state: Список словарей с данными транзакций
        state: Значение для фильтрации (по умолчанию 'EXECUTED')

    Возвращается:
        Новый список словарей с указанным значением state
    """
    return [item for item in transaction_1 if item.get("state") == state]


def sort_by_date(transaction_2: list, descending: bool = True) -> list:
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
