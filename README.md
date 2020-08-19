# Kanbanize
A visual workflow project management system with a Kanban structure

## Completed Features

- Implemented ability to add multiple projects and tasks with time logs to build and track a real-world project
- Created a complete authentication system for sign up, registration and resetting passwords securely
- Users can view visualizations made using Dash and Plotly to gain insights on time spent on individual tasks and overall time spent on the project
- Realized the Database in SQL utilizing lazy loading for efficiency with complete Unit Test coverage

## Pending Features

- Multiple team members can collaborate on a project
- Different roles within a project
- Drag and drop cards
- Build API which can be consumed by an mobile app (iOS)

# Requirements

- Python3

# Installation and Usage (macOS/Linux)

- Create a virtual environment <code>python3 -m venv venv</code>
- Activate the virtual environment <code>source venv/bin/activate</code>
- Install all the dependencies from requirements.txt <code>pip install -r requirements.txt</code>
- Initialize the database migration system <code>flask db init</code>
- Perform all necessary migrations based on Flask-SQLAlchemy DB models <code>flask db migrate -m "Initial Migration"</code>
- Upgrade the current database <code>flask db upgrade</code>
- Run the application <code>flask run</code>
