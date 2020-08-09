from app import app, db
from app.models import User, Project, TaskList, Task, TaskLog

@app.shell_context_processor
def make_shell_context() :
    return {
        "db" : db,
        "User" : User,
        "Project" : Project,
        "TaskList" : TaskList,
        "Task" : Task,
        "TaskLog" : TaskLog
    }