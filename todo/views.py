from datetime import datetime

from flask import render_template, request, redirect, url_for, flash
from .models import Todo
from .forms import TodoForm
from . import app, db

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