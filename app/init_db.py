import sqlite3


if __name__ == '__main__':
    try:
        sqlite_connection = sqlite3.connect('ba_ru_pairs.db')
        cursor = sqlite_connection.cursor()

        sql='''create table IF NOT EXISTS raw_pair(
        id INTEGER PRIMARY KEY,
        ba TEXT NOT NULL,
        ru TEXT NOT NULL
        )
        '''
        cursor.execute(sql)
        sqlite_connection.commit()

        sql = '''create table IF NOT EXISTS check_result(
                id INTEGER PRIMARY KEY,
                pair_id INTEGER,
                result INTEGER,
                author TEXT,
                date TEXT
                )
                '''
        cursor.execute(sql)
        sqlite_connection.commit()

        sql = ("CREATE INDEX IF NOT EXISTS index_pair_id ON check_result (pair_id);")
        cursor.execute(sql)
        sqlite_connection.commit()

        with open("files/33.ba","rt") as bf:
            with open("files/33.ru", "rt") as rf:
                bash_lines=bf.readlines()
                rus_lines = rf.readlines()

                if len(bash_lines)!=len(rus_lines):
                    raise Exception("Different lenght")
                print("Lines:", len(bash_lines))

                i=0
                while i<len(bash_lines):
                    sql='insert into raw_pair(ba,ru) values(?,?)'
                    cursor.execute(sql, (bash_lines[i],rus_lines[i]))
                    i+=1
                sqlite_connection.commit()
                cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")