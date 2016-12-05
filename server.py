from flask import Flask, render_template, session, flash, request, redirect, url_for
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import os
app = Flask(__name__)
app.secret_key = "fadf34trr32resgfb=Rxlxs80gaeaDfdz"
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app, 'thebigwalldb')


@app.route('/', methods=['GET'])
def index():
    if id is not session:
        session.clear()
    else:
        return redirect('wall')

    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():

    password = request.form['password']
    pw_encrypted = bcrypt.generate_password_hash(password)

    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"

    data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': pw_encrypted
            }

    mysql.query_db(query, data)

    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session['email'] = request.form['email']
    session['password'] = request.form['password']

    query = "SELECT * FROM users WHERE email = :email LIMIT 1"
    data = { 'email': session['email'] }

    user = mysql.query_db(query, data)
    if bcrypt.check_password_hash(user[0]['password'], session['password']):
        session['id'] = id
        return redirect('/wall/', id=id)
    else:
        flash ("Your entred invalid credentials, please try again!")

    return redirect('/')


@app.route('/wall/<id>', methods=['GET', 'POST'])
def wall(id):
    flash ("You have successfully logged in!")

    query = "SELECT * FROM users WHERE id = :id LIMIT 1"
    data = { 'id': id }

    user = mysql.query_db(query, data)
    print user
    return render_template('wall.html', users = user[0], id=id)


@app.route('/post', methods=['POST'])
def make_post():

    query = "INSERT INTO messages (messages.messages) VALUES (:post_submit)"
    data = { 'post_submit': request.form['post_submit'] }

    post_message = mysql.query_db(query, data)
    print post_message

    return redirect('/wall', post_message=post_message)



@app.route('/logout')
def logout():
    session.clear() # Function that logs user out!
    flash('You were successfully logged out!')

    return redirect('/')

# INCLUDE flask_static_files_cache_invalidator
# created by https://gist.github.com/Ostrovski/f16779933ceee3a9d181
@app.url_defaults
def hashed_url_for_static_file(endpoint, values):
    if 'static' == endpoint or endpoint.endswith('.static'):
        filename = values.get('filename')
        if filename:
            if '.' in endpoint:  # has higher priority
                blueprint = endpoint.rsplit('.', 1)[0]
            else:
                blueprint = request.blueprint  # can be None too

            if blueprint:
                static_folder = app.blueprints[blueprint].static_folder
            else:
                static_folder = app.static_folder

            param_name = 'h'
            while param_name in values:
                param_name = '_' + param_name
            values[param_name] = static_file_hash(os.path.join(static_folder, filename))

def static_file_hash(filename):
  return int(os.stat(filename).st_mtime) # or app.config['last_build_timestamp'] or md5(filename) or etc...
# END flask_static_files_cache_invalidator


app.run(debug=True)
