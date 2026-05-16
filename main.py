from src.widget import get_date, mask_account_card
from src.utils import read_transactions

# from src.processing import filter_by_state, sort_by_date

# Примеры использования и проверка
if __name__ == "__main__":
    # Указываем путь к файлу с операциями
    file_path = 'data/operations.json'

    # Читаем транзакции
    transactions = read_transactions(file_path)

    # Выводим результат
    print(mask_account_card(input("Введите номер")))
    print(get_date(input("Введите дату")))
    print(f"Найдено транзакций: {len(transactions)}")
    print(transactions)
