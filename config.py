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
    PROJECT_DATA_BASES = os.environ.get('PROJECT_DATA_BASES') or PROJECT_DATA_BASES
    SEQ_LOG_CONF = os.environ.get('SEQ_LOG_CONF') or SEQ_LOG_CONF

    # API_DOC: настройки авто документирования проекта
    api_doc_member = ['basket', 'hockey', 'soccer']
    # RESTful Api документы должны быть исключены
    restful_api_doc_exclude = []


class JsonEncoder(json.JSONEncoder):
    """Определение метода сериализации данных типа Decimal в json формат."""

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)
