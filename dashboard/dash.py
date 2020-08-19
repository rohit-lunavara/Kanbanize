# Dash
from dash import Dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
# Plotly
import plotly.graph_objs as go
import plotly.express as px
# Authentication
from flask_login import current_user
from dashboard.auth import apply_layout_with_auth
# Database
from app.models import Project, TaskList, Task, TaskLog
# Data Storage
import pandas as pd

dash_url_base = "/visualization/dash/app/"

def create_dashboard(server) :
    """
    Create a Plotly Dash dashboard
    """
    dash_app = Dash(
        __name__,
        server = server,
        url_base_pathname = dash_url_base, 
        assets_folder = "static",
        external_stylesheets = [
            "/static/css/bootstrap-theme.css",
            "/static/css/bootstrap-theme.css.map",
            "/static/css/bootstrap-theme.min.css",
            "/static/css/bootstrap.css",
            "/static/css/bootstrap.css.map",
            "/static/css/bootstrap.min.css",
        ],
        external_scripts = [
            "/static/js/bootstrap.js",
            "/static/js/bootstrap.min.js",
            "/static/js/npm.js",
            "/static/jquery.js",
            "/static/jquery.min.js",
            "/static/jquery.min.map"
        ]
    )

    # Create Dash Layout
    layout = html.Div(id = 'dash-container', children = [
            html.Div(id = 'dash-row', children = [
                # Empty div to trigger callbacks after authentication
                html.Div(
                    id = "none",
                    children = [],
                    style = {
                        "display" : "none"
                    }
                ),

                html.H1(
                    id = "title",
                    children = "Task Duration"
                ),


                dcc.Dropdown(
                    id = "project-dropdown",
                    options = [],
                    value = "",
                    multi = False
                ),

                html.Div(
                    id = "task-bar-stacked-duration-container",
                    children = [
                        html.H3(
                            id = "task-bar-stacked-duration-title",
                            children = "Individual"
                        ),
                        dcc.Graph(
                            id = "task-bar-stacked-duration-graph"
                        )
                    ],
                    className = "col-md-6"
                ),

                html.Div(
                    id = "task-bar-single-duration-container",
                    children = [
                        html.H3(
                            id = "task-bar-single-duration-title",
                            children = "Overall"
                        ),
                        dcc.Graph(
                            id = "task-bar-single-duration-graph"
                        )
                    ],
                    className = "col-md-6"
                )
            ],
            className = "row")
        ],
        className = "container"
    )

    # Apply layout only if user is logged in
    apply_layout_with_auth(dash_app, layout)

    # Initialize callbacks after our app is loaded
    # Pass dash_app as a parameter
    init_callbacks(dash_app)

    return dash_app.server

def init_callbacks(dash_app) :
    @dash_app.callback(
        Output(component_id = "project-dropdown", component_property = "options"),
        [
            Input(component_id = "none", component_property = "children")
        ]
    )
    def load_project_dropdown(none) :
        if current_user and current_user.is_authenticated :
            return [{"value" : ele.id, "label" : ele.name} for ele in current_user.projects]


    @dash_app.callback(
        Output(component_id = "task-bar-single-duration-graph", component_property = "figure"),
        [
            Input(component_id = "project-dropdown", component_property = "value")
        ]
    )
    def overall_task_duration_graph(project_id) :
        project = Project.query.filter_by(id = project_id).first()
        tasklogs = retrieve_tasklogs(project)
        graph_dict = dict()
        for tasklog in tasklogs :
            # For each day, calculate the number of hours of work done
            graph_dict[tasklog.start_time.date()] = graph_dict.get(tasklog.start_time.date(), 0) + (tasklog.end_time - tasklog.start_time).total_seconds() / 3600

        res = pd.DataFrame(
            {
                "StartDate" : [f"{k}" for k in graph_dict.keys()],
                "Duration" : [v for v in graph_dict.values()]
            }
        )

        figure = go.Figure(
            [
                go.Pie(
                    labels = res.StartDate,
                    values = res.Duration,
                    hovertext = [ f"{hours * 60:.2f} minutes" for hours in res.Duration ]
                )
            ]
        )
        figure.update_layout(
            {
                "xaxis" : {
                    "title" : "Date",
                    "tickformat" : '%x',
                },
                "yaxis" : {
                    "title" : "Time Spent (in hrs)"
                }
            }
        )
        return figure

    @dash_app.callback(
        Output(component_id = "task-bar-stacked-duration-graph", component_property = "figure"),
        [
            Input(component_id = "project-dropdown", component_property = "value")
        ]
    )
    def individual_task_duration_graph(project_id) :
        project = Project.query.filter_by(id = project_id).first()
        tasklogs = retrieve_tasklogs(project)

        # For each task, calculate and store the duration along with start_time.date()
        for tasklog in tasklogs :
            print(f"{tasklog.id}, {tasklog.start_time} - {tasklog.end_time}, TASK : {tasklog.task}")

        res = pd.DataFrame(
            {
                "Index" : [ tasklog.task_id for tasklog in tasklogs ],
                "Task" : [ tasklog.task.name for tasklog in tasklogs ],
                "StartDate" : [ f"{tasklog.start_time.date()}" for tasklog in tasklogs ],
                "Duration" : [ ((tasklog.end_time - tasklog.start_time).total_seconds() / 3600) for tasklog in tasklogs ]
            }
        )
        res = res.set_index("Index")

        # TODO - Squash same-day logs into a single bar
        graphs = [
            go.Bar(
                name = split_df.Task.iloc[0],
                x = split_df.StartDate,
                y = split_df.Duration,
                hovertext = [ f"{hours * 60:.2f} minutes" for hours in split_df.Duration ]
            )
            for _, split_df in res.groupby(res.index)
        ]

        figure = go.Figure(
            graphs
        )
        figure.update_layout(
            {
                "xaxis" : {
                    "title" : "Date",
                    "tickformat" : '%x',
                },
                "yaxis" : {
                    "title" : "Time Spent (in hrs)"
                }
            },
            barmode = "stack"
        )

        return figure

def retrieve_tasklogs(project) :
    if project is None : 
        raise PreventUpdate
    tasklogs = []
    for tasklist in project.tasklists :
        for task in tasklist.tasks :
            for tasklog in task.durations :
                tasklogs.append(tasklog)

    return tasklogs