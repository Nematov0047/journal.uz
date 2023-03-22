import sqlite3
from flask import session
from flask_session import Session
from flask import redirect
def check_login(login):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT login FROM users WHERE login="'+login+'"')
    answers = c.fetchall()
    conn.commit()
    conn.close()

    if len(answers) > 0:
        return True
    else:
        return False
    
def add_login(t):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO users VALUES (?,?,?)',t)
    conn.commit()
    conn.close()

def login(login, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE login="'+login+'"')
    answers = c.fetchall()
    conn.commit()
    conn.close()
    if len(answers) == 0:
        return False
    else:
        if answers[0][0] == login and answers[0][2] == password:
            return True
        else:
            return False
        
def check_auth():
    if not session.get('login') or not session.get('password'):
        return False
    if login(session['login'], session['password']):
        return True
    else:
        return False