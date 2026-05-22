from src.widget import get_date, mask_account_card
from src.utils import read_transactions
from pathlib import Path
import sys
from src.transaction_reader import read_transactions_from_csv, read_transactions_from_excel

# from src.processing import filter_by_state, sort_by_date

def main() -> None:
    csv_path = Path("data/transactions.csv")
    excel_path = Path("data/transactions_excel.xlsx")

    # --- Чтение CSV ---
    try:
        csv_transactions = read_transactions_from_csv(csv_path)
        print(f"Успешно прочитано: {len(csv_transactions)} транзакций")
        print("Первые 3 записи:")
        for i, tx in enumerate(csv_transactions[:5], start=1):
            print(f"  [{i}] {tx}")
    except Exception as e:
        print(f"Ошибка при чтении CSV: {e}", file=sys.stderr)
        sys.exit(1)
    print()

    # --- Чтение Excel ---
    try:
        excel_transactions = read_transactions_from_excel(excel_path)
        print(f"Успешно прочитано: {len(excel_transactions)} транзакций")
        print("Первые 3 записи:")
        for i, tx in enumerate(excel_transactions[:5], start=1):
            print(f"  [{i}] {tx}")
    except ImportError as e:
        # Graceful fallback: ловим ImportError и выводим инструкцию без краша
        print(f" {e}", file=sys.stderr)
        print("Совет: запустите `pip install openpyxl` в вашем виртуальном окружении.")
    except Exception as e:
        print(f"Ошибка при чтении Excel: {e}", file=sys.stderr)
        sys.exit(1)
    print()

    print("Демонстрация завершена.")

# Примеры использования и проверка
if __name__ == "__main__":
    # Указываем путь к файлу с операциями
    file_path = "data/operations.json"

    # Читаем транзакции
    transactions = read_transactions(file_path)

    # если хотите проверить вывод через принт закомментируйте лишние и проверяйте нужное

    # Выводим результат
    print(mask_account_card(input("Введите номер")))        # здесь мы проверяем введите и выведение замаскированного номер.
    print(get_date(input("Введите дату")))                  # здесь мы проверяем введите и выведение даты.
    print(f"Найдено транзакций: {len(transactions)}")       # здесь мы проверяем считаем количество транзакций.
    print(transactions)                                     # здесь мы проверяем чтение формата json.
    main()                                                  # здесь мы проверяем чтение формата csv и xlsx.
