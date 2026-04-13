from src.widget import get_date, mask_account_card

# from src.processing import filter_by_state, sort_by_date

# Примеры использования и проверка
if __name__ == "__main__":
    print(mask_account_card(input("Введите номер")))
    print(get_date(input("Введите дату")))
