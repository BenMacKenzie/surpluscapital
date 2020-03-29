# Import required libraries
import os
from random import randint


import flask
import dash
import dash_html_components as dhc
import dash_core_components as dcc




# Setup the app
# Make sure not to change this file name or the variable names below,
# the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
#server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash('Dash Hello World')

text_style = dict(color='#444', fontFamily='sans-serif', fontWeight=300)
plotly_figure = dict(data=[dict(x=[1,2,3], y=[2,4,8])])

app.layout = dhc.Div([
        dhc.H2('Surplus Capital', style=text_style),
        dhc.P('Enter a Plotly trace type into the text box, such as histogram, bar, or scatter.', style=text_style),
        dcc.Input(id='text1', placeholder='box', value=''),
        dcc.Graph(id='plot1', figure=plotly_figure),
    ])
# Put your Dash code here


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)