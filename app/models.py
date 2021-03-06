from datetime import datetime
from flask import current_app
from app import db, login
# Secure Password
from werkzeug.security import generate_password_hash, check_password_hash
# Login
from flask_login import UserMixin
# Avatar
from hashlib import md5
# Reset Password
from time import time
import jwt

UserProjects = db.Table("UserProjects",
    db.Column("user_id", db.Integer, db.ForeignKey('User.id')),
    db.Column("project_id", db.Integer, db.ForeignKey('Project.id'))
)

class TaskLog(db.Model) :
    __tablename__ = 'TaskLog'
    id = db.Column(db.Integer, primary_key = True)
    note = db.Column(db.String(128))
    start_time = db.Column(db.DateTime, nullable = False)
    end_time = db.Column(db.DateTime, nullable = False)
    task_id = db.Column(db.Integer, db.ForeignKey("Task.id"))

    def __repr__(self) :
        return "<TaskLog {}, {} to {}>".format(self.id, self.start_time, self.end_time)

class Task(db.Model) :
    __tablename__ = 'Task'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), nullable = False)
    description = db.Column(db.Text)
    tasklist_id = db.Column(db.Integer, db.ForeignKey("TaskList.id"))
    is_complete = db.Column(db.Boolean, default = False)
    durations = db.relationship(
        "TaskLog",
        backref = db.backref("task"),
        lazy = "dynamic",
        cascade = "all,delete"
    )

    def __repr__(self) :
        return "<Task {}, {}>".format(self.id, self.name)

class TaskList(db.Model) :
    __tablename__ = 'TaskList'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), nullable = False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey("Project.id"))
    tasks = db.relationship(
        "Task",
        backref = db.backref("tasklist"),
        lazy = "dynamic",
        cascade = "all,delete"
    )

    def __repr__(self) :
        return "{}".format(self.name)


class User(UserMixin, db.Model) :
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(128), index = True, unique = True)
    password_hash = db.Column(db.String(128), nullable = False)
    about_me = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self) :
        return "<User {}, {}>".format(self.id, self.username)

    # Password
    def set_password(self, password) :
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) :
        return check_password_hash(self.password_hash, password)

    # Avatar
    def avatar(self, size) :
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest, size)

    # Projects
    def is_in_project(self, project_id) :
        return self.projects.filter(UserProjects.c.project_id == project_id).count() > 0

    # Reset Password
    def get_reset_password_token(self, expires_in = 600):
        return jwt.encode(
            {
                'reset_password' : self.id,
                'exp' : time() + expires_in
            },
            current_app.config['SECRET_KEY'], algorithm = 'HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms = ['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Project(db.Model) : 
    __tablename__ = 'Project'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), nullable = False)
    description = db.Column(db.Text)
    members = db.relationship(
        "User", 
        secondary = UserProjects, 
        primaryjoin = (UserProjects.c.project_id == id), 
        secondaryjoin = (UserProjects.c.user_id == User.id), 
        # Deletes the projects backref instead of the members backref
        # If members backref is deleted, then the user is deleted as well
        backref = db.backref("projects", lazy = "dynamic", cascade = "all,delete"),
        lazy = "dynamic",
    )
    tasklists = db.relationship(
        "TaskList",
        backref = db.backref("project"),
        lazy = "dynamic",
        cascade = "all,delete"
    )

    def __repr__(self) :
        return "<Project {}, {}>".format(self.id, self.name)

    # Projects
    def add_to_project(self, user) :
        if not self.__is_in_project(user) :
            self.members.append(user)

    def remove_from_project(self, user) :
        if self.__is_in_project(user) :
            self.members.remove(user)

    def __is_in_project(self, user) :
        return self.members.filter(UserProjects.c.user_id == user.id).count() > 0

@login.user_loader
def load_user(id) :
    return User.query.get(int(id))