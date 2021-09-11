"""Содержит фабрику приложений Flask.

Также сообщает Python, что каталог следует рассматривать как отдельный пакет.

Запуск приложения:
flask run
"""

import time
from flask import Flask, g, request
from flask_docs import ApiDoc
from flask_log_request_id import RequestID
import seqlog

import app.database as db
from config import Config, JsonEncoder
from app import logging_into_seq, urls as main


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
    """

    app = Flask(__name__)
    app.config.from_object(config_class)
    RequestID(app)
    ApiDoc(app)
    db.init_app(app)
    app.json_encoder = JsonEncoder

    seq_log_config = app.config['SEQ_LOG_CONF']
    seqlog.log_to_seq(
        server_url=seq_log_config['server_url'],
        api_key=seq_log_config['api_key'],
        level=seq_log_config['level'],
        batch_size=seq_log_config['batch_size'],
        auto_flush_timeout=seq_log_config['auto_flush_timeout'],  # seconds
        override_root_logger=seq_log_config['override_root_logger'],
        json_encoder_class=app.json_encoder, )

    app.register_blueprint(main.bp)

    app.add_url_rule('/', endpoint='index')

    @app.route('/')
    def index():
        return 'bc_master is running'

    @app.before_request
    def before_request():
        """Перед началом обработки запроса"""
        data_bases_names = app.config["PROJECT_DATA_BASES"].keys()
        g.db_connections = dict.fromkeys(data_bases_names)
        g.start = time.time()
        logging_into_seq.send_log_to_seq(
            f"Get request, path: {request.path}")

    @app.after_request
    def after_request(response):
        """По окончании выполнения запроса"""
        diff = time.time() - g.start
        logging_into_seq.send_log_to_seq(f"Запрос обработан.",
                                         {"elapsed_time": diff})
        return response

    return app
