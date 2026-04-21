def get_mask_card_number(card_number: str) -> str:
    """Маскирует номер банковской карты."""
    if not card_number or not card_number.isdigit() or len(card_number) != 16:
        return "Некорректный номер карты"

    first_six = card_number[:6]
    last_four = card_number[-4:]

    # Форматируем первые 6 цифр как 'XXXX XX'
    formatted_first_six = f"{first_six[:4]} {first_six[4:]}"

    # Формируем маскированную часть
    masked_middle = "** ****"

    # Собираем все части в итоговую строку
    return f"{formatted_first_six}{masked_middle} {last_four}"


def get_mask_account(account: str) -> str:
    """Маскирует номер банковского счета."""
    # Проверка на наличие цифр и минимальную длину
    if not account.isdigit() or len(account) < 4:
        return "Некорректный номер счета"

    last_four = account[-4:]
    return f"**{last_four}"
