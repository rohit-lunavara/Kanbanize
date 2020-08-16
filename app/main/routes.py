from flask import render_template, flash, redirect, url_for, request
from app import app, db
# Forms
from app.main.forms import NewComponentForm, EditTaskForm, NewTaskLogForm
# Models
from app.models import User, Project, TaskList, Task, TaskLog
# Authentication
from flask_login import current_user, login_required
# URL Parse
from werkzeug.urls import url_parse
# Task Log
from datetime import timedelta

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
    project = Project.query.filter_by(id = project_id).first_or_404()
    if current_user.is_in_project(project_id) :
        if form.validate_on_submit() :
            project.name = form.name.data
            project.description = form.description.data
            db.session.commit()
            flash("Project - \"{}\" changed successfully!".format(project.name))
            return redirect(url_for('project', project_id = project.id))
        else :
            form.name.data = project.name
            form.description.data = project.description
        return render_template('edit_project.html', form = form, project_name = project.name, project_id = project_id, project = project)
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
    project = Project.query.filter_by(id = project_id).first_or_404()
    if form.validate_on_submit() :
        # Check if current user is in the project
        if current_user.is_in_project(project_id) :
            tasklist = TaskList(name = form.name.data, description = form.description.data)
            db.session.add(tasklist)
            project.tasklists.append(tasklist)
            db.session.commit()
            flash("Task List - \"{}\" created successfully!".format(tasklist.name, project.name))
            return redirect(url_for('project', project_id = project.id))
        else :
            flash("You cannot add task lists to this project.")
            return redirect(url_for('index'))
    return render_template('new_tasklist.html', form = form, project_id = project_id, project_name = project.name)

@app.route('/edit/project/<int:project_id>/tasklist/<int:tasklist_id>', methods = ["GET", "POST"])
@login_required
def edit_tasklist(project_id, tasklist_id) :
    form = NewComponentForm()
    project = Project.query.filter_by(id = project_id).first_or_404()
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
        return render_template('edit_tasklist.html', form = form, project_id = project_id, tasklist_id = tasklist_id, project_name = project.name, tasklist_name = tasklist.name, tasklist = tasklist)
    else :
        flash("You cannot edit task lists for this project.")
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
        flash("You cannot delete task lists from this project.")
    return redirect(url_for('project', project_id = project_id))

# Task

@app.route('/new/project/<int:project_id>/tasklist/<int:tasklist_id>', methods = ["GET", "POST"])
@login_required
def new_task(project_id, tasklist_id) :
    form = NewComponentForm()
    project = Project.query.filter_by(id = project_id).first_or_404()
    tasklist = TaskList.query.filter_by(id = tasklist_id).first_or_404()
    if form.validate_on_submit() :
        # Check if current user and the task list is in the project 
        if current_user.is_in_project(project_id) and tasklist.project_id == project_id :
            task = Task(name = form.name.data, description = form.description.data)
            db.session.add(task)
            tasklist.tasks.append(task)
            db.session.commit()
            flash("Task - \"{}\" created successfully!".format(task.name))
            return redirect(url_for('project', project_id = project_id, ))
        else :
            flash("You cannot add tasks to this project.")
            return redirect(url_for('index'))
    return render_template('new_task.html', form = form, project_id = project_id, tasklist_id = tasklist_id, project_name = project.name, tasklist_name = tasklist.name)

@app.route('/edit/project/<int:project_id>/tasklist/<int:tasklist_id>/task/<int:task_id>', methods = ["GET", "POST"])
@login_required
def edit_task(project_id, tasklist_id, task_id) :
    form = EditTaskForm()
    project = Project.query.filter_by(id = project_id).first_or_404()
    tasklist = TaskList.query.filter_by(id = tasklist_id).first_or_404()
    task = Task.query.filter_by(id = task_id).first_or_404()
    form.tasklists.choices = [ (ele.id, ele.name) for ele in project.tasklists ]
    # Check if current user, task list and task is in the project 
    if current_user.is_in_project(project_id) and tasklist.project_id == project_id and task.tasklist_id == tasklist_id :
        if form.validate_on_submit() :
            new_tasklist = TaskList.query.filter_by(id = form.tasklists.data).first_or_404()
            # Check if new task list is in the project
            if new_tasklist.project_id != project_id :
                flash("You cannot move the task to this task list.")
                return redirect(url_for('edit_task', project_id = project_id, tasklist_id = tasklist_id, task_id = task_id))
            else :
                task.name = form.name.data
                task.description = form.description.data
                task.is_complete = form.is_complete.data
                task.tasklist_id = new_tasklist.id
                db.session.commit()
                flash("Task - \"{}\" changed successfully!".format(task.name))
                return redirect(url_for('project', project_id = project_id))
        else :
            form.name.data = task.name
            form.description.data = task.description
            form.is_complete.data = task.is_complete
        return render_template('edit_task.html', form = form, project_id = project_id, tasklist_id = tasklist_id, task_id = task_id, project_name = project.name, tasklist_name = tasklist.name, task = task)
    else :
        flash("You cannot edit tasks for this project.")
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
        flash("You cannot delete task lists from this project.")
    return redirect(url_for('project', project_id = project_id))

