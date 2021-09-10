"""Содержит фабрику приложений Flask.

Также сообщает Python, что каталог следует рассматривать как отдельный пакет.

Запуск приложения:
flask run
"""

from flask import Flask, json
from flask_docs import ApiDoc
from flask_log_request_id import RequestID
import seqlog

import app.database as db
from config import Config, JsonEncoder
from app.main import routes as main


def create_app(config_class=Config):
    """Фабрика приложений

    app = Flask(__name__)создает Flask экземпляр. __name__это имя текущего модуля Python.
    Приложению необходимо знать, где оно расположено, чтобы настроить некоторые пути,
    и __name__это удобный способ сообщить ему об этом

    app.config.from_object(config_class) - загружает рабочую конфигурацию из файла
    config.py в корне проекта

    RequestID(app) - сохранение и получение RequestID каждого запроса

    ApiDoc(app) - автодокументирование проекта

    database.init_app(app) - подключает базу данных к созданному приложению

    app.json_encoder - устанавливаем свой инкодер json с поддержкой Decimal

    seqlog.log_to_seq - настройки логирования в 'seq'

    app.register_blueprint() - импортирует и зарегистрирует новый блок для
    созданного приложения. В нашем случае создаст ссылку по имени подраздела:
        /basket/.../.../

    app.add_url_rule() -  установит '/' как index для всех разделов.
    Раздел /basket/ --> basket.index.
    """

    app = Flask(__name__)
    app.config.from_object(config_class)
    RequestID(app)
    ApiDoc(app)
    db.init_app(app)
    app.json_encoder = JsonEncoder

    seq_log_conf = app.config['SEQ_LOG_CONF']
    seqlog.log_to_seq(
        server_url=seq_log_conf['server_url'],
        api_key=seq_log_conf['api_key'],
        level=seq_log_conf['level'],
        batch_size=seq_log_conf['batch_size'],
        auto_flush_timeout=seq_log_conf['auto_flush_timeout'],  # seconds
        override_root_logger=seq_log_conf['override_root_logger'],
        json_encoder_class=app.json_encoder, )

    app.register_blueprint(main.bp)

    app.add_url_rule('/', endpoint='index')

    return app
