from flask import Flask
from flask import redirect
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask import request
from flask import flash
import sqlite3
from flask import make_response
from datetime import date
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField
import re

app = Flask(__name__)
ckeditor = CKEditor(app)

app.config['SECRET_KEY'] = '51efw@#651%$658efd-09+1'

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
    if request.cookies.get('login') and request.cookies.get('password'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM USERS WHERE login='"+request.cookies.get('login')+"'")
        answers = c.fetchall()
        conn.commit()
        conn.close()

        if len(answers) == 1:
            if answers[0][2] == request.cookies.get('password'):
                return True
            else:
                return False
        else:
            return False
        
def get_user_info():
    login = request.cookies.get('login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM USERS WHERE login='"+login+"'")
    answers = c.fetchall()
    conn.commit()
    conn.close()
    if len(answers) == 1:
        return answers[0]
    else:
        return False
    
def results():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    id = c.execute("SELECT rowid FROM users WHERE login='"+request.cookies.get('login')+"'")
    user_id = c.fetchall()[0][0]
    journals = c.execute("SELECT *, rowid FROM diaries WHERE user_id='"+str(user_id)+"'")
    results = c.fetchall()
    conn.commit()
    conn.close()
    return results
def remove_html(string):
    pattern = re.compile('<.*?>')
    return re.sub(pattern, ' ', string).strip()

class LoginForm(FlaskForm):
    login = StringField('login',validators=[DataRequired(), Length(5)])
    password = PasswordField('password', validators=[DataRequired(), Length(8)])
    submit = SubmitField('Log In') 

class RegisterForm(FlaskForm):
    login = StringField('login',validators=[DataRequired(), Length(5)])
    password = PasswordField('password', validators=[DataRequired(), Length(8)])
    name = StringField('name', validators=[DataRequired(),Length(3)])
    submit = SubmitField('Register')

class WriteForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    journal = SelectField('journal',choices=['Default'], validators=[DataRequired()])
    #content = TextAreaField('content', validators=[DataRequired()])
    content = CKEditorField('content', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')
def index_page():
    if check_auth():
        i = get_user_info()
        name = i[2]
        return render_template('index.html', name=name, results=results())
    else:
        return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        if login(form.login.data, form.password.data):
            resp = make_response(redirect('/'))
            resp.set_cookie('login', form.login.data)
            resp.set_cookie('password', form.password.data)
            flash('Success')
            return resp
        else:
            flash('Failure')
    return render_template('login.html', form=form)
@app.route('/register')
def register_page():
    form = RegisterForm()
    return render_template('register.html', form=form)

@app.route('/register/add', methods=['GET','POST'])
def register_add_page():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.name.data)
        print(form.login.data)
        print(form.password.data)
        if check_login(form.login.data):
            flash('Login already exists')
            return redirect('/register')
        else:
            add_login((form.login.data, form.name.data, form.password.data))
            flash('successfully Registered')
            return redirect('/login')
    else:
        flash('Please fill out all fields')
        return redirect('/register')
    
@app.route('/logout')
def logout_page():
    resp = make_response(redirect('/login'))
    resp.set_cookie('login','',expires=0)
    resp.set_cookie('password','',expires=0)
    flash('Logged out')
    return resp

@app.route('/write')
def write_page():
    if check_auth():
        i = get_user_info()
        name = i[2]
        form = WriteForm()
        return render_template('write.html', name=name, form=form)
    else:
        return redirect('/login')
@app.route('/write/add', methods=['GET','POST'])
def write_add_page():
    if check_auth():
        i = get_user_info()
        name = i[2]
        form = WriteForm()
        if form.validate_on_submit():
            user_id = i[0]
            journal_id = 1
            title = form.title.data
            content = form.content.data
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            date_today = date.today()
            description = ''
            for word in remove_html(content).split(' ')[0:51]:
                description += word + ' '
            description += '...'
            c.execute("INSERT INTO diaries VALUES (?,?,?,?,?,?)",(user_id, journal_id, title, content, date_today, description))
            conn.commit()
            conn.close()
            flash('Successfully Added')
            return redirect('/')
        else:
            flash('Please fill out all fields')
            return redirect('/write')
    else:
        return redirect('/login')

@app.route('/read/<id>')
def read_page(id):
    if check_auth():
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT *, rowid FROM diaries WHERE rowid='"+id+"'")
        result = c.fetchall()[0]
        conn.commit()
        conn.close()
        i = get_user_info()
        name = i[2]
        if result[0] == i[0]:
            return render_template('read.html',result=result, name=name)
        else:
            flash("Access forbidden")
            # return render_template('index.html',name=name,results=results())
            return redirect('/')
    else:
        redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)