# TaskLog

@app.route('/new/project/<int:project_id>/tasklist/<int:tasklist_id>/task/<int:task_id>', methods = ["GET", "POST"])
@login_required
def new_tasklog(project_id, tasklist_id, task_id) :
    form = NewTaskLogForm()
    project = Project.query.filter_by(id = project_id).first_or_404()
    tasklist = TaskList.query.filter_by(id = tasklist_id).first_or_404()
    task = Task.query.filter_by(id = task_id).first_or_404()
    if form.validate_on_submit() :
        # Check if current user, the task list and the task is in the project
        if current_user.is_in_project(project_id) and tasklist.project_id == project_id and task.tasklist_id == tasklist_id :
            minutesTimezoneOffset = timedelta(minutes = int(form.minutesTimezoneOffset.data))
            start_time = form.start_time.data - minutesTimezoneOffset
            end_time = form.end_time.data - minutesTimezoneOffset
            time_diff = end_time - start_time
            # Check if end time is greater than start time
            if time_diff.total_seconds() <= 0 :
                flash("Task end time cannot be earlier than start time")
                return redirect(url_for('new_tasklog', project_id = project_id, tasklist_id = tasklist_id, task_id = task_id))
            else :
                tasklog = TaskLog(note = form.note.data, start_time = start_time, end_time = end_time)
                db.session.add(tasklog)
                task.durations.append(tasklog)
                db.session.commit()
                flash("Task Log - \"{}\" created successfully!".format(tasklog.note))
                return redirect(url_for('edit_task', project_id = project.id, tasklist_id = tasklist_id, task_id = task_id))
        else :
            flash("You cannot add task logs to this project.")
            return (url_for('index'))
    return render_template('new_tasklog.html', form = form, project_id = project.id, tasklist_id = tasklist_id, task_id = task_id, project_name = project.name, tasklist_name = tasklist.name, task_name = task.name)

@app.route('/edit/project/<int:project_id>/tasklist/<int:tasklist_id>/task/<int:task_id>/tasklog/<int:tasklog_id>', methods = ["GET", "POST"])
@login_required
def edit_tasklog(project_id, tasklist_id, task_id, tasklog_id) :
    form = NewTaskLogForm()
    project = Project.query.filter_by(id = project_id).first_or_404()
    tasklist = TaskList.query.filter_by(id = tasklist_id).first_or_404()
    task = Task.query.filter_by(id = task_id).first_or_404()
    tasklog = TaskLog.query.filter_by(id = tasklog_id).first_or_404()
    # Check if current user, task list, task and task log is in the project 
    if current_user.is_in_project(project_id) and tasklist.project_id == project_id and task.tasklist_id == tasklist_id and tasklog.task_id == task_id :
        if form.validate_on_submit() :
            minutesTimezoneOffset = timedelta(minutes = int(form.minutesTimezoneOffset.data))
            start_time = form.start_time.data - minutesTimezoneOffset
            end_time = form.end_time.data - minutesTimezoneOffset
            time_diff = end_time - start_time
            # Check if end time is greater than start time
            if time_diff.total_seconds() <= 0 :
                flash("Task end time cannot be earlier than start time")
                return redirect(url_for('edit_task', project_id = project_id, tasklist_id = tasklist_id, task_id = task_id))
            else :
                tasklog.note = form.note.data
                tasklog.start_time = start_time
                tasklog.end_time = end_time
                db.session.commit()
                flash("Task Log - \"{}\" changed successfully!".format(tasklog.note))
                return redirect(url_for('edit_task', project_id = project_id, tasklist_id = tasklist_id, task_id = task_id))
        else :
            form.note.data = tasklog.note
            form.start_time.data = tasklog.start_time
            form.end_time.data = tasklog.end_time
        return render_template('edit_tasklog.html', form = form, project_id = project_id, tasklist_id = tasklist_id, task_id = task_id, tasklog_id = tasklog_id, project_name = project.name, tasklist_name = tasklist.name, task_name = task.name, tasklog_name = tasklog.note)
    else :
        flash("You cannot edit task logs for this project.")
        return redirect(url_for('index'))

@app.route('/delete/project/<int:project_id>/tasklist/<int:tasklist_id>/task/<int:task_id>/tasklog/<int:tasklog_id>', methods = ["GET", "POST"])
@login_required
def delete_tasklog(project_id, tasklist_id, task_id, tasklog_id) :
    tasklist = TaskList.query.filter_by(id = tasklist_id).first_or_404()
    task = Task.query.filter_by(id = task_id).first_or_404()
    tasklog = TaskLog.query.filter_by(id = tasklog_id).first_or_404()
    # Check if current user, task list, task and task log is in the project 
    if current_user.is_in_project(project_id) and tasklist.project_id == project_id and task.tasklist_id == tasklist_id and tasklog.task_id == task_id :
        flash("Deleted Task Log - \"{}\"".format(tasklog.note))
        db.session.delete(tasklog)
        db.session.commit()
    else :
        flash("You cannot delete task logs from this project.")
    return redirect(url_for('edit_task', project_id = project_id, tasklist_id = tasklist_id, task_id = task_id))