"""Декоратор для логирования функций."""

import functools
import logging


def log_this_into_seq(func):
    """Обработчик ошибок.
    В случае поднятия исключения отправляет полное описание ошибки в SEQ.
    Чтобы сохранить в декораторе имя оборачиваемой функции/docstring,
    используем functools.wraps()"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            logging.error(err, exc_info=True)
            return {'error': 'it was an error'}

    return wrapper
