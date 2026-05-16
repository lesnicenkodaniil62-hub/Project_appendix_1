from unittest.mock import MagicMock, patch

import requests

from src.external_api import convert_to_rubles


def test_convert_to_rubles_already_rub() -> None:
    """Тест: если валюта уже рубли — возвращается исходная сумма."""
    transaction = {"operationAmount": {"amount": "100.50", "currency": {"code": "RUB", "name": "руб."}}}
    result = convert_to_rubles(transaction)

    assert result == 100.50
    assert isinstance(result, float)


def test_convert_to_rubles_usd_with_api_mock() -> None:
    """Тест: конвертация USD в рубли через маркированный вызов API."""
    transaction = {
        "operationAmount": {"amount": "100.00", "currency": {"code": "USD", "name": "USD"}},
        "date": "2018-01-01T10:00:00",
    }

    # Макаем запрос к внешнему API
    with patch("src.external_api.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 6000.0}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = convert_to_rubles(transaction)

        assert result == 6000.0
        assert isinstance(result, float)
        # Проверяем, что запрос был выполнен ровно один раз
        mock_get.assert_called_once()
        # Проверяем корректность параметров в URL
        call_args = mock_get.call_args
        assert "to=RUB" in call_args[0][0]
        assert "from=USD" in call_args[0][0]
        assert "amount=100.0" in call_args[0][0]


def test_convert_to_rubles_eur_with_api_mock() -> None:
    """Тест: конвертация EUR в рубли через маркированный вызов API."""
    transaction = {
        "operationAmount": {"amount": "50.00", "currency": {"code": "EUR", "name": "EUR"}},
        "date": "2019-06-15T12:30:00.123456",
    }

    with patch("src.external_api.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 4500.0}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = convert_to_rubles(transaction)

        assert result == 4500.0
        assert isinstance(result, float)


def test_convert_to_rubles_api_error_fallback() -> None:
    """Тест: при ошибке API возвращается исходная сумма."""
    transaction = {"operationAmount": {"amount": "100.00", "currency": {"code": "USD", "name": "USD"}}}

    # Имитируем исключение requests.RequestException (реалистичная ошибка сети)
    with patch("src.external_api.requests.get", side_effect=requests.RequestException("API Error")):
        result = convert_to_rubles(transaction)

        # Должна вернуться исходная сумма при ошибке
        assert result == 100.0
        assert isinstance(result, float)


def test_convert_to_rubles_api_timeout_fallback() -> None:
    """Тест: при тайм-ауте API возвращается исходная сумма."""
    transaction = {"operationAmount": {"amount": "250.00", "currency": {"code": "EUR", "name": "EUR"}}}

    # requests.Timeout — это подкласс RequestException, реалистичный сценарий
    with patch("src.external_api.requests.get", side_effect=requests.Timeout("Request timed out")):
        result = convert_to_rubles(transaction)
        assert result == 250.0
        assert isinstance(result, float)


def test_convert_to_rubles_missing_operation_amount() -> None:
    """Тест: обработка транзакции без ключа operationAmount."""
    transaction: dict = {}
    result = convert_to_rubles(transaction)
    assert result == 0.0


def test_convert_to_rubles_invalid_amount_string() -> None:
    """Тест: обработка невалидной строки суммы."""
    transaction = {"operationAmount": {"amount": "not-a-number", "currency": {"code": "RUB"}}}
    result = convert_to_rubles(transaction)
    assert result == 0.0


def test_convert_to_rubles_unknown_currency() -> None:
    """Тест: неизвестный код валюты возвращает исходную сумму."""
    transaction = {"operationAmount": {"amount": "100.00", "currency": {"code": "GBP", "name": "British Pound"}}}
    result = convert_to_rubles(transaction)
    assert result == 100.0


def test_convert_to_rubles_api_returns_invalid_json() -> None:
    """Тест: если API вернул ответ без ключа 'result' — используется исходная сумма."""
    transaction = {"operationAmount": {"amount": "75.00", "currency": {"code": "USD"}}}

    with patch("src.external_api.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "invalid"}  # Нет ключа 'result'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = convert_to_rubles(transaction)
        # Должна вернуться исходная сумма
        assert result == 75.0


def test_convert_to_rubles_date_parsing_fallback() -> None:
    """Тест: при невалидном формате даты используется дата по умолчанию."""
    transaction = {"operationAmount": {"amount": "100.00", "currency": {"code": "USD"}}, "date": "invalid-date-format"}

    with patch("src.external_api.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 6000.0}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = convert_to_rubles(transaction)

        assert result == 6000.0
        # Проверяем, что в запросе использована дата по умолчанию
        call_url = mock_get.call_args[0][0]
        assert "date=2026-01-01" in call_url
