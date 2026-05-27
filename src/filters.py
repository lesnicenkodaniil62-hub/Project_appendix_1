import re


def process_bank_search(data: list[dict], search: str) -> list[dict]:
    """
    Возвращает список транзакций, в описании которых найдена указанная подстрока.
    Поиск выполняется с помощью регулярных выражений (регистронезависимо).
    """
    if not search:
        return data

    # re.escape экранирует спецсимволы, чтобы поиск работал как безопасная подстрока.
    # re.IGNORECASE делает поиск нечувствительным к регистру (стандарт для UI-поиска).
    pattern = re.compile(re.escape(search), re.IGNORECASE)

    return [item for item in data if pattern.search(str(item.get("description", "")))]
