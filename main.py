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

def generate_page(page_number):
    page_number = int(page_number)
    #start_page = (page_number*1)+((page_number-1)*5)
    offset_page = (page_number*5)-5
    i = get_user_info()
    user_id = i[0]
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    #c.execute("SELECT *,rowid FROM diaries WHERE rowid BETWEEN "+str(start_page)+" AND "+str(end_page))
    c.execute("SELECT *,rowid FROM diaries WHERE user_id="+str(user_id) + " LIMIT 5 OFFSET " + str(offset_page))
    results = c.fetchall()
    conn.commit()
    conn.close()
    return results

def generate_paging(page_number = 1):
    page_number = int(page_number)
    i = get_user_info()
    user_id = i[0]
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM diaries WHERE user_id='"+str(user_id)+"'")
    results = c.fetchall()
    page = results[0][0]/5
    if page > int(page):
        page += 1
    conn.commit()
    conn.close()
    output = ''
    print('page number: ' + str(page_number))
    if page_number == 1:
        output += '<li class="page-item disabled"><a class="page-link" href="#">Previous</a></li>'
    else:
        output += '<li class="page-item"><a class="page-link" href="/page/'+str(page_number-1)+'">Previous</a></li>'
    index = 1
    while index <= page:
        if index == page_number:
            output += '<li class="page-item active"><a class="page-link" href="/page/'+str(index)+'">'+str(index)+'</a></li>'
        else:
            output += '<li class="page-item"><a class="page-link" href="/page/'+str(index)+'">'+str(index)+'</a></li>'
        index += 1
    if page_number == page:
        output += '<li class="page-item disabled"><a class="page-link" href="#">Next</a></li>'
    else:
        output += '<li class="page-item"><a class="page-link" href="/page/'+str(page_number+1)+'">Next</a></li>'
    return output

# Class bilan yozib chiq
def generate_paging_search(page_number, search):
    page_number = int(page_number)
    i = get_user_info()
    user_id = i[0]
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM diaries WHERE user_id='"+str(user_id)+"' AND content LIKE '%"+str(search)+"%'")
    results = c.fetchall()
    page = results[0][0]/5
    if page > int(page):
        page += 1
    conn.commit()
    conn.close()
    output = ''
    print('page number: ' + str(page_number))
    if page_number == 1:
        output += '<li class="page-item disabled"><a class="page-link" href="#">Previous</a></li>'
    else:
        output += '<li class="page-item"><a class="page-link" href="/search/'+str(page_number-1)+'">Previous</a></li>'
    index = 1
    while index <= page:
        if index == page_number:
            output += '<li class="page-item active"><a class="page-link" href="/search/'+str(index)+'">'+str(index)+'</a></li>'
        else:
            output += '<li class="page-item"><a class="page-link" href="/search/'+str(index)+'">'+str(index)+'</a></li>'
        index += 1
    if page_number == page:
        output += '<li class="page-item disabled"><a class="page-link" href="#">Next</a></li>'
    else:
        output += '<li class="page-item"><a class="page-link" href="/search/'+str(page_number+1)+'">Next</a></li>'
    return output

def generate_page_search(page_number, search):
    page_number = int(page_number)
    offset_page = (page_number*5)-5
    i = get_user_info()
    user_id = i[0]
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT *,rowid FROM diaries WHERE user_id="+str(user_id) + " AND content LIKE '%"+str(search)+"%' LIMIT 5 OFFSET " + str(offset_page))
    results = c.fetchall()
    conn.commit()
    conn.close()
    return results


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

class SearchForm(FlaskForm):
    search = StringField('q',validators=[DataRequired()])
    submit = SubmitField('search')

@app.route('/')
def index_page(page=1):
    print('page is ' + str(page))
    page = int(page)
    if check_auth():
        i = get_user_info()
        name = i[2]
        pagination = generate_paging()
        return render_template('index.html', name=name, results=generate_page(page), pagination=pagination)
    else:
        return redirect('/login')
    
@app.route('/page/<int:page>')
def page_page(page=1):
    print('page is ' + str(page))
    page = int(page)
    if check_auth():
        i = get_user_info()
        name = i[2]
        pagination = generate_paging(page)
        return render_template('index.html', name=name, results=generate_page(page), pagination=pagination)
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
            for word in remove_html(content).split()[0:51]:
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

@app.route('/search', methods=['GET'])
def search_page():
    if check_auth():
        i = get_user_info()
        name = i[2]
        search = request.args.get('q')
        pagination = generate_paging_search(1,search)
        resp = make_response(render_template('index.html', name=name, results=generate_page_search(1, search), pagination=pagination))
        resp.set_cookie('search',search)
        return resp
    else:
        return redirect('/login')

@app.route('/search/<int:id>')
def search_page_page(id):
    if check_auth():
        i = get_user_info()
        name = i[2]
        search = request.cookies.get('search')
        pagination = generate_paging_search(id,search)
        return render_template('index.html', name=name, results=generate_page_search(id, search), pagination=pagination)
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)