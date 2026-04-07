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
