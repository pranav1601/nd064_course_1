import sqlite3
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging

# Function to get a database connection.
# This function connects to database with the name `database.db`
connection_count=0

def get_db_connection():
    connection = sqlite3.connect('database.db')
    global connection_count
    connection_count+=1
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

@app.route('/healthz')
def health():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    return response

@app.route('/metrics')
def metrics():
    global connection_count
    connection = get_db_connection()
    posts = connection.cursor().execute('SELECT COUNT(id) FROM posts').fetchone()
    # print(posts[0])
    connection.close()
    response = app.response_class(
            response=json.dumps({"data":{"db_connection_count": connection_count, "post_count": posts[0]}}),
            status=200,
            mimetype='application/json'
    )

    return response

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        sys.stderr.write('Article does not exist')
        print('Article does not exist')
        app.logger.info('Article does not exist!')
        

        return render_template('404.html'), 404
    else:
        # for i in post:
        #     print(i[2])
        sys.stdout.write('Article- '+str(post[2])+' retrieved')
        print('Article- '+str(post[2])+' retrieved')

        app.logger.info('Article- '+str(post[2])+' retrieved')

        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    sys.stdout.write('about page retrieved')
    print('about page retrieved')
    app.logger.info('About page retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            sys.stdout.write('Article- '+title+' retrieved')
            print('Article- '+title+' retrieved')
            app.logger.info('Article '+title+' created')

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',filename='app.log',level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')


    app.run(host='0.0.0.0', port='3111')
