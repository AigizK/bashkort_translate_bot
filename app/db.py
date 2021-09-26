import sqlite3
import random
from datetime import datetime


def get_raw_pair(id):
    try:
        sqlite_connection = sqlite3.connect('ba_ru_pairs.db')
        cursor = sqlite_connection.cursor()

        sqlite_select_query = '''
        select * from raw_pair
        where id=?'''

        cursor.execute(sqlite_select_query, (int(id),))
        record = cursor.fetchone()
        return {'id': record[0], 'ba': record[1], 'ru': record[2]}
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def save_user_answer(id, answer, username, userid):
    try:
        sqlite_connection = sqlite3.connect('ba_ru_pairs.db')
        cursor = sqlite_connection.cursor()
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        sqlite_select_query = '''
        insert into check_result(pair_id,result,author,date,author_id) values(?,?,?,?,?)'''

        cursor.execute(sqlite_select_query,
                       (int(id), int(answer), username, dt_string, userid))
        sqlite_connection.commit()
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def add_blocked_user(userid):
    try:
        sqlite_connection = sqlite3.connect('ba_ru_pairs.db')
        cursor = sqlite_connection.cursor()
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        sqlite_select_query = '''
        insert into user_is_blocked(user,date) values(?,?)'''

        cursor.execute(sqlite_select_query, (userid, dt_string))
        sqlite_connection.commit()
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def get_blocked_users():
    results = []

    try:
        sqlite_connection = sqlite3.connect('ba_ru_pairs.db')
        cursor = sqlite_connection.cursor()

        sqlite_select_query = '''select distinct user from user_is_blocked'''

        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        for record in records:
            results.append(record[0])

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
    return results


def get_next_task():
    try:
        sqlite_connection = sqlite3.connect('ba_ru_pairs.db')
        cursor = sqlite_connection.cursor()

        sqlite_select_query = '''
        select r.id,ba,ru from raw_pair r 
        left join check_result c 
        on r.id=c.pair_id 
        where c.id is null 
        limit 100'''

        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        results = []
        for record in records:
            results.append({'id': record[0], 'ba': record[1], 'ru': record[2]})

        cursor.close()
        if len(records) == 0:
            return None

        return results[random.randint(0, len(results)) - 1]

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def get_success_results():
    try:
        sqlite_connection = sqlite3.connect('ba_ru_pairs.db')
        cursor = sqlite_connection.cursor()

        sqlite_select_query = '''
        select r.id,ba,ru,c.date from raw_pair r 
        join check_result c 
        on r.id=c.pair_id and c.result=1'''

        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        results = []
        for record in records:
            results.append({'id': record[0], 'ba': record[1], 'ru': record[2],
                            'date': record[3]})

        cursor.close()
        return results

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def get_users():
    try:
        sqlite_connection = sqlite3.connect('ba_ru_pairs.db')
        cursor = sqlite_connection.cursor()

        sqlite_select_query = '''select distinct author from check_result'''

        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        results = []
        for record in records:
            results.append(record[0])

        cursor.close()
        return results

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def get_stat():
    try:
        sqlite_connection = sqlite3.connect('ba_ru_pairs.db')
        cursor = sqlite_connection.cursor()

        result = {}

        sqlite_select_query = '''select count(*) from raw_pair'''
        cursor.execute(sqlite_select_query)
        record = cursor.fetchone()
        uniq_pairs = record[0]
        result["pairs"] = uniq_pairs

        sqlite_select_query = '''select result,count(*) from check_result
group by result'''
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()

        for record in records:
            rt = record[0]
            r_count = record[1]
            if rt == 1:
                result["success"] = r_count
            else:
                result["fail"] = r_count

        return result

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def get_user_stat(author):
    try:
        sqlite_connection = sqlite3.connect('ba_ru_pairs.db')
        cursor = sqlite_connection.cursor()

        sqlite_select_query = '''select count(*) from check_result where author=?'''
        cursor.execute(sqlite_select_query, (author,))
        record = cursor.fetchone()
        return record[0]

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
