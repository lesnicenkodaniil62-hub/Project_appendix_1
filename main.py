from pathlib import Path
from typing import Any, Dict, List, Optional

from src.bank_processor import process_bank_operations
from src.filters import process_bank_search
from src.transaction_reader import read_transactions_from_csv, read_transactions_from_excel
from src.utils import read_transactions
from src.widget import get_date, mask_account_card

# Фиксированные пути к файлам с данными
DATA_DIR: Path = Path(__file__).resolve().parent / "data"
FILE_PATHS: Dict[str, Path] = {
    "json": DATA_DIR / "operations.json",
    "csv": DATA_DIR / "transactions.csv",
    "xlsx": DATA_DIR / "transactions_excel.xlsx",
}


def get_user_choice(prompt: str, options: List[str]) -> str:
    """Запрашивает выбор пользователя из списка допустимых вариантов."""
    while True:
        choice = input(prompt).strip().lower()
        if choice in [opt.lower() for opt in options]:
            return choice
        print(f"Неверный ввод. Доступные варианты: {', '.join(options)}")


def get_valid_status(available_statuses: List[str]) -> Optional[str]:
    """Запрашивает статус с валидацией и нормализацией регистра."""
    while True:
        print(
            "Введите статус, по которому необходимо выполнить фильтрацию. \n"
            f"Доступные для фильтровки статусы: {', '.join(available_statuses)}"
        )
        user_input = input().strip()
        normalized_input = user_input.upper()

        if normalized_input in available_statuses:
            return normalized_input
        else:
            print(f'Статус операции "{user_input}" недоступен.')


