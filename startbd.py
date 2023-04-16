import sqlite3
import config


def main():
    connect = sqlite3.connect('telegram_base.db')
    cursor = connect.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS all_profiles(
    id INTEGER PRIMARY KEY,
    profile_id INTEGER,
    profile_username TEXT,
    activity TEXT,
    super_user TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS all_tokens(
    id_token INTEGER PRIMARY KEY,
    token_num TEXT,
    activity TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS all_ai_tokens(
    id_token INTEGER PRIMARY KEY,
    token_num TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS all_questions(
    id INTEGER PRIMARY KEY,
    id_username TEXT,
    question TEXT
    )
    ''')

    have_keys = cursor.execute('SELECT * FROM all_tokens').fetchall()

    if not have_keys:
        for key in config.key_for_bot:
            data = (key, 'false')
            cursor.execute('INSERT INTO all_tokens(token_num, activity) VALUES(?,?)', data)

    print(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ").fetchall())
    print(cursor.execute("SELECT * FROM all_profiles").fetchall())
    print(cursor.execute("SELECT * FROM all_tokens").fetchall())
    connect.commit()
    connect.close()


if __name__ == '__main__':
    main()
    print('The database was created successfully ')
