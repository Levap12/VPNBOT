import sqlite3
from datetime import datetime

class LogsDB:
    def __init__(self, db_name="bot_logs.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        Создает таблицу logs, если она еще не существует.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def log_action(self, user_id, username, action):
        """
        Добавляет запись в таблицу logs.
        :param user_id: ID пользователя
        :param username: Имя пользователя
        :param action: Действие пользователя
        """
        self.cursor.execute(
            "INSERT INTO logs (user_id, username, action) VALUES (?, ?, ?)",
            (user_id, username, action)
        )
        self.conn.commit()

    def get_user_logs(self, user_id):
        """
        Возвращает все логи пользователя по его ID.
        :param user_id: ID пользователя
        :return: Список логов
        """
        self.cursor.execute("SELECT action, timestamp FROM logs WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        self.conn.close()

# Пример использования
if __name__ == "__main__":
    db = LogsDB()

    # Добавление логов
    db.log_action(user_id=123456, username="test_user", action="menu_button_1")
    db.log_action(user_id=123456, username="test_user", action="menu_button_2")

    # Получение логов пользователя
    logs = db.get_user_logs(user_id=123456)
    for action, timestamp in logs:
        print(f"{timestamp} - {action}")

    db.close()
