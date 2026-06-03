from random import choice, randint
from typing import Any, Dict, Generator, List, Set
from unittest.mock import MagicMock, patch

import pytest

import main as app

# =============================================================================
# ФИКСТУРЫ
# =============================================================================


@pytest.fixture
def random_json_transactions() -> List[Dict[str, Any]]:
    """
    ТЕСТ: Генерация случайных транзакций во вложенной JSON-структуре.
    ЧТО ПРОВЕРЯЕТ: Способность приложения корректно работать с вложенными данными
    (как при загрузке из JSON или API).
    ОСОБЕННОСТЬ: Гарантированно добавляет ровно одну рублёвую транзакцию,
    чтобы позже проверить логику фильтрации по алиасам рубля.
    """
    currencies: List[str] = ["Euro", "Dollar", "Peso", "Yuan", "Sol", "Shilling"]
    statuses: List[str] = ["EXECUTED", "CANCELED", "PENDING"]
    tx_list: List[Dict[str, Any]] = []
    for _ in range(randint(3, 6)):
        tx_list.append(
            {
                "date": f"2024-01-{randint(1, 28):02d}T12:00:00",
                "state": choice(statuses),
                "description": choice(["Покупка", "Перевод", "Оплата ЖКХ", "Снятие"]),
                "from": f"Visa *{randint(1000, 9999)}",
                "to": f"MasterCard *{randint(1000, 9999)}",
                "operationAmount": {
                    "amount": f"{randint(100, 15000)}.{randint(0, 99):02d}".replace(".", ","),
                    "currency": {"name": choice(currencies)},
                },
            }
        )
    # Гарантированно добавляем ровно одну рублевую транзакцию
    tx_list.append(
        {
            "date": "2024-01-15T10:00:00",
            "state": "EXECUTED",
            "description": "Тестовая рублевая операция",
            "from": "Visa *0000",
            "to": "Счет *0000",
            "operationAmount": {"amount": "1 234,56", "currency": {"name": "рубль"}},
        }
    )
    return tx_list


@pytest.fixture
def random_flat_transactions() -> List[Dict[str, Any]]:
    """
    ТЕСТ: Генерация случайных транзакций в плоской структуре.
    ЧТО ПРОВЕРЯЕТ: Корректность обработки данных из CSV/XLSX,
    где поля (amount, currency_name) находятся на верхнем уровне,
    а не вложены в operationAmount.
    """
    currencies: List[str] = ["Euro", "Shilling", "Krona", "Sol"]
    statuses: List[str] = ["EXECUTED", "CANCELED"]
    return [
        {
            "date": f"2024-02-{randint(1, 28):02d}",
            "state": choice(statuses),
            "description": f"Операция {i}",
            "amount": f"{randint(500, 20000)}.{randint(0, 99):02d}",
            "currency_name": choice(currencies),
        }
        for i in range(4)
    ]


@pytest.fixture
def patch_external_deps() -> Generator[Dict[str, MagicMock], None, None]:
    """
    ТЕСТ: Изоляция приложения от внешних зависимостей.
    ЧТО ПРОВЕРЯЕТ: Заменяет реальные функции чтения файлов, аналитики,
    поиска, форматирования даты и маскирования карт на mock-объекты.
    ПОЧЕМУ ЭТО НУЖНО: Тесты становятся детерминированными, не зависят
    от файловой системы, библиотек и рандома внутри main.py.
    Позволяет проверять, какие функции были вызваны и с какими аргументами.
    """
    with patch("main.read_transactions") as mock_read_json, patch(
        "main.read_transactions_from_csv"
    ) as mock_read_csv, patch("main.read_transactions_from_excel") as mock_read_xlsx, patch(
        "main.process_bank_operations", return_value={}
    ) as mock_analytics, patch(
        "main.process_bank_search",
        side_effect=lambda tx, kw: [t for t in tx if kw.lower() in str(t).lower()],
    ) as mock_search, patch(
        "main.get_date", return_value="15.01.2024"
    ) as mock_date, patch(
        "main.mask_account_card", return_value="**** 1234"
    ) as mock_mask:
        yield {
            "json": mock_read_json,
            "csv": mock_read_csv,
            "xlsx": mock_read_xlsx,
            "analytics": mock_analytics,
            "search": mock_search,
            "date": mock_date,
            "mask": mock_mask,
        }


# =============================================================================
# МОДУЛЬНЫЕ ТЕСТЫ
# =============================================================================


