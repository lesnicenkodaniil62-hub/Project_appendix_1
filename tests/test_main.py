from src.processing import filter_by_state, sort_by_date
from src.widget import get_date, mask_account_card

# Примеры использования и проверка
if __name__ == "__main__":
    # Проверка mask_account_card
    test_cases = [
        "Maestro 1596837868705199",
        "Счет 64686473678894779589",
        "MasterCard 7158300734726758",
        "Счет 35383033474447895560",
        "Visa Classic 6831982476737658",
        "Visa Platinum 8990922113665229",
        "Visa Gold 5999414228426353",
        "Счет 73654108430135874305",
    ]

    print("Проверка функции mask_account_card:")
    for test in test_cases:
        print(f"{test} -> {mask_account_card(test)}")

    print("\n" + "=" * 50 + "\n")

    # Проверка get_date
    date_test = "2024-03-11T02:26:18.671407"
    print(f"get_date('{date_test}') -> {get_date(date_test)}")

    # Пример использования и проверка

    # Входные данные для проверки
    test_data = [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
    ]

    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ФУНКЦИИ filter_by_state")
    print("=" * 70)

    print("\nИсходный список:")
    for item in test_data:
        print(f"  {item}")

    # Проверка filter_by_state с параметром по умолчанию
    print("\n1. filter_by_state(test_data) - фильтр по умолчанию 'EXECUTED':")
    filtered_default = filter_by_state(test_data)
    for item in filtered_default:
        print(f"  {item}")

    # Проверка filter_by_state с параметром 'CANCELED'
    print("\n2. filter_by_state(test_data, 'CANCELED'):")
    filtered_canceled = filter_by_state(test_data, "CANCELED")
    for item in filtered_canceled:
        print(f"  {item}")

    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ ФУНКЦИИ sort_by_date")
    print("=" * 70)

    # Проверка sort_by_date с параметром по умолчанию (убывание)
    print("\n3. sort_by_date(test_data) - сортировка по убыванию (новые сверху):")
    sorted_desc = sort_by_date(test_data)
    for i, item in enumerate(sorted_desc, 1):
        print(f"  {i}. {item}")
        print(f"     Дата: {item['date']}")

    # Проверка sort_by_date с параметром descending=False
    print("\n4. sort_by_date(test_data, descending=False) - сортировка по возрастанию:")
    sorted_asc = sort_by_date(test_data, descending=False)
    for i, item in enumerate(sorted_asc, 1):
        print(f"  {i}. {item}")
        print(f"     Дата: {item['date']}")

    print("\n" + "=" * 70)
    print("КОМБИНИРОВАННОЕ ИСПОЛЬЗОВАНИЕ ФУНКЦИЙ")
    print("=" * 70)

    # Пример комбинированного использования: сначала фильтруем, потом сортируем
    print("\n5. Сначала фильтруем по 'EXECUTED', затем сортируем по дате (убывание):")
    filtered = filter_by_state(test_data, "EXECUTED")
    sorted_filtered = sort_by_date(filtered)
    for item in sorted_filtered:
        print(f"  {item}")

    print("\n6. Сначала фильтруем по 'CANCELED', затем сортируем по дате (возрастание):")
    filtered = filter_by_state(test_data, "CANCELED")
    sorted_filtered = sort_by_date(filtered, descending=False)
    for item in sorted_filtered:
        print(f"  {item}")

    print("\n" + "=" * 70)
    print("ПРОВЕРКА, ЧТО ИСХОДНЫЙ СПИСОК НЕ ИЗМЕНИЛСЯ")
    print("=" * 70)
    print("\nИсходный список (первые элементы):")
    for i, item in enumerate(test_data[:2], 1):
        print(f"  {i}. id={item['id']}, state={item['state']}, date={item['date']}")

    print(f"\nДлина исходного списка: {len(test_data)}")
    print(f"Длина отфильтрованного списка (EXECUTED): {len(filtered_default)}")
    print(f"Длина отфильтрованного списка (CANCELED): {len(filtered_canceled)}")
    print(f"Длина отсортированного списка (убыв.): {len(sorted_desc)}")
    print(f"Длина отсортированного списка (возр.): {len(sorted_asc)}")
