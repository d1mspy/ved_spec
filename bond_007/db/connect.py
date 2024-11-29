import sqlite3
import uuid

# глобальные переменные для подключения к бд
conn = sqlite3.connect('sqlite.db')
c = conn.cursor()

# проверка что таблица существует и ее создание если не существует
def check_table() -> None:
    c.execute('''CREATE TABLE IF NOT EXISTS score(
        id text primary key,
        username text,
        player_score int
        );''')
    conn.commit()

# сохранение очков в бд
def save_score(score) -> None:
    c.execute('''INSERT INTO score(id, player_score) VALUES(?, ?)''', (uuid_as_str(), score))
    conn.commit()

# создание уникального id
def uuid_as_str() -> None:
    return str(uuid.uuid4())