def filter_by_status(transactions: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """Фильтрует транзакции по статусу."""
    return [t for t in transactions if str(t.get("state", "")).upper() == status]


def sort_by_date(transactions: List[Dict[str, Any]], ascending: bool = True) -> List[Dict[str, Any]]:
    """Сортирует транзакции по дате."""

    def parse_date(tx: Dict[str, Any]) -> str:
        date_val = str(tx.get("date", ""))
        return date_val.split("T")[0] if "T" in date_val else date_val

    return sorted(transactions, key=parse_date, reverse=not ascending)


def extract_amount_and_currency(tx: Dict[str, Any]) -> tuple[float, str]:
    """
    Извлекает сумму и название валюты независимо от формата:
    • JSON: берёт из operationAmount.amount и operationAmount.currency.name
    • CSV/XLSX: берёт из столбцов amount и currency_name (с fallback на currency)
    """
    op_amount = tx.get("operationAmount")
    if isinstance(op_amount, dict):
        raw_amount = op_amount.get("amount")
        curr_data = op_amount.get("currency", {})
        currency_name = curr_data.get("name", "Неизвестно") if isinstance(curr_data, dict) else str(curr_data)
    else:
        raw_amount = tx.get("amount")
        currency_name = tx.get("currency_name", tx.get("currency", "Неизвестно"))

    try:
        amount = float(str(raw_amount).replace(",", ".").strip())
    except (ValueError, TypeError):
        amount = 0.0

    return amount, str(currency_name).strip()


def get_unique_currencies(transactions: List[Dict[str, Any]]) -> List[str]:
    """Возвращает отсортированный список уникальных названий валют из транзакций."""
    currencies = set()
    for tx in transactions:
        _, curr_name = extract_amount_and_currency(tx)
        if curr_name and curr_name != "Неизвестно":
            currencies.add(curr_name)
    return sorted(currencies)


def filter_by_currency(transactions: List[Dict[str, Any]], target: str) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по названию валюты.
    Поддерживает нечувствительное к регистру сравнение + синонимы для рубля.
    """
    if not target:
        return transactions

    target_lower = target.strip().lower()
    rub_aliases = {"рубль", "rubl", "ruble", "rub", "руб.", "российский рубль", "rouble"}

    filtered = []
    for tx in transactions:
        _, curr_name = extract_amount_and_currency(tx)
        curr_lower = curr_name.lower()

        if target_lower in rub_aliases and curr_lower in rub_aliases:
            filtered.append(tx)
        elif curr_lower == target_lower:
            filtered.append(tx)

    return filtered


def format_transaction_amount(tx: Dict[str, Any]) -> str:
    """Форматирует сумму и название валюты для вывода."""
    amount, currency_name = extract_amount_and_currency(tx)

    if amount.is_integer():
        amount_str = f"{int(amount):,}".replace(",", " ")
    else:
        amount_str = f"{amount:,.2f}".replace(",", " ")

    return f"{amount_str} {currency_name}"


def format_transaction(tx: Dict[str, Any]) -> str:
    """Форматирует одну транзакцию для вывода."""
    raw_date = tx.get("date", "")
    date_formatted = get_date(str(raw_date)) if raw_date else "Неизвестно"
    description = tx.get("description") or tx.get("name", "Без описания")

    accounts = []
    if tx.get("from"):
        accounts.append(mask_account_card(str(tx["from"])))
    if tx.get("to"):
        accounts.append(mask_account_card(str(tx["to"])))

    result = f"{date_formatted} {description}\n"
    if accounts:
        result += " -> ".join(accounts) + "\n"
    result += f"Сумма: {format_transaction_amount(tx)}"
    return result


def print_transactions(transactions: List[Dict[str, Any]]) -> None:
    """Выводит отформатированный список транзакций."""
    print(f"\nВсего банковских операций в выборке: {len(transactions)}\n")
    for i, tx in enumerate(transactions):
        print(format_transaction(tx))
        if i < len(transactions) - 1:
            print()


def read_transactions_wrapper(file_type: str) -> List[Dict[str, Any]]:
    """Загружает данные из фиксированного файла с корректной обработкой ошибок."""
    file_path = FILE_PATHS.get(file_type)
    if not file_path:
        print(f"Ошибка: неизвестный тип файла '{file_type}'.")
        return []

    try:
        # Преобразуем Path в str, чтобы удовлетворить строгую типизацию read_transactions
        path_str = str(file_path)
        if file_type == "json":
            return read_transactions(path_str)
        elif file_type == "csv":
            return read_transactions_from_csv(path_str)
        elif file_type == "xlsx":
            return read_transactions_from_excel(path_str)
    except ImportError as e:
        if file_type == "xlsx":
            print("Ошибка: для работы с Excel-файлами требуется библиотека 'openpyxl'.")
            print("Совет: запустите `pip install openpyxl` в вашем виртуальном окружении.")
        else:
            print(f"Ошибка импорта зависимостей: {e}")
        return []
    except FileNotFoundError:
        print(f"Ошибка: файл не найден по пути: {file_path}")
        return []
    except Exception as e:
        print(f"Непредвиденная ошибка при чтении файла: {e}")
        return []

    #  Явный return для удовлетворения type checker (mypy)
    return []


def main() -> None:
    """Основная логика программы."""
    print(
        "Привет! Добро пожаловать в программу работы с банковскими транзакциями. \n"
        "Выберите необходимый пункт меню:\n"
        "1. Получить информацию о транзакциях из JSON-файла\n"
        "2. Получить информацию о транзакциях из CSV-файла\n"
        "3. Получить информацию о транзакциях из XLSX-файла"
    )

    file_choice = get_user_choice("\nВаш выбор (1-3): ", ["1", "2", "3"])
    format_map = {"1": "json", "2": "csv", "3": "xlsx"}
    selected_format = format_map[file_choice]
    print(f"\nДля обработки выбран {selected_format.upper()}-файл.")

    # 1. Загрузка данных
    transactions = read_transactions_wrapper(selected_format)
    if not transactions:
        print("Не удалось загрузить транзакции. Проверьте наличие и структуру файла.")
        return

    # 2. Фильтрация по статусу
    status = get_valid_status(["EXECUTED", "CANCELED", "PENDING"])
    if status:
        print(f'Операции отфильтрованы по статусу "{status}"')
        transactions = filter_by_status(transactions, status)

    # 3. Сортировка по дате
    if get_user_choice("\nОтсортировать операции по дате? Да/Нет: ", ["да", "нет"]) == "да":
        order = get_user_choice("Отсортировать по возрастанию или по убыванию? ", ["по возрастанию", "по убыванию"])
        transactions = sort_by_date(transactions, ascending=(order == "по возрастанию"))
        print(f"Операции отсортированы {'по возрастанию' if order == 'по возрастанию' else 'по убыванию'}")

    # 4. ПРИОРИТЕТНАЯ ЛОГИКА ФИЛЬТРАЦИИ ПО ВАЛЮТЕ
    rub_choice = get_user_choice("\nВыводить транзакции в рублях? Да/Нет: ", ["да", "нет"])

    if rub_choice == "да":
        transactions = filter_by_currency(transactions, "рубль")
        print("Применен фильтр: только рублевые транзакции")
    else:
        # Если не рубли, спрашиваем про фильтрацию по другой валюте
        if get_user_choice("\nОтфильтровать транзакции по другой валюте? Да/Нет: ", ["да", "нет"]) == "да":
            available_currencies = get_unique_currencies(transactions)
            if available_currencies:
                print(f"\nДоступные валюты в данных: {', '.join(available_currencies)}")
                target_curr = input("Введите название валюты для фильтрации: ").strip()
                if target_curr:
                    transactions = filter_by_currency(transactions, target_curr)
                    print(f"Применен фильтр по валюте: {target_curr}")
            else:
                print("В текущей выборке не найдены другие валюты.")

    # 5. Фильтрация по ключевому слову
    if get_user_choice("\nОтфильтровать список транзакций по слову в описании? Да/Нет: ", ["да", "нет"]) == "да":
        keyword = input("Введите слово для поиска: ").strip()
        if keyword:
            transactions = process_bank_search(transactions, keyword)
            print(f'Применена фильтрация по слову: "{keyword}"')

    # ПРОВЕРКА НА ПУСТУЮ ВЫБОРКУ
    if not transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши\nусловия фильтрации")
        return

    # 6. Аналитика
    if get_user_choice("\nПоказать сводку по типам операций? Да/Нет: ", ["да", "нет"]) == "да":
        categories = list({tx.get("description") or tx.get("name", "Без категории") for tx in transactions})
        stats = process_bank_operations(transactions, categories)
        print("\nСводка по операциям:")
        for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
            if count > 0:
                print(f"  • {cat}: {count}")

    # 7. Вывод результата
    print("\nРаспечатываю итоговый список транзакций...")
    print_transactions(transactions)


if __name__ == "__main__":
    main()
