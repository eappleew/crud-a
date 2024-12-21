from flask import Flask,redirect,render_template
from flask import request,send_file,url_for

import os
import pymysql,datetime


app = Flask(__name__)

db = pymysql.connect(host='localhost',user='root',password='1234',charset='utf8',database='mysql')
cursor = db.cursor(pymysql.cursors.DictCursor)
cursor.execute('CREATE DATABASE IF NOT EXISTS programming;')
db = pymysql.connect(host='localhost',user='root',password='1234',charset='utf8',database='programming')
cursor = db.cursor(pymysql.cursors.DictCursor)
cursor.execute('''
        CREATE TABLE IF NOT EXISTS crud_information (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            readpw VARCHAR(255) NOT NULL,
            file_title VARCHAR(255) NULL,
            file_path VARCHAR(255) NULL);
    ''')
cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_information (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            user_pw VARCHAR(255) NOT NULL,
            user_number VARCHAR(255) NOT NULL,
            user_school VARCHAR(255) NOT NULL,
            user_birthday VARCHAR(255) NOT NULL,
            user_imgtitle VARCHAR(255) NULL,
            user_imgpath VARCHAR(255) NULL);
''')
cursor.execute('SELECT * FROM crud_information;')
value = cursor.fetchall()
info = value


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'file')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

profile = 0
login = 0

def get_info():
    cursor.execute('SELECT * FROM crud_information;')
    return cursor.fetchall()


def add():
    info = get_info()
    add_info=''
    for i in info:
        if i['readpw']:
            add_info += f"<h2><a href='/read/{i['id']}/'>{i['id']}-{i['title']}(비밀글)</a></h2><br>"
        else:
            add_info += f"<h2><a href='/read/{i['id']}/'>{i['id']}-{i['title']}</a></h2><br>"
    return add_info


@app.route('/')
def main():
    return render_template('index.html',add_info=add())


@app.route('/read/<int:id>/',methods=['GET','POST'])
def readpage(id):
    if request.method == 'GET':
        info = get_info()
        for i in info:
            if id == i['id']:
                if i['readpw']:
                    return render_template('readpwcheck.html',id=i['id'])
                else:
                    if i['file_path']:
                        return render_template(f'read.html',title=i['title'],description=i['description'],id=i['id'])
    elif request.method == 'POST':
        checkpw = request.form['readpwcheck']
        info = get_info()
        for i in info:
            if id == i['id']:
                if i['readpw'] == checkpw:
                    return render_template('read.html',title=i['title'],description=i['description'],id=i['id'])
                else:
                    return render_template('readpwcheck.html', id=i['id'],error='비밀 번호가 틀렸습니다.')


@app.route('/create/',methods=['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html')
    elif request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        readpw = request.form['readpw']
        file = request.files['file']
        if file:
            file_title = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_title)
            file.save(file_path)
            cursor.execute('INSERT INTO crud_information (title, description, readpw, file_title, file_path) VALUES (%s, %s, %s, %s, %s)',(title, description, readpw, file_title, file_path))
        else:
            cursor.execute('INSERT INTO crud_information (title, description,readpw) VALUES (%s, %s,%s)',(title, description,readpw))
        db.commit()
        return redirect('/')


@app.route('/delete/<int:id>/')
def delete(id):
    cursor.execute(f'DELETE FROM crud_information WHERE id = {id};')
    db.commit()
    return redirect('/')


@app.route('/update/<int:id>/',methods=['GET','POST'])
def update(id):
    info = get_info()
    for i in info:
        if id == i['id']:
            title = i['title']
            description = i['description']
    if request.method == 'GET':
        return render_template('update.html',id=id,title=title,description=description)
    elif request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        cursor.execute(f'UPDATE crud_information SET title="{title}",description="{description}" WHERE id="{id}";')
        db.commit()
        return redirect('/')


@app.route('/search/',methods=['POST','GET'])
def allsearch():
    searchobject = request.form['object']
    searchtype = request.form.get('searchType')
    if searchtype == 'all':
        cursor.execute(f'SELECT * FROM crud_information WHERE title LIKE "%{searchobject}%" OR description LIKE "%{searchobject}%"')
        info = cursor.fetchall()
    elif searchtype == 'title':
        cursor.execute(f'SELECT * FROM crud_information WHERE title LIKE "%{searchobject}%"')
        info = cursor.fetchall()
    elif searchtype == 'description':
        cursor.execute(f'SELECT * FROM crud_information WHERE description LIKE "%{searchobject}%"')
        info = cursor.fetchall()
    value = ""
    for i in info:
        if i['readpw']:
            value += f"<h2><a href='/read/{i['id']}/'>{i['id']}-{i['title']}(비밀글)</a></h2><br>"
        else:
            value += f"<h2><a href='/read/{i['id']}/'>{i['id']}-{i['title']}</a></h2><br>"
    return render_template('search.html',add_info=value)


@app.route('/download/<int:id>/')
def download(id):
    cursor.execute(f'SELECT file_path,file_title FROM crud_information WHERE id = {id}')
    result = cursor.fetchall()
    if result[0]["file_path"]:
        file_path = result[0]["file_path"]
        file_title = result[0]["file_title"]
        return send_file(file_path,mimetype='application/octet-stream',download_name=f'downloaded_file_{file_title}',as_attachment=True)
    else:
        return render_template('read.html',empty='파일이 존재 하지 않습니다.',id=id)


@app.route('/join/',methods=['GET','POST'])
def join():
    if request.method == 'GET':
        return render_template('join.html')
    elif request.method == 'POST':
        add_id = request.form.get('add_id')
        add_pw = request.form.get('add_pw')
        add_number = request.form.get('number')
        add_school = request.form.get('school')
        add_birthday = request.form.get('birthday')
        cursor.execute('SELECT user_id FROM user_information WHERE user_id = %s', (add_id,))
        result = cursor.fetchone()
        if result:
            return render_template('join.html', error="아이디가 이미 존재 합니다.")
        else:
            cursor.execute('INSERT INTO user_information (user_id,user_pw,user_number,user_school,user_birthday) VALUES (%s,%s,%s,%s,%s)',(add_id,add_pw,add_number,add_school,add_birthday))
            db.commit()
            return render_template('join.html', error="회원가입이 완료 되었습니다.")
	

@app.route('/login/',methods=['GET','POST'])
def login():
    global login
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        user_id = request.form.get('user_id')
        user_pw = request.form.get('user_pw')

        if not user_id or not user_pw:
            return render_template('login.html', error="아이디와 비밀번호를 입력하세요.")
        cursor.execute('SELECT user_pw FROM user_information WHERE user_id = %s', (user_id))
        result = cursor.fetchall()

        if not result:
            return render_template('login.html', error="아이디 또는 비밀번호가 틀렸습니다.")
        db_password = result[0]["user_pw"]

        if db_password == user_pw:
            login = user_id
            return redirect('/profile/')
        else:
            return render_template('login.html', error="아이디 또는 비밀번호가 틀렸습니다.")


@app.route('/find/',methods=['GET','POST'])
def find():
    if request.method == 'GET':
        return render_template('find.html')
    elif request.method == 'POST':
        birthday = request.form["birthday"]
        number = request.form["number"]
        cursor.execute('SELECT user_id,user_pw FROM user_information WHERE user_number = %s AND user_birthday = %s',(number,birthday))
        result = cursor.fetchall()
        if result:
            user_id = result[0]["user_id"]
            user_pw = result[0]["user_pw"]
            return render_template('find_result.html',user_id = user_id , user_pw = user_pw)
        else:
            return render_template('find.html',error='일치하는 계정이 없습니다.')

@app.route('/logout/')
def logout():
    global login
    login = 0
    profile = 0
    return redirect('/profile/')

@app.route('/profile/',methods=['GET','POST'])
def profile():
    if login:
        cursor.execute('SELECT user_number,user_school,user_imgpath FROM user_information WHERE user_id = %s', (login))
        result = cursor.fetchone()
        if result:
            number = result["user_number"]
            school = result["user_school"]
            name = login
            profile = result.get("user_imgpath", "profile_images/default.png")
            if profile:
                return render_template('profile.html',name=name,number=number,school=school,profile=profile)
            else:
                return render_template('profile.html',name=name,number=number,school=school)
        else:
            return render_template('profile.html',name='로그인이 필요합니다.')
    else:
        return render_template('profile.html',name='로그인이 필요합니다.')



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROFILE_IMAGE_FOLDER = os.path.join(BASE_DIR, 'static/profile_images')
os.makedirs(PROFILE_IMAGE_FOLDER, exist_ok=True)
app.config['PROFILE_IMAGE_FOLDER'] = PROFILE_IMAGE_FOLDER



@app.route('/edit/',methods=['GET','POST'])
def edit():
    if request.method == 'GET' and login:
        cursor.execute('SELECT user_number,user_school,user_birthday FROM user_information WHERE user_id = %s', (login))
        result = cursor.fetchone()
        if result:
            number = result["user_number"]
            school = result["user_school"]
            name = login
            return render_template('edit.html',name=name,number=number,school=school)
        else:
            return render_template('profile.html',name='로그인이 필요합니다.')
    elif request.method == 'POST':
        name = login
        number = request.form["number"]
        school = request.form["school"]
        file = request.files['img_file']
        if file:
            file_title = file.filename
            file_path = os.path.join(app.config['PROFILE_IMAGE_FOLDER'], file_title)
            file.save(file_path)
            db_file_path = f"profile_images/{file_title}"
            profile = db_file_path
            cursor.execute('UPDATE user_information SET user_number = %s,user_school = %s,user_imgtitle = %s,user_imgpath = %s WHERE user_id = %s',(number,school,file_title,db_file_path,login))
            db.commit()
            return redirect('/profile/')
        else:
            cursor.execute('UPDATE user_information SET user_number = %s,user_school = %s WHERE user_id = %s',(number,school,login))
            db.commit()
            return redirect('/profile/')


@app.route('/user_search/',methods=['GET','POST'])
def user_search():
    searchobject = request.form['user_id']
    cursor.execute('SELECT user_number, user_school, user_imgtitle FROM user_information WHERE user_id = %s', (searchobject,))
    result = cursor.fetchone()

    if not result:
        return render_template('profile.html', error='해당 아이디 유저가 존재하지 않습니다.')
        
    user_number = result["user_number"]
    user_school = result["user_school"]
    file_title = result["user_imgtitle"]
    db_file_path = f"profile_images/{file_title}"
    profile = db_file_path

    return render_template('use_search.html', number=user_number, school=user_school, name=searchobject, profile=profile)

app.run(port=8080,debug=True)
