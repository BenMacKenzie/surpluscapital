

import flask
import dash
import dash_html_components as dhc
import dash_core_components as dcc
import plotly.graph_objects as go

import plotly.express as px

from engine import get_essential_capital_projection


app = dash.Dash('Dash Hello World')
server = app.server

text_style = dict(color='#444', fontFamily='sans-serif', fontWeight=300)

data = get_essential_capital_projection()



fig = go.Figure(data=[
    go.Bar(name='essential', x=data["year"], y=data["essential"]),
    go.Bar(name='surplus', x=data["year"], y=data["surplus"])
])

app.layout = dhc.Div([
        dhc.H2('Surplus Capital', style=text_style),
        dhc.P('Enter desired end capital', style=text_style),
        dcc.Input(id='text1', placeholder='box', value=''),
        dcc.Graph(id='plot1', figure=fig),
    ])
# Put your Dash code here


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=False, threaded=True)