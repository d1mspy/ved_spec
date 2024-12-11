import sqlite3
import uuid

# глобальные переменные для подключения к бд
conn = sqlite3.connect('sqlite.db')
c = conn.cursor()


# проверка что таблица существует и ее создание если не существует
def check_table() -> None:
    c.execute('''
        CREATE TABLE IF NOT EXISTS score(
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            player_score INTEGER NOT NULL
        );
    ''')
    conn.commit()



# сохранение очков в бд
def save_score(username: str, score: int) -> None:
    c.execute('''
              INSERT INTO score(id, username, player_score) VALUES(?, ?, ?)
              ''',
              (uuid_as_str(), username, score))
    conn.commit()



# создание уникального id
def uuid_as_str() -> str:
    return str(uuid.uuid4())


# выбор 5 лучших игроков
def get_leaders() -> list:
    c.execute('''
              SELECT username, player_score
              FROM score
              ORDER BY player_score DESC
              LIMIT 5;
              ''')
    conn.commit()
    
    results = c.fetchall()
    
    return results