import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from database import data  # Importing the data fetched from Firebase

# Initialize Dash app
app = dash.Dash(__name__)

# Constants for Image size
IMAGE_WIDTH = "400px"
IMAGE_HEIGHT = "270px"

# Prepare data for the dashboard
def get_total_tasks(filtered_data):
    return sum(len(date_tasks) for space in filtered_data.values() for date_tasks in space.values())

def get_completed_tasks(filtered_data):
    return sum(1 for space in filtered_data.values() for date_tasks in space.values() for task in date_tasks.values() if task['status'] == 'complete')

def get_incomplete_tasks(filtered_data):
    return sum(1 for space in filtered_data.values() for date_tasks in space.values() for task in date_tasks.values() if task['status'] == 'incomplete')

def get_approved_tasks(filtered_data):
    return sum(1 for space in filtered_data.values() for date_tasks in space.values() for task in date_tasks.values() if task['status'] == 'approved')

def calculate_average_ratings(filtered_data):
    task_ratings = {}
    for space in filtered_data.values():
        for date_tasks in space.values():
            for task_details in date_tasks.values():
                task_name = task_details["task"]
                if "rating" in task_details and task_details["rating"] > 0:
                    if task_name not in task_ratings:
                        task_ratings[task_name] = []
                    task_ratings[task_name].append(task_details["rating"])

    average_ratings = {task_name: sum(ratings) / len(ratings) for task_name, ratings in task_ratings.items()}
    return average_ratings

def get_task_images_with_info(filtered_data):
    images_info = []
    for space in filtered_data.values():
        for date_tasks in space.values():
            for task_details in date_tasks.values():
                image_info = {
                    "imageUrl": task_details.get("imageUrl", None),
                    "task": task_details.get("task", ""),
                    "completedBy": task_details.get("completedBy", ""),
                }
                if image_info["imageUrl"]:
                    images_info.append(image_info)
    return images_info

# Layout for the dashboard
app.layout = html.Div([
    html.H1("Task Dashboard", style={'text-align': 'center', 'margin-bottom': '30px'}),

    html.Div([
        # Filter by workspace
        dcc.Dropdown(
            id="workspace-filter",
            options=[{"label": workspace, "value": workspace} for workspace in data.keys()],
            placeholder="Select a workspace",
            multi=True,
            style={'width': '30%', 'display': 'inline-block'}
        ),

        # Filter by date
        dcc.Dropdown(
            id="date-filter",
            placeholder="Select a date",
            multi=True,
            style={'width': '30%', 'display': 'inline-block', 'margin-left': '20px'}
        ),
    ], style={'text-align': 'center', 'margin-bottom': '30px'}),

    html.Div([
        # KPIs in a 2x2 grid
        html.Div([
            html.Div([
                html.H4("Total Tasks", style={'color': '#ffffff'}),
                html.H2(id="total-tasks-kpi", style={'color': '#ffffff'})
            ], className="kpi-card", style={'background-color': '#1f77b4', 'padding': '20px', 'border-radius': '10px'}),
            html.Div([
                html.H4("Completed Tasks", style={'color': '#ffffff'}),
                html.H2(id="completed-tasks-kpi", style={'color': '#ffffff'})
            ], className="kpi-card", style={'background-color': '#2ca02c', 'padding': '20px', 'border-radius': '10px'}),
            html.Div([
                html.H4("Incomplete Tasks", style={'color': '#ffffff'}),
                html.H2(id="incomplete-tasks-kpi", style={'color': '#ffffff'})
            ], className="kpi-card", style={'background-color': '#d62728', 'padding': '20px', 'border-radius': '10px'}),
            html.Div([
                html.H4("Approved Tasks", style={'color': '#ffffff'}),
                html.H2(id="approved-tasks-kpi", style={'color': '#ffffff'})
            ], className="kpi-card", style={'background-color': '#9467bd', 'padding': '20px', 'border-radius': '10px'}),
        ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'gap': '20px', 'margin-bottom': '40px', 'width': '40%', 'float': 'left'}),
        
        # Image display with navigation buttons
        html.Div([
            html.Div([
                html.Img(id='task-image', style={
                    'width': IMAGE_WIDTH, 'height': IMAGE_HEIGHT,
                    'object-fit': 'cover', 'border-radius': '10px',
                    'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.2)'
                }),
            ], style={'text-align': 'center', 'margin-bottom': '10px'}),
            
            # Task name and completed by
            html.Div([
                html.P(id="task-name", style={'font-weight': 'bold'}),
                html.P(id="completed-by", style={'color': 'gray'})
            ]),
            
            # Navigation buttons
            html.Div([
                html.Button("❮", id='prev-button', n_clicks=0, style={
                    'background-color': '#007bff', 'color': 'white',
                    'border': 'none', 'border-radius': '50%',
                    'width': '50px', 'height': '50px', 'font-size': '24px',
                    'margin-right': '20px'
                }),
                html.Button("❯", id='next-button', n_clicks=0, style={
                    'background-color': '#007bff', 'color': 'white',
                    'border': 'none', 'border-radius': '50%',
                    'width': '50px', 'height': '50px', 'font-size': '24px',
                })
            ], style={'text-align': 'center', 'margin-top': '10px'}),
            
        ], style={'width': '55%', 'float': 'right'}),
    ], style={'text-align': 'center', 'margin-bottom': '40px', 'clear': 'both'}),

    html.Div([
        # Task Status Pie Chart
        dcc.Graph(id="task-status-pie", style={'width': '48%', 'display': 'inline-block'}),
        # Star Ratings Bar Chart
        dcc.Graph(id="star-ratings-bar", style={'width': '48%', 'display': 'inline-block'}),
    ], style={'text-align': 'center'}),
])

