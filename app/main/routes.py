import time

from flask import current_app, g
from app import app_logger
from app.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    return 'Welcome to bc_master'


@bp.before_request
def before_request():
    """Перед началом обработки запроса"""
    data_bases_names = current_app.config["project_data_bases"].keys()
    g.db_connections = dict.fromkeys(data_bases_names)
    g.start = time.time()


@bp.after_request
def after_request(response):
    """По окончании выполнения запроса"""
    diff = time.time() - g.start
    app_logger.send_log_to_seq(f"Запрос обработан.",
                               {"elapsed_time": diff})
    return response
