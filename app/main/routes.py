from flask import Blueprint

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return 'bc_master is running'
