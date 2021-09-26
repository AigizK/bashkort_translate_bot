import sqlite3


def get_bot_users():
    result = []

    try:
        sqlite_connection = sqlite3.connect('bot.session')
        cursor = sqlite_connection.cursor()

        sqlite_select_query = '''select id,hash,username,name from entities'''

        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        for record in records:
            result.append(
                {'id': record[0], 'hash': record[1], 'username': record[2],
                 'name': record[3]})

    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

    return result
