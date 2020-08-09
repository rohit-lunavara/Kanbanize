from flask import render_template, url_for, redirect, flash, request
from app import app, db
# Forms
from app.profile.forms import EditProfileForm
# Models
from app.models import User
# Authentication
from flask_login import current_user, login_required
# Last Seen
from datetime import datetime

@app.route('/user/<username>')
@login_required
def user(username) :
    user = User.query.filter_by(username = username).first_or_404()
    projects = []
    return render_template('user.html', user = user, projects = projects)

@app.route('/edit_profile', methods = ["GET", "POST"])
@login_required
def edit_profile() :
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit() :
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for('edit_profile'))
    elif request.method == "GET" :
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title = "Edit Profile", form = form)

@app.before_request
def before_request() :
    if current_user.is_authenticated : 
        current_user.last_seen = datetime.utcnow()
        db.session.commit()