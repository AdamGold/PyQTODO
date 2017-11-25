import sqlite3
NOTES_TABLE = 'notes'
class Database(object):
    db = None
    cursor = None
    table = ''
    @staticmethod
    def connect_to_db(fn):
        try:
            Database.db = sqlite3.connect(fn, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            Database.cursor = Database.db.cursor()
        except:
            print("Can not connect to database")
    
    @staticmethod
    def init_db(table_name):
        Database.table = table_name
        Database.db.execute('''CREATE TABLE IF NOT EXISTS
            {}(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            priority INTEGER NOT NULL DEFAULT 1,
            due_in DATETIME,
            completed INTEGER NOT NULL DEFAULT 0);
            '''.format(Database.table))
