from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(input_string: str) -> str:
    """
    Принимает строку с типом и номером карты или счета.
    Возвращает строку с замаскированным номером.
    """
    # Разделяем строку на части
    parts = input_string.rsplit(' ', 1)

    if len(parts) != 2:
        return input_string

    card_type = parts[0]
    number = parts[1]

    # Определяем, карта это или счет
    if card_type.lower() == "счет":
        return f"{card_type} {get_mask_account(number)}"
    else:
        return f"{card_type} {get_mask_card_number(number)}"


def get_date(date_string: str) -> str:
    """
    Принимает строку с датой в формате "2024-03-11T02:26:18.671407"
    Возвращает строку с датой в формате "ДД.ММ.ГГГГ"
    """
    # Извлекаем часть с датой (до буквы T)
    date_part = date_string.split('T')[0]

    # Разделяем на год, месяц, день
    year, month, day = date_part.split('-')

    # Возвращаем в формате ДД.ММ.ГГГГ
    return f"{day}.{month}.{year}"