def test_extract_amount_and_currency_json(random_json_transactions: List[Dict[str, Any]]) -> None:
    """
    ТЕСТ: Извлечение суммы и валюты из JSON-структуры.
    ЧТО ПРОВЕРЯЕТ: Функция корректно парсит вложенный ключ operationAmount,
    преобразует строку с суммой в float и возвращает точное название валюты.
    """
    amount, currency = app.extract_amount_and_currency(random_json_transactions[0])
    assert isinstance(amount, float)
    assert currency == random_json_transactions[0]["operationAmount"]["currency"]["name"]


def test_extract_amount_and_currency_flat(random_flat_transactions: List[Dict[str, Any]]) -> None:
    """
    ТЕСТ: Извлечение суммы и валюты из плоской структуры.
    ЧТО ПРОВЕРЯЕТ: То же, что и выше, но для данных CSV/XLSX,
    где amount и currency_name лежат на верхнем уровне словаря.
    """
    amount, currency = app.extract_amount_and_currency(random_flat_transactions[0])
    assert isinstance(amount, float)
    assert currency == random_flat_transactions[0]["currency_name"]


def test_format_transaction_amount_correct_formatting(random_json_transactions: List[Dict[str, Any]]) -> None:
    """
    ТЕСТ: Форматирование суммы для вывода пользователю.
    ЧТО ПРОВЕРЯЕТ: Наличие пробела-разделителя тысяч (например, "1 234,56")
    и корректное сохранение цифр в строке.
    """
    formatted: str = app.format_transaction_amount(random_json_transactions[0])
    assert " " in formatted
    assert any(char.isdigit() for char in formatted)


@pytest.mark.parametrize("target", ["рубль", "Euro"])
def test_filter_by_currency_variants(target: str, random_json_transactions: List[Dict[str, Any]]) -> None:
    """
    ТЕСТ: Фильтрация транзакций по валюте с поддержкой синонимов рубля.
    ЧТО ПРОВЕРЯЕТ:
    1. Точное совпадение для обычных валют (например, "Euro").
    2. Учёт алиасов рубля: "рубль", "RUB", "руб.", "rouble" и т.д.
    3. Динамический подсчёт expected_count гарантирует, что тест
       не будет "flaky" из-за случайной генерации данных.
    """
    rub_aliases: Set[str] = {"рубль", "rubl", "ruble", "rub", "руб.", "российский рубль", "rouble"}

    expected_count: int = 0
    for tx in random_json_transactions:
        # str() нужен, чтобы mypy не ругался на неявное присваивание Any к str
        curr_name: str = str(tx.get("operationAmount", {}).get("currency", {}).get("name", "")).lower()
        if target.lower() in rub_aliases:
            if curr_name in rub_aliases:
                expected_count += 1
        else:
            if curr_name == target.lower():
                expected_count += 1

    result: List[Any] = app.filter_by_currency(random_json_transactions, target)
    assert len(result) == expected_count


def test_get_unique_currencies_returns_sorted_list(
    random_json_transactions: List[Dict[str, Any]], random_flat_transactions: List[Dict[str, Any]]
) -> None:
    """
    ТЕСТ: Сбор уникальных валют из смешанного списка транзакций.
    ЧТО ПРОВЕРЯЕТ:
    1. Удаление дубликатов.
    2. Строгая сортировка результата по алфавиту.
    """
    combined: List[Dict[str, Any]] = random_json_transactions + random_flat_transactions
    unique: List[str] = app.get_unique_currencies(combined)
    assert isinstance(unique, list)
    assert unique == sorted(unique)


# =============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ (main flow)
# =============================================================================


