from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple


def log(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для логирования начала и конца выполнения функции,
    а также результатов или ошибок.

    Args:
        filename: имя файла для записи логов. Если None, логи выводятся в консоль.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
            func_name = func.__name__
            try:
                result = func(*args, **kwargs)
                message = f"{func_name} ok"
                _write_log(message, filename)
                return result
            except Exception as e:
                error_type = type(e).__name__
                inputs_repr = f"Inputs: {args}, {kwargs}"
                message = f"{func_name} error: {error_type}. {inputs_repr}"
                _write_log(message, filename)
                raise

        return wrapper

    return decorator


def _write_log(message: str, filename: Optional[str]) -> None:
    """Записывает лог в файл или в консоль."""
    if filename:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    else:
        print(message)
