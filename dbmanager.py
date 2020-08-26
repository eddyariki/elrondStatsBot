import sqlite3
from sqlite3 import Error
from datetime import datetime


class DBManager:
    def __init__(self, dbname):
        try:
            self.connection = sqlite3.connect(dbname, check_same_thread=False)
            self.dbname = dbname
            print("Connection to SQLite DB was successful")
            self.cursor = self.connection.cursor()
            self.cursor.execute("CREATE TABLE IF NOT EXISTS chat (id integer)")
            self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS chat_id on chat (id)")
            self.connection.commit()
            self.connection.close()
            print("Connection  to SQLite DB was closed")
        except Error as e:
            print(e)

    def get_ids(self):
        try:
            self.connection = sqlite3.connect(self.dbname, check_same_thread=False)
            print("Connection to SQLite DB was successful")
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT * FROM chat")
            d = self.cursor.fetchall()
            self.connection.close()
            print("Connection  to SQLite DB was closed")
            return d
        except Error as e:
            print(e)

    def insert(self, id):
        try:
            self.connection = sqlite3.connect(self.dbname,check_same_thread=False)
            print("Connection to SQLite DB was successful")
            self.cursor = self.connection.cursor()
            self.cursor.execute("INSERT OR IGNORE INTO  chat (id) VALUES (?)", (id,))
            self.connection.commit()
            self.connection.close()
            print("Insertion to SQLite DB was successful")
            print("Connection  to SQLite DB was closed")
        except Error as e:
            print(e)

    def delete(self, id):
        try:
            self.connection = sqlite3.connect(self.dbname,check_same_thread=False)
            print("Connection to SQLite DB was successful")
            self.cursor = self.connection.cursor()
            self.cursor.execute("DELETE FROM chat WHERE id=?", (id,))
            self.connection.commit()
            self.connection.close()
            print(f"Deletion of {id} from SQLite DB was successful")
            print("Connection  to SQLite DB was closed")
        except Error as e:
            print(e)
    
    def backup(self, location):
        try:
            self.connection = sqlite3.connect(self.dbname, check_same_thread=False)
            print("Connection to SQLite DB was successful")
            now = datetime.now()
            bck = sqlite3.connect(f"{location}/db_{now.strftime('%m%d%H%Y')}.db")
            with bck:
                self.connection.backup(bck, pages=1, progress=None)
            print("Backup saved")
            self.connection.close()
            print("Connection  to SQLite DB was closed")
        except Error as e:
            print(e)