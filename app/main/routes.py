from flask import render_template, flash, redirect, url_for, request
from app import app, db
# Forms
from app.main.forms import NewProjectForm
# Models
from app.models import User, Project
# Authentication
from flask_login import current_user, login_required
# URL Parse
from werkzeug.urls import url_parse
# Last Seen
# from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index() :
    projects = current_user.projects.all()
    return render_template('index.html', title = "Home", projects = projects)

@app.route('/new_project', methods = ["GET", "POST"])
@login_required
def new_project() :
    form = NewProjectForm()
    if form.validate_on_submit() :
        project = Project(name = form.name.data, description = form.description.data)
        db.session.add(project)
        project.add_to_project(current_user)
        db.session.commit()
        flash("Project - \"{}\" created successfully!".format(project.name))
        return redirect(url_for('index'))
    return render_template('new_project.html', form = form)

@app.route('/project/<int:project_id>')
@login_required
def project(project_id) :
    project = Project.query.filter_by(id = project_id).first_or_404()
    if current_user.is_in_project(project) :
        # Stub
        flash("You can access this project.")
        return render_template('project.html', project = project)
    else :
        # Stub
        flash("You cannot access this project.")
        return redirect(url_for('index'))