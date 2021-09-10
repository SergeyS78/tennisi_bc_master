import time

from flask import current_app, g, Blueprint, request
from app import logger_into_seq

bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    return 'Welcome to bc_master'


@bp.before_request
def before_request():
    """Перед началом обработки запроса"""
    data_bases_names = current_app.config["PROJECT_DATA_BASES"].keys()
    g.db_connections = dict.fromkeys(data_bases_names)
    g.start = time.time()
    logger_into_seq.send_log_to_seq(
        f"Get request, path: {request.path}")


@bp.after_request
def after_request(response):
    """По окончании выполнения запроса"""
    diff = time.time() - g.start
    logger_into_seq.send_log_to_seq(f"Запрос обработан.",
                                    {"elapsed_time": diff})
    return response
