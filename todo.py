from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

DATABASE = '/tmp/todo.db'
DEBUG = True
SECRET_KEY = 'development-key'
SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class TodoForm(Form):
    text = StringField('text', validators=[DataRequired()])


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    completed_at = db.Column(db.DateTime)

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "<Todo {}>".format(self.text)


@app.route("/")
def index():
    current_todos = Todo.query.filter(Todo.completed_at == None).all()
    completed_todos = Todo.query.filter(Todo.completed_at != None).all()
    new_todo_form = TodoForm()
    return render_template("index.html",
                           new_todo_form=new_todo_form,
                           todos=current_todos,
                           completed=completed_todos)


@app.route("/add", methods=['POST'])
def add_todo():
    form = TodoForm()
    if form.validate_on_submit():
        todo = Todo(form.text.data)
        db.session.add(todo)
        db.session.commit()
        flash("Your todo was created.")
    else:
        flash("Your todo could not be created.")

    return redirect(url_for('index'))


@app.route("/complete", methods=['POST'])
def complete():
    ids = request.form.getlist('todo')
    for id in ids:
        todo = Todo.query.get(id)
        todo.completed_at = datetime.utcnow()
        db.session.add(todo)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    manager.run()