@pytest.mark.parametrize(
    "rub_choice, other_currency_choice, file_type, expected_in_output",
    [
        ("да", "нет", "1", "только рублевые"),
        ("нет", "да", "1", "Применен фильтр по валюте"),
        ("нет", "нет", "2", "Всего банковских операций"),
    ],
)
def test_main_currency_flow(
    rub_choice: str,
    other_currency_choice: str,
    file_type: str,
    expected_in_output: str,
    random_json_transactions: List[Dict[str, Any]],
    patch_external_deps: Dict[str, MagicMock],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    ТЕСТ: Полный консольный сценарий выбора валюты.
    ЧТО ПРОВЕРЯЕТ:
    - Пользователь выбирает только рубли → выводится "только рублевые".
    - Пользователь выбирает другую валюту → вводит её, выводится "Применен фильтр...".
    - Пользователь отказывается от фильтра → выводится общая статистика.
    - Захватывает stdout через capsys и проверяет ожидаемые фразы.
    """
    if file_type == "1":
        patch_external_deps["json"].return_value = random_json_transactions
    elif file_type == "2":
        patch_external_deps["csv"].return_value = random_json_transactions
    else:
        patch_external_deps["xlsx"].return_value = random_json_transactions

    inputs: List[str] = [file_type, "EXECUTED", "нет", rub_choice, other_currency_choice, "нет", "нет"]
    if rub_choice.lower() == "нет" and other_currency_choice.lower() == "да":
        inputs.insert(5, "Euro")

    with patch("builtins.input", side_effect=inputs):
        app.main()

    captured = capsys.readouterr()
    assert expected_in_output in captured.out


@pytest.mark.parametrize("file_type, read_mock_name", [("1", "json"), ("2", "csv"), ("3", "xlsx")])
def test_main_loads_correct_file_type(
    file_type: str,
    read_mock_name: str,
    random_json_transactions: List[Dict[str, Any]],
    patch_external_deps: Dict[str, MagicMock],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    ТЕСТ: Корректный выбор функции чтения файла по вводу пользователя.
    ЧТО ПРОВЕРЯЕТ: При вводе "1" вызывается только JSON-ридер,
    "2" → CSV-ридер, "3" → XLSX-ридер. assert_called_once() гарантирует,
    что лишние функции чтения не срабатывают.
    """
    inputs: List[str] = [file_type, "EXECUTED", "нет", "да", "нет", "нет", "нет"]
    patch_external_deps["json"].return_value = random_json_transactions
    patch_external_deps["csv"].return_value = random_json_transactions
    patch_external_deps["xlsx"].return_value = random_json_transactions

    with patch("builtins.input", side_effect=inputs):
        app.main()

    reader: MagicMock = patch_external_deps[read_mock_name]
    reader.assert_called_once()


# =============================================================================
# ТЕСТЫ ОБРАБОТКИ ОШИБОК
# =============================================================================


def test_read_wrapper_handles_missing_file() -> None:
    """
    ТЕСТ: Обработка отсутствия файла.
    ЧТО ПРОВЕРЯЕТ: При выбросе FileNotFoundError обёртка не падает,
    а возвращает пустой список [].
    """
    with patch("main.read_transactions", side_effect=FileNotFoundError):
        assert app.read_transactions_wrapper("json") == []


def test_read_wrapper_handles_import_error() -> None:
    """
    ТЕСТ: Обработка отсутствия библиотеки openpyxl.
    ЧТО ПРОВЕРЯЕТ: При ImportError (нет модуля xlsx) функция
    корректно ловит исключение и возвращает [].
    """
    with patch("main.read_transactions_from_excel", side_effect=ImportError("No module named openpyxl")):
        assert app.read_transactions_wrapper("xlsx") == []


def test_read_wrapper_handles_unknown_type() -> None:
    """
    ТЕСТ: Обработка неподдерживаемого формата.
    ЧТО ПРОВЕРЯЕТ: Передача "xml" или другого неизвестного типа
    должна вернуть [], а не вызвать KeyError или crash.
    """
    assert app.read_transactions_wrapper("xml") == []


def test_main_exits_on_empty_data(
    patch_external_deps: Dict[str, MagicMock], capsys: pytest.CaptureFixture[str]
) -> None:
    """
    ТЕСТ: Загрузка пустого файла.
    ЧТО ПРОВЕРЯЕТ: Если ридер вернул [], приложение должно вывести
    сообщение об ошибке и корректно завершить работу, не переходя к фильтрам.
    """
    patch_external_deps["json"].return_value = []
    with patch("builtins.input", side_effect=["1"]):
        app.main()
    captured = capsys.readouterr()
    assert "Не удалось загрузить транзакции" in captured.out


def test_main_handles_empty_after_filter(
    random_json_transactions: List[Dict[str, Any]],
    patch_external_deps: Dict[str, MagicMock],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    ТЕСТ: Фильтр отсеивает все транзакции.
    ЧТО ПРОВЕРЯЕТ: Если данные есть, но ни одна не прошла фильтр (например,
    ищем RUB, а в файле только USD), приложение должно вывести
    "Не найдено ни одной транзакции" и не упасть при попытке форматирования.
    """
    usd_data: List[Dict[str, Any]] = [
        {
            "date": "2024-01-01T00:00:00",
            "state": "EXECUTED",
            "description": "Test",
            "from": "A",
            "to": "B",
            "operationAmount": {"amount": "100", "currency": {"name": "USD"}},
        }
    ]
    patch_external_deps["json"].return_value = usd_data

    with patch("builtins.input", side_effect=["1", "EXECUTED", "нет", "да", "нет", "нет"]):
        app.main()

    captured = capsys.readouterr()
    assert "Не найдено ни одной транзакции" in captured.out
