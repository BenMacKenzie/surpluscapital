

import flask
import dash
import dash_html_components as dhc
import dash_core_components as dcc
import plotly.graph_objects as go

import plotly.express as px

from engine import get_essenetial_capital_projection

# Setup the app
# Make sure not to change this file name or the variable names below,
# the template is configured to execute 'server' on 'app.py'
#server = flask.Flask(__name__)
#server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash('Dash Hello World')
server = app.server

text_style = dict(color='#444', fontFamily='sans-serif', fontWeight=300)
#plotly_figure = dict(data=[dict(x=[1,2,3], y=[2,4,8])])
data = get_essenetial_capital_projection()
#fig = px.bar(data, x='year', y='capital')



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