import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from datetime import date
from dash.dependencies import Input, Output
from flask import Flask
from sqlalchemy import create_engine

dialect = 'mysql+pymysql://root:Bigdata2122@localhost:3306/scrapping'
#dialect = 'mysql+pymysql://root@localhost:3306/scrapping'
sqlEngine = create_engine(dialect)

sentencia = f"SELECT * FROM jordimulet_eventos"
eventosdb = pd.read_sql(sentencia, con=sqlEngine)

sentencia = f"SELECT * FROM jordimulet_tipos"
tiposdb = pd.read_sql(sentencia, con=sqlEngine)

# Initialize the app
server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Dashboard'
app.config.suppress_callback_exceptions = False

navbar = dbc.Navbar(
    [
        dbc.NavbarBrand("Teatre Inca", className="ms-2"),
        dcc.DatePickerRange(
            id='fecha_eventos',
            start_date=date.today(),
            display_format='DD-MM-YYYY'
        )
    ],
    color="blue",
    dark=True
)

grafica1 = dcc.Graph(id='histograma',
                     figure={'data': [
                         go.Histogram(
                             x=eventosdb['fecha'],
                             nbinsx=100
                         )
                     ],
                         'layout': go.Layout(title='Cantidad Eventos')}
                     )

grafica2 = dcc.Graph(id='pie',
                     figure={'data': [
                         go.Pie(labels=tiposdb['tipo'].value_counts().index,
                                values=tiposdb['tipo'].value_counts().values, textinfo='none')
                     ],
                         'layout': go.Layout(title='Tipos Eventos')}
                     )

app.layout = html.Div(children=[navbar,
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Row([
                                            dbc.Col(html.Div("Nº barras:"), width=2, style={'padding': 0}),
                                            dbc.Col(dbc.Input(id="barras", type="number", min=0, step=1, value=100),
                                                    width=3, style={'padding': 0})
                                        ], align="start", style={'margin-left': 50, 'margin-top': 10}),
                                        html.Div([grafica1])],
                                        width=4),
                                    dbc.Col(html.Div([grafica2]), width=4),
                                    # dbc.Col(
                                    #    html.Div([table], id='taulaNum', style={'margin-top': 50, 'margin-right': 50}),
                                    #    width=4)
                                ]),
                                ])


@app.callback(Output('histograma', 'figure'),
              [Input('barras', 'value'),
               Input('fecha_eventos', 'start_date'),
               Input('fecha_eventos', 'end_date')])
def update_figure(numero, start, end):
    if end is None:
        eventos = eventosdb[
            (eventosdb.fecha.dt.strftime("%Y-%m-%d") >= start)]
    else:
        eventos = eventosdb[
            (eventosdb.fecha.dt.strftime("%Y-%m-%d") >= start) & (eventosdb.fecha.dt.strftime("%Y-%m-%d") < end)]

    figure = {'data': [
        go.Histogram(
            x=eventos['fecha'],
            nbinsx=numero
        )
    ],
        'layout': go.Layout(title='Cantidad Eventos')}

    return figure

@app.callback(Output('pie', 'figure'),
              [Input('fecha_eventos', 'start_date'),
               Input('fecha_eventos', 'end_date')])
def update_figure(start, end):
    if end is None:
        tipos = tiposdb[
            (eventosdb.fecha.dt.strftime("%Y-%m-%d") >= start)]
    else:
        tipos = tiposdb[
            (eventosdb.fecha.dt.strftime("%Y-%m-%d") >= start) & (eventosdb.fecha.dt.strftime("%Y-%m-%d") < end)]

    pie = {'data': [
        go.Pie(labels=tipos['tipo'].value_counts().index,
               values=tipos['tipo'].value_counts().values, textinfo='none')
    ],
        'layout': go.Layout(title='Tipos Eventos')}

    return pie


if __name__ == '__main__':
    app.run_server(debug=True)