# Update the date dropdown based on workspace selection
@app.callback(
    Output("date-filter", "options"),
    [Input("workspace-filter", "value")]
)
def set_dates(workspace):
    if workspace:
        selected_workspaces = workspace if isinstance(workspace, list) else [workspace]
        available_dates = sorted({date for ws in selected_workspaces if ws in data for date in data[ws].keys()})
    else:
        available_dates = sorted({date for ws_data in data.values() for date in ws_data.keys()})
    return [{"label": date, "value": date} for date in available_dates]

# Update KPIs, Graphs, and Images based on workspace and date filters and button clicks
@app.callback(
    [Output("total-tasks-kpi", "children"),
     Output("completed-tasks-kpi", "children"),
     Output("incomplete-tasks-kpi", "children"),
     Output("approved-tasks-kpi", "children"),
     Output("task-status-pie", "figure"),
     Output("star-ratings-bar", "figure"),
     Output("task-image", "src"),
     Output("task-name", "children"),
     Output("completed-by", "children")],
    [Input("workspace-filter", "value"),
     Input("date-filter", "value"),
     Input("next-button", "n_clicks"),
     Input("prev-button", "n_clicks")],
    [State("task-image", "src")]
)
def update_dashboard(workspace, selected_date, next_clicks, prev_clicks, current_image):
    if workspace:
        selected_workspaces = workspace if isinstance(workspace, list) else [workspace]
        if selected_date:
            filtered_data = {ws: {dt: data[ws][dt]} for ws in selected_workspaces for dt in selected_date if ws in data and dt in data[ws]}
        else:
            filtered_data = {ws: data[ws] for ws in selected_workspaces if ws in data}
    else:
        if selected_date:
            filtered_data = {ws: {dt: data[ws][dt]} for ws, ws_data in data.items() for dt in selected_date if dt in ws_data}
        else:
            filtered_data = data

    # Calculate KPIs
    total_tasks = get_total_tasks(filtered_data)
    completed_tasks = get_completed_tasks(filtered_data)
    incomplete_tasks = get_incomplete_tasks(filtered_data)
    approved_tasks = get_approved_tasks(filtered_data)

    # Update Task Status Pie Chart
    labels = ['Completed', 'Incomplete']
    values = [completed_tasks, incomplete_tasks]
    task_status_pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    task_status_pie_fig.update_layout(title="Completed vs Incomplete Tasks")

    # Update Star Ratings Bar Chart
    average_ratings = calculate_average_ratings(filtered_data)
    task_names = list(average_ratings.keys())
    ratings = list(average_ratings.values())
    
    star_ratings_bar_fig = go.Figure(data=go.Bar(
        x=task_names,
        y=ratings,
        marker_color='indianred'
    ))
    star_ratings_bar_fig.update_layout(title="Average Star Ratings for Tasks", xaxis_title="Tasks", yaxis_title="Average Rating")

    # Update Image Display with "Next" and "Prev" navigation
    images_info = get_task_images_with_info(filtered_data)
    if images_info:
        current_index = next((index for (index, d) in enumerate(images_info) if d["imageUrl"] == current_image), 0)
        if dash.callback_context.triggered[0]['prop_id'] == 'next-button.n_clicks':
            next_image_info = images_info[(current_index + 1) % len(images_info)]
        elif dash.callback_context.triggered[0]['prop_id'] == 'prev-button.n_clicks':
            next_image_info = images_info[(current_index - 1) % len(images_info)]
        else:
            next_image_info = images_info[0]
    else:
        next_image_info = {"imageUrl": None, "task": "", "completedBy": ""}

    return (
        total_tasks, completed_tasks, incomplete_tasks, approved_tasks, 
        task_status_pie_fig, star_ratings_bar_fig,
        next_image_info["imageUrl"],
        f"Task: {next_image_info['task']}",
        f"Completed By: {next_image_info['completedBy']}"
    )

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
