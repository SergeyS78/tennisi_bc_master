"""Определение и доступ к базе данных

Модуль работает с базой данный postgesql. Настройки подключения в файле config.py

Создает соединение с базой данных. Любые запросы и операции выполняются через соединение,
которое закрывается после завершения работы. Соединение привязано к запросу.
Он создается при обработке запроса и закрывается перед отправкой ответа.
"""

import psycopg2
import psycopg2.extras
from psycopg2 import Error, pool
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import current_app, g, request
from app import logger_into_seq

POOLS = {}


def get_db_name_from_request():
    """Получает имя базы данных из префикса роутера запроса"""
    return request.url_rule.rule.split('/')[1]


def check_db_name(db_name):
    """Проверяет, передано ли имя базы данных в запросе.
    Иначе получает его из префикса роутера в запросе"""
    if db_name is None:
        return get_db_name_from_request()

    return db_name


def open_db_connection(db_name):
    """Открывает соединение с базой данных

    current_app- специальный объект Flask, который указывает на приложение Flask,
    обрабатывающее запрос.

    База данных вызовется, когда приложение будет открыто. Поэтому использование
    current_app тут оправдано

    Создадаем пул соединений, который будет работать в многопоточной среде.
    Это можно сделать с помощью класса ThreadedConnectionPool.

    request.url_rule.rule содержит активный роутер. Из него берем вид спорта и получаем
    настройки базы данных по данному виду спорта из current_app.config
    """

    try:
        if db_name not in POOLS:
            POOLS[db_name] = psycopg2.pool.ThreadedConnectionPool(
                **current_app.config[f"DATABASES"][db_name])
            logger_into_seq.send_log_to_seq(
                f"PostgreSQL - - Пул соединений для '{db_name}' создан успешно.")

        # Получаем соединение из пула соединений.
        connection = POOLS[db_name].getconn()
        if connection:
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    except (Exception, psycopg2.DatabaseError) as err:
        logger_into_seq.send_log_to_seq(
            f"PostgreSQL - - ошибка при подключении к '{db_name}': {err}")
        raise err from None

    return connection


def get_db_connection(db_name):
    """Возвращает ссылку на соединение с базой данных

    g- это особый объект Flask, уникальный для каждого запроса. Он используется для хранения данных,
    к которым могут обращаться несколько функций во время запроса.
    Соединение сохраняется и используется повторно вместо создания нового соединения,
    если get_db вызывается второй раз в том же запросе.

    Поскольку в проекте будет использоваться фабрика приложений,
    при написании остальной части кода объект приложения еще отсутствует. get_db будет вызываться,
    когда приложение будет создано и начнет обрабатывать запрос.
    """

    if g.db_connections[db_name] is None:
        g.db_connections[db_name] = open_db_connection(db_name)

    logger_into_seq.send_log_to_seq(
        f"PostgreSQL - - Соединение с {db_name} установлено.")

    return g.db_connections[db_name]


def close_db(e=None):
    """Проверяет, было ли создано соединение и проверяет, было ли g.db установлено.

    Если соединение существует, оно закрывается.

    Далее этот метод будет зарегистрирован в фабрике приложений, и будет вызываться автоматически
    в конце каждого запроса.
    """

    for db_name, connection in g.db_connections.items():

        if connection is not None:
            connection.cursor().close()
            POOLS[db_name].putconn(connection)
            logger_into_seq.send_log_to_seq(
                f"PostgreSQL - - соединение c '{db_name}' вернулось в пул.")

    g.pop('db_connections')


def init_app(app):
    """Функцию close_db необходимо зарегистрировать в экземпляре приложения,
    в противном случае она не будут использоваться приложением.
    Однако, поскольку вы используете фабричную функцию, этот экземпляр недоступен
    при написании функций. Вместо этого функция init_app примет приложение и выполняет регистрацию
    базы данных в ней.

    app.teardown_appcontext() сообщает Flask о необходимости вызвать эту функцию
    при очистке после возврата ответа.

    Будет вызываться из фабрики:
        from . import database
        database.init_app(app)
    """

    app.teardown_appcontext(close_db)


def get_row_count(cursor):
    """Выдает количество измененных запросом строк базы данных"""

    try:
        count = cursor.rowcount
    except (Exception, Error) as err:
        logger_into_seq.send_log_to_seq(f"Ошибка при работе с PostgreSQL: {err}")
        raise

    return count


