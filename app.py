import os
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_draggable

# Загрузка данных
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

# Переименование колонок для русского языка
df = df.rename(columns={
    'country': 'Страна',
    'continent': 'Континент',
    'year': 'Год', 
    'pop': 'Население',
    'gdpPercap': 'ВВП на душу',
    'lifeExp': 'Продолжительность жизни'
})

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server  # КРИТИЧЕСКИ ВАЖНО для Render

app.layout = html.Div([
    html.H3(children='Дашборд по странам', style={'textAlign': 'center'}),
    
    html.Div([
        html.H4('Выбор года'),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in sorted(df['Год'].unique())],
            value=df['Год'].max(),
            style={'width': '100%'}
        )
    ], style={'textAlign': 'center', 'margin': '0 auto'}),
    
    dash_draggable.ResponsiveGridLayout(
        id='draggable-dashboard',
        clearSavedLayout=False,
        children=[
            html.Div([
                html.H4('Линейная диаграмма', style={'textAlign': 'center'}),
                dcc.Dropdown(df['Страна'].unique(), ['Canada', 'China'], multi=True, id='line-dropdown-selection'),
                html.Div([
                    html.Label('Показатель:'),
                    dcc.Dropdown(
                        ['Население', 'ВВП на душу', 'Продолжительность жизни'],
                        'Население',
                        id='line-y-axis'
                    ),
                ]),
                dcc.Graph(id='line-graph', style={'height': 300})
            ], style={"height": "100%", "display": "flex", "flex-direction": "column"}),
            
            html.Div([
                html.H4('Пузырьковая диаграмма', style={'textAlign': 'center'}),
                html.Div([
                    html.Div([
                        html.Label('Ось X:'),
                        dcc.Dropdown(
                            ['Население', 'ВВП на душу', 'Продолжительность жизни'],
                            'ВВП на душу',
                            id='bubble-x-axis'
                        ),
                    ], style={'width': '32%', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Ось Y:'),
                        dcc.Dropdown(
                            ['Население', 'ВВП на душу', 'Продолжительность жизни'],
                            'Продолжительность жизни',
                            id='bubble-y-axis'
                        ),
                    ], style={'width': '32%', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Размер пузырьков:'),
                        dcc.Dropdown(
                            ['Население', 'ВВП на душу', 'Продолжительность жизни'],
                            'Население',
                            id='bubble-size'    
                        ),
                    ], style={'width': '32%', 'display': 'inline-block'}),
                ]),
                dcc.Graph(id='bubble-graph', style={'height': 300})
            ], style={"height": "100%", "display": "flex", "flex-direction": "column"}),
            
            html.Div([
                html.H4('Топ-15 стран по населению'),
                dcc.Graph(id='top15-graph', style={'height': 300})
            ], style={"height": "100%", "display": "flex", "flex-direction": "column"}),
            
            html.Div([
                html.H4('Население по континентам'),
                dcc.Graph(id='pie-graph', style={'height': 300})
            ], style={"height": "100%", "display": "flex", "flex-direction": "column"})
        ]
    )
])

# Callback функции
@callback(
    Output('line-graph', 'figure'),
    [Input('line-dropdown-selection', 'value'),
     Input('line-y-axis', 'value')]
)
def update_line_graph(selected_countries, y_axis):
    if not selected_countries:
        return px.line(title='Выберите интересующие страны')
    dff = df[df['Страна'].isin(selected_countries)]
    fig = px.line(dff, x='Год', y=y_axis, color='Страна')
    return fig

@callback(
    Output('bubble-graph', 'figure'),
    [Input('bubble-x-axis', 'value'),
     Input('bubble-y-axis', 'value'),
     Input('bubble-size', 'value'),
     Input('year-dropdown', 'value')]
)
def update_bubble_graph(x_axis, y_axis, size_axis, selected_year):
    dff = df[df['Год'] == selected_year]
    fig = px.scatter(dff, x=x_axis, y=y_axis, size=size_axis, color='Континент', hover_name='Страна', size_max=60)
    return fig

@callback(
    Output('top15-graph', 'figure'),
    Input('year-dropdown', 'value')
)
def update_top15_graph(selected_year):
    dff = df[df['Год'] == selected_year]
    top15 = dff.nlargest(15, 'Население')
    fig = px.bar(top15, x='Население', y='Страна', color='Континент', orientation='h')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig

@callback(
    Output('pie-graph', 'figure'),
    Input('year-dropdown', 'value')
)
def update_pie_graph(selected_year):
    dff = df[df['Год'] == selected_year]
    con_population = dff.groupby('Континент')['Население'].sum().reset_index()
    fig = px.pie(con_population, values='Население', names='Континент', hole=0.3)
    return fig

# Запуск приложения для Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port, debug=False)