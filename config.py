"""Получает параметры для конфигурации Flask приложения"""
import os
import json
import decimal
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

PROJECT_DATA_BASES = ''
SEQ_LOG_CONF = ''


class JsonEncoder(json.JSONEncoder):
    """Добавление метода сериализации данных типа Decimal в json формат."""

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def json_loads(obj):
    """Cоздает json из объекта.
     Возвращает json или сам объект, если его тип не поддерживается. В данном случае
     используется в конфигурации, если параметр не указан в .env и его значение
     возвращается как неподдерживаемый тип None"""

    try:
        return json.loads(obj)
    except (TypeError, ValueError):
        return obj


class Config(object):
    """Параметры запуска Flask приложения"""

    LOG_PATH = json_loads(os.environ.get('LOG_PATH')) or '/mnt/v-ecb/logs'
    TMP_FILES_PATH = os.environ.get(
        'TMP_FILES_PATH') or '/mnt/v-ecb/tmp_files'
    COMMON_DATA_PATH = os.environ.get(
        'COMMON_DATA_PATH') or '/mnt/v-ecb/common_data'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    PROJECT_DATA_BASES = json_loads(os.environ.get(
        'PROJECT_DATA_BASES')) or PROJECT_DATA_BASES
    SEQ_LOG_CONF = json_loads(os.environ.get('SEQ_LOG_CONF')) or SEQ_LOG_CONF

    # API_DOC: настройки авто документирования проекта
    API_DOC_MEMBER = ['basket', 'hockey', 'soccer']
    # RESTful Api документы, которые должны быть исключены
    RESTFUL_API_DOC_EXCLUDE = []
