"""Получает параметры для конфигурации Flask приложения"""
import os
import json
import decimal
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

PROJECT_DATA_BASES = ''
SEQ_LOG_CONF = ''

class Config(object):
    """Параметры запуска Flask приложения"""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    PROJECT_DATA_BASES = json.loads(os.environ.get('PROJECT_DATA_BASES')) or PROJECT_DATA_BASES
    SEQ_LOG_CONF = json.loads(os.environ.get('SEQ_LOG_CONF')) or SEQ_LOG_CONF

    # API_DOC: настройки авто документирования проекта
    API_DOC_MEMBER = ['basket', 'hockey', 'soccer']
    # RESTful Api документы должны быть исключены
    RESTFUL_API_DOC_EXCLUDE = []


class JsonEncoder(json.JSONEncoder):
    """Определение метода сериализации данных типа Decimal в json формат."""

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)
