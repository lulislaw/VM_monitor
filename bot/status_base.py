import sqlite3


def createdb():
    db = sqlite3.connect('database.db')
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, user_id INTEGER, user_status TEXT, lst_page INTEGER)''')
    db.commit()
    db.close()


def page(user_id):
    db = sqlite3.connect('database.db')
    c = db.cursor()
    c.execute('SELECT lst_page FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    db.close()
    if result:
        return result[0]
    else:
        return None

def update_lst_page(user_id, new_lst_page):
    db = sqlite3.connect('database.db')
    c = db.cursor()
    c.execute('UPDATE users SET user_status = ? WHERE user_id = ?', (new_lst_page, user_id))
    db.commit()
    db.close()


def get_user_status(user_id):
    db = sqlite3.connect('database.db')
    c = db.cursor()
    c.execute('SELECT user_status FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    db.close()
    if result:
        return result[0]
    else:
        return None


import sqlite3

def update_user_status(user_id, new_status):
    db = sqlite3.connect('database.db')
    c = db.cursor()
    c.execute('UPDATE users SET user_status = ? WHERE user_id = ?', (new_status, user_id))
    db.commit()
    db.close()

def add_user(user_id, user_status):
    db = sqlite3.connect('database.db')
    c = db.cursor()

    c.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    if result[0] > 0:
        db.close()
        return
    c.execute('INSERT OR IGNORE INTO users (user_id, user_status, lst_page) VALUES (?, ?, ?)', (user_id, user_status,
                                                                                                0))
    db.commit()
    db.close()