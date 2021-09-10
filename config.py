import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    PROJECT_DATA_BASES = os.environ.get('PROJECT_DATA_BASES')
    SEQ_LOG_CONF = os.environ.get('SEQ_LOG_CONF')
