from flask import render_template, flash, redirect, url_for, request
from app import app, db
# Forms
from app.main.forms import NewComponentForm
# Models
from app.models import User, Project, TaskList, Task
# Authentication
from flask_login import current_user, login_required
# URL Parse
from werkzeug.urls import url_parse
# Last Seen
# from datetime import datetime

# Project Directory

@app.route('/')
@app.route('/index')
@login_required
def index() :
    projects = current_user.projects.all()
    return render_template('index.html', title = "Home", projects = projects)

# Project Main

@app.route('/project/<int:project_id>')
@login_required
def project(project_id) :
    if current_user.is_in_project(project_id) :
        project = Project.query.filter_by(id = project_id).first_or_404()
        return render_template('project.html', project = project)
    else :
        flash("You cannot access this project.")
        return redirect(url_for('index'))

# Project

@app.route('/new/project', methods = ["GET", "POST"])
@login_required
def new_project() :
    form = NewComponentForm()
    if form.validate_on_submit() :
        project = Project(name = form.name.data, description = form.description.data)
        db.session.add(project)
        project.add_to_project(current_user)
        db.session.commit()
        flash("Project - \"{}\" created successfully!".format(project.name))
        return redirect(url_for('index'))
    return render_template('new_project.html', form = form)

@app.route('/edit/project/<int:project_id>', methods = ["GET", "POST"])
@login_required
def edit_project(project_id) :
    form = NewComponentForm()
    if current_user.is_in_project(project_id) :
        project = Project.query.filter_by(id = project_id).first_or_404()
        if form.validate_on_submit() :
            project.name = form.name.data
            project.description = form.description.data
            db.session.commit()
            flash("Project - \"{}\" changed successfully!".format(project.name))
            return redirect(url_for('project', project_id = project.id))
        else :
            form.name.data = project.name
            form.description.data = project.description
        return render_template('edit_project.html', form = form, project_id = project_id)
    else :
        flash("You cannot edit this project.")
        return redirect(url_for('index'))

@app.route('/delete/project/<int:project_id>', methods = ["GET", "POST"])
@login_required
def delete_project(project_id) :
    # Check if current user is in the project
    if current_user.is_in_project(project_id) :
        project = Project.query.filter_by(id = project_id).first_or_404()
        flash("Deleted Project - \"{}\"".format(project.name))
        db.session.delete(project)
        db.session.commit()
    else :
        flash("You cannot delete this project.")
    return redirect(url_for('index'))

# TaskList

@app.route('/new/tasklist/<int:project_id>', methods = ["GET", "POST"])
@login_required
def new_tasklist(project_id) :
    form = NewComponentForm()
    if form.validate_on_submit() :
        # Check if current user is in the project
        if current_user.is_in_project(project_id) :
            tasklist = TaskList(name = form.name.data, description = form.description.data)
            db.session.add(tasklist)
            project = Project.query.filter_by(id = project_id).first_or_404()
            project.tasklists.append(tasklist)
            db.session.commit()
            flash("Task List - \"{}\" for Project - \"{}\" created successfully!".format(tasklist.name, project.name))
            return redirect(url_for('project', project_id = project.id))
        else :
            flash("You cannot add task lists to this project.")
            return redirect(url_for('index'))
    return render_template('new_tasklist.html', form = form)

@app.route('/edit/project/<int:project_id>/tasklist/<int:tasklist_id>', methods = ["GET", "POST"])
@login_required
def edit_tasklist(project_id, tasklist_id) :
    form = NewComponentForm()
    tasklist = TaskList.query.filter_by(id = tasklist_id).first_or_404()
    # Check if current user and the task list is in the project 
    if current_user.is_in_project(project_id) and tasklist.project_id == project_id :
        if form.validate_on_submit() :
            tasklist.name = form.name.data
            tasklist.description = form.description.data
            db.session.commit()
            flash("Task List - \"{}\" changed successfully!".format(tasklist.name))
            return redirect(url_for('project', project_id = project_id))
        else :
            form.name.data = tasklist.name
            form.description.data = tasklist.description
        return render_template('edit_tasklist.html', form = form, project_id = project_id, tasklist_id = tasklist_id)
    else :
        flash("You cannot edit the task list for this project.")
        return redirect(url_for('index'))

@app.route('/delete/project/<int:project_id>/tasklist/<int:tasklist_id>', methods = ["GET", "POST"])
@login_required
def delete_tasklist(project_id, tasklist_id) :
    tasklist = TaskList.query.filter_by(id = tasklist_id).first_or_404()
    # Check if current user and the task list is in the project 
    if current_user.is_in_project(project_id) and tasklist.project_id == project_id :
        flash("Deleted Task List - \"{}\"".format(tasklist.name))
        db.session.delete(tasklist)
        db.session.commit()
    else :
        flash("You cannot delete the task list for this project.")
    return redirect(url_for('project', project_id = project_id))

# Task

@app.route('/new/project/<int:project_id>/tasklist/<int:tasklist_id>', methods = ["GET", "POST"])
@login_required
def new_task(project_id, tasklist_id) :
    form = NewComponentForm()
    if form.validate_on_submit() :
        tasklist = TaskList.query.filter_by(id = tasklist_id).first_or_404()
        # Check if current user and the task list is in the project 
        if current_user.is_in_project(project_id) and tasklist.project_id == project_id :
            task = Task(name = form.name.data, description = form.description.data)
            db.session.add(task)
            tasklist.tasks.append(task)
            db.session.commit()
            flash("Task - \"{}\" in Task List - \"{}\"created successfully!".format(task.name, tasklist.name))
            return redirect(url_for('project', project_id = project_id))
        else :
            flash("You cannot add tasks to task lists in this project.")
            return redirect(url_for('index'))
    return render_template('new_task.html', form = form)

@app.route('/edit/project/<int:project_id>/tasklist/<int:tasklist_id>/task/<int:task_id>', methods = ["GET", "POST"])
@login_required
def edit_task(project_id, tasklist_id, task_id) :
    form = NewComponentForm()
    tasklist = TaskList.query.filter_by(id = tasklist_id).first_or_404()
    task = Task.query.filter_by(id = task_id).first_or_404()
    # Check if current user, task list and task is in the project 
    if current_user.is_in_project(project_id) and tasklist.project_id == project_id and task.tasklist_id == tasklist_id :
        if form.validate_on_submit() :
            task.name = form.name.data
            task.description = form.description.data
            db.session.commit()
            flash("Task - \"{}\" changed successfully!".format(task.name))
            return redirect(url_for('project', project_id = project_id))
        else :
            form.name.data = task.name
            form.description.data = task.description
        return render_template('edit_task.html', form = form)
    else :
        flash("You cannot edit the task for this project.")
        return redirect(url_for('index'))

@app.route('/delete/project/<int:project_id>/tasklist/<int:tasklist_id>/task/<int:task_id>', methods = ["GET", "POST"])
@login_required
def delete_task(project_id, tasklist_id, task_id) :
    tasklist = TaskList.query.filter_by(id = tasklist_id).first_or_404()
    task = Task.query.filter_by(id = task_id).first_or_404()
    # Check if current user, task list and task is in the project 
    if current_user.is_in_project(project_id) and tasklist.project_id == project_id and task.tasklist_id == tasklist_id :
        flash("Deleted Task - \"{}\"".format(task.name))
        db.session.delete(task)
        db.session.commit()
    else :
        flash("You cannot delete the task list for this project.")
    return redirect(url_for('project', project_id = project_id))