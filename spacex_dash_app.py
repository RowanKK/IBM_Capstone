# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Extract unique launch sites from the dataframe
launch_sites = spacex_df['Launch Site'].unique().tolist()
# Add an 'ALL' option for selecting all launch sites
launch_sites_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                       [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    html.Br(),
    dcc.Dropdown(id='site-dropdown',
                 options=launch_sites_options,
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={i: '{} Kg'.format(i) for i in range(0, 10001, 1000)},
                    value=[min_payload, max_payload]),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback function for updating the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value')]
)
def update_pie_chart(entered_site):
    if entered_site == 'ALL':
        grouped_data = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(grouped_data, names='Launch Site', values='class', 
                     title="Total Success Launches by Site")
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_fail_count = filtered_df['class'].value_counts().reset_index()
        fig = px.pie(success_fail_count, names='index', values='class', 
                     title=f"Total Success and Failed Launches for {entered_site}")
    return fig

# Callback function for updating the scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', 
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for all Sites')
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', 
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for {entered_site}')
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
