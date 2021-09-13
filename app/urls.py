import app.views as views
from flask import Blueprint, current_app, jsonify
from app.views.functions import log_this_into_seq as log_this

bp = Blueprint('main', __name__, url_prefix='/api')


@bp.route('/get_leagues_api_new/')
@log_this
def get_leagues_api_new():
    """
    @@@
    #### Аrgs:
    не принимает параметров

    #### Return:
    | return | rtype |
    |--------|--------|
    |    список команд    |    Serialized data to JSON and wrapped in a ~flask.Response with the application/json mimetype.    |

    #### Описание:
    Получает список команд с отсутствующим id (без статистики).
    Принимает запрос вида:
    http://127.0.0.1:5000/вид спорта/clean_matches_wo_sources

    Обрабатывается модулем clean_matches_wo_sources.

    В оригинальной программе роутер "getLeaguesAPINEW".
    @@@
    """

    res = views.get_leagues_api_new()

    return jsonify(res)