def execute_sql(query, data_for_query=None, db_name=None):
    """Выполняет sql запрос

    Для красивого вывода информационного сообщения предварительно удаляет \n и лишние пробелы
    из строки запроса.

    Функция mogrify из psycopg2 возвращает скомпилированный запрос с уже подставленными в него
    внешними данными.
    """

    db_name = check_db_name(db_name)

    db_connection = get_db_connection(db_name)
    cursor = db_connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor)

    query = ' '.join(query.split())
    logger_into_seq.send_log_to_seq(f"PostgreSQL - - Выполняется запрос.",
                                    {"sql": cursor.mogrify(query, data_for_query)})

    cursor.execute(query, data_for_query)

    return cursor


def execute_and_fetchall_sql(query, data_for_query=None, db_name=None):
    """Выполняет sql запрос"""

    db_name = check_db_name(db_name)

    try:
        cursor = execute_sql(query=query, db_name=db_name, data_for_query=data_for_query)
        records = cursor.fetchall()
    except (Exception, Error) as err:
        logger_into_seq.send_log_to_seq(f"Ошибка при работе с PostgreSQL: {err}")
        raise

    return records

def execute_and_fetchone_sql(query, data_for_query=None, db_name=None):
    """Выполняет sql запрос"""

    db_name = check_db_name(db_name)

    try:
        cursor = execute_sql(query=query, db_name=db_name, data_for_query=data_for_query)
        records = cursor.fetchone()
    except (Exception, Error) as err:
        logger_into_seq.send_log_to_seq(f"Ошибка при работе с PostgreSQL: {err}")
        raise

    return records


def execute_sql_list_as_transaction(queries, db_name=None):
    """Выполняет список запросов 'queries' как одну транзакцию при помощи контекстного менеджера.

    Каждый запрос передается в виде кортежа (запрос, данные для запроса)
    """

    db_name = check_db_name(db_name)

    db_connection = None

    try:
        db_connection = get_db_connection(db_name)
        db_connection.autocommit = False
        cursor = db_connection.cursor

        logger_into_seq.send_log_to_seq("PostgreSQL - - Начало транзакции.")

        for query in queries:
            logger_into_seq.send_log_to_seq(
                f"PostgreSQL - - Выполняется запрос:\t{query[0]}.")
            cursor.execute(query)

        logger_into_seq.send_log_to_seq(
            "PostgreSQL - - Транзакция успешно завершена.")

    except (Exception, psycopg2.DatabaseError) as error:
        logger_into_seq.send_log_to_seq(
            f"PostgreSQL - - Ошибка в транзакции. "
            f"Отмена всех остальных операций транзакции: {error}")
        if db_connection:
            db_connection.rollback()
        raise


def insert(query, data_for_query=None, db_name=None):
    """CRUD insert"""

    db_name = check_db_name(db_name)

    cursor = execute_sql(query=query, db_name=db_name, data_for_query=data_for_query)
    logger_into_seq.send_log_to_seq(
        f"PostgreSQL - - {get_row_count(cursor)} запись(ей) успешно добавлена в таблицу.")

    return 'ок'


def update(query, data_for_query=None, db_name=None):
    """CRUD update"""

    db_name = check_db_name(db_name)

    cursor = execute_sql(query=query, db_name=db_name, data_for_query=data_for_query)
    logger_into_seq.send_log_to_seq(
        f"PostgreSQL - - {get_row_count(cursor)} запись успешно обновлена.")

    return 'ок'


def delete(query, data_for_query=None, db_name=None):
    """CRUD delete"""

    db_name = check_db_name(db_name)

    cursor = execute_sql(query=query, db_name=db_name, data_for_query=data_for_query)
    logger_into_seq.send_log_to_seq(
        f"PostgreSQL - - {get_row_count(cursor)} запись успешно удалена.")

    return 'ок'


def select_all(query, data_for_query=None, db_name=None):
    """CRUD select"""

    db_name = check_db_name(db_name)

    result = execute_and_fetchall_sql(query=query, data_for_query=data_for_query, db_name=db_name)
    logger_into_seq.send_log_to_seq(
        f"PostgreSQL - - {len(result)} запись(ей) получено.")

    return result

def select_one(query, data_for_query=None, db_name=None):
    """CRUD select"""

    db_name = check_db_name(db_name)

    result = execute_and_fetchone_sql(query=query, data_for_query=data_for_query, db_name=db_name)
    logger_into_seq.send_log_to_seq(
        f"PostgreSQL - - {len(result)} запись(ей) получено.")

    return result
