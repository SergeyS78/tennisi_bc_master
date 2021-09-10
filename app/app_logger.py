"""Модуль обеспечивает логирование работы приложения в seq
Используется библиотека seqlog. Работает через стандартный логгер Python"""

import inspect
import logging
from pathlib import Path
from flask_log_request_id import current_request_id
import seqlog
from config import JsonEncoder
from flask import current_app


def send_log_to_seq(msg, properties={}):
    """Отправляет данные на seq.
    Обновляет глобальные константы для seqlog и отправляет данные в seq.
    Константы можно добавлять любые, мы используем id текущего запроса, молуль и функцию,
    из которых произведена запись"""

    request_id = current_request_id()
    func_name = inspect.getframeinfo(inspect.currentframe()
                                     .f_back).function
    parts = Path(inspect.currentframe()
                 .f_back.f_code.co_filename).with_suffix("").parts
    module_name = ".".join(parts[-3:])
    lineno = inspect.currentframe().f_back.f_lineno

    properties['AssemblyName'] = "STAT_API"
    properties['current_request_id'] = request_id
    properties['func_name'] = func_name
    properties['module_name'] = module_name
    properties['lineno'] = lineno

    seqlog.set_global_log_properties(**properties)

    logger = get_logger(module_name)
    logger.info(msg)


def get_logger(name):
    """Создает логгер с именем, равным имени модуля из которой он запущен"""

    logger = logging.getLogger(name)

    return logger
