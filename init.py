import sqlite3

# Creating users table
conn = sqlite3.connect('database.db')

c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (login TEXT, name TEXT, password TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS diaries (user_id INTEGER, journal_id INTEGER, title TEXT, content TEXT, date DATETIME, description TEXT)")
conn.commit()
conn.close()