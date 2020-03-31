

import flask
import dash
import dash_html_components as dhc
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from transasctions import *

from engine import get_projection


app = dash.Dash('Dash Hello World')
server = app.server

text_style = dict(color='#444', fontFamily='sans-serif', fontWeight=300)



START_BOOK = {
        "joint" : {Account.CLEARING: 0,
                   Account.HOME: 0},
        "client" : {
            Account.REGULAR: 0,
            Account.REGULAR_BOOK_VALUE: 0,
            Account.TFSA: 0,
            Account.RRSP: 0,
            Account.RRIF: 0
        },

        "spouse": {
            Account.REGULAR: 0,
            Account.REGULAR_BOOK_VALUE: 0,
            Account.TFSA: 0,
            Account.RRSP: 0,
            Account.RRIF: 0
        },


}







app.layout = dhc.Div([
        dhc.H2('Surplus Capital', style=text_style),
        dhc.P('Regular Asset Account Balance', style=text_style),
        dcc.Input(id='Regular_Account_Balance', placeholder='0', value='100000'),
        dhc.Button('Calculate', id='calculate_button'),
        dcc.Graph(id='plot1'),
    ])



@app.callback(
    Output("plot1", "figure"), [Input("calculate_button", "n_clicks")], state=[State("Regular_Account_Balance", "value")])
def update_graph(n, end_balance):
    start_book = START_BOOK
    start_book["client"][Account.REGULAR] = int(end_balance)
    _, _, _, data = get_projection(start_book=start_book)

    fig = go.Figure(data=[
        go.Bar(name='essential', x=data["year"], y=data["essential"]),
        go.Bar(name='surplus', x=data["year"], y=data["surplus"])
    ])

    return fig




# Put your Dash code here


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=False, threaded=True)