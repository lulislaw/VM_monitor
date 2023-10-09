import sqlite3

def create_base():
    db = sqlite3.connect("status_base.db")
    cur = db.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,  username TEXT, user_id INTEGER)
    
    '''
    cur.execute(query)
    db.commit()
    db.close()

