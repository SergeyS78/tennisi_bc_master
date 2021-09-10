

from flask import Blueprint


bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    return 'Welcome to bc_master'
