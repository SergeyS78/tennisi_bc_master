"""Модуль обеспечивает логирование работы приложения в seq
Используется библиотека seqlog. Работает через стандартный логгер Python"""

import inspect
from pathlib import Path
from flask import current_app
from flask_log_request_id import current_request_id
import seqlog


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

    properties['AssemblyName'] = "bc_master"
    properties['current_request_id'] = request_id
    properties['func_name'] = func_name
    properties['module_name'] = module_name
    properties['lineno'] = lineno

    seqlog.set_global_log_properties(**properties)

    current_app.logger.info(msg)
