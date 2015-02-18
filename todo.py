from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3

DATABASE = '/tmp/todo.db'
DEBUG = True
SECRET_KEY = 'development-key'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Gives us a connection to our database. Only one connection per
    request."""
    # getattr lets us get an attribute of an object, or a default
    # g._database would throw an error here if we'd never created it.
    db = getattr(g, '_database', None)
    if db is None:
        db = connect_db()
        # This means we'll get back a dictionary for each row instead of
        # a tuple.
        db.row_factory = sqlite3.Row
        g._database = db
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Lets us query our database and get back a generator instead of a
    cursor."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if one:
        return (rv[0] if rv else None)
    else:
        return rv


@app.route("/")
def index():
    todo_list = query_db("SELECT id, text FROM todo")
    return render_template("index.html",
                           todos=todo_list)


@app.route("/add", methods=['POST'])
def add_todo():
    text = request.form['text']
    get_db().execute("INSERT INTO todo (text) VALUES(?)", [text])
    get_db().commit()
    return redirect(url_for('index'))


@app.route("/complete", methods=['POST'])
def complete():
    ids = request.form.getlist('todo')
    get_db().executemany("DELETE FROM todo WHERE id = ?", ids)
    get_db().commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'])
