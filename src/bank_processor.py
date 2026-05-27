from collections import Counter


def process_bank_operations(data: list[dict], categories: list) -> dict:
    """
    Подсчитывает количество операций для каждой категории с использованием collections.Counter.

    :param data: Список словарей с банковскими операциями.
    :param categories: Список категорий для агрегации.
    :return: Словарь {категория: количество}
    """
    # Counter автоматически игнорирует отсутствующие ключи, возвращая 0
    counts = Counter(op.get("description") for op in data)

    # Формируем итоговый словарь строго в порядке переданных категорий
    return {cat: counts[cat] for cat in categories}
