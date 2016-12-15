from flask import Flask, render_template, session, flash, request, redirect, url_for
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import os
import re
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

    # session['email'] = request.form['email']
    # session['password'] = request.form['password']
    #
    # query = "SELECT * FROM users WHERE email = :email LIMIT 1"
    # data = { 'email': session['email'] }
    #
    # session['id'] = user[0]['id']
    # session['first_name'] = user[0]['first_name']

    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session['email'] = request.form['email']
    session['password'] = request.form['password']

    query = "SELECT * FROM users WHERE email = :email LIMIT 1"
    data = { 'email': session['email'] }
    user = mysql.query_db(query, data)
    if bcrypt.check_password_hash(user[0]['password'], session['password']):
        session['id'] = user[0]['id']
        session['first_name'] = user[0]['first_name']
        # print "Set session", session['first_name']
        # Double check the above!
        return redirect('/wall')
    else:
        flash ("Your entred invalid credentials, please try again!")

    return redirect('/')

@app.route('/post', methods=['POST'])
def make_post():

    query = "INSERT INTO messages (messages, created_at, updated_at, user_id) VALUES (:post_submit, NOW(), NOW(), :session_id)"
    data = {
            'post_submit': request.form['wall_post'],
            'session_id':session['id']
            }

    post_message = mysql.query_db(query, data)

    return redirect('/wall')

@app.route('/delete/<post_id>', methods=['POST'])
def delete_post(post_id):

    query = "DELETE FROM messages, user_id LEFT JOIN users WHERE messages.id = :post_id"
    data = { 'user_id': session['id'], 'post_id': post_id }

    delete_message = mysql.query_db(query, data)

    return redirect('/wall')

@app.route('/comments', methods=['POST'])
def make_comment():

    query = "INSERT INTO comments (comments, created_at, updated_at, message_id, user_id) VALUES (:comment, NOW(), NOW(), :message_id, :user_id)"
    data = {
            'comment': request.form['comment_post'],
            'message_id': request.form['hidden'],
            'user_id':session['id']
            }

    mysql.query_db(query, data)

    return redirect('/wall')

@app.route('/delete/<comment_id>', methods=['POST'])
def delete_comment(comment_id):

    query = "DELETE FROM comments WHERE comments.id = :comment_id LEFT JOIN users ON comments.user_id = users.id"
    data = { 'user_id': session['id'], 'comment_id': comment_id }

    delete_comment = mysql.query_db(query, data)
    print "Deleting route working!"
    return redirect('/wall')

@app.route('/wall')
def show_post():

    query = "SELECT messages.messages, messages.id, messages.created_at, users.first_name, users.last_name FROM messages JOIN users ON messages.user_id = users.id  ORDER BY created_at DESC"

    messages = mysql.query_db(query)

    query = "SELECT comments.comments, comments.id, comments.created_at, users.first_name, users.last_name , comments.message_id FROM comments LEFT JOIN users ON comments.user_id = users.id  ORDER BY created_at ASC"

    comments = mysql.query_db(query)
    # print comments

    query = "SELECT first_name FROM users WHERE ID = :session_id"
    data = {
            'session_id': session['id']
            }

    first_name = mysql.query_db(query, data)

    return render_template('wall.html', messages=messages, comments=comments, name=first_name)


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

#
# @app.route('/wall')
# def wall():
#     flash ("You have successfully logged in!")
#
#     query = "SELECT * FROM users WHERE id = :id LIMIT 1"
#     data = { 'id': id }
#
#     user = mysql.query_db(query, data)
#     print user
#     return render_template('wall.html', users = user)
