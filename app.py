

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
        dhc.P([
            "Regular Asset Account Balance:",  dcc.Input(id='Regular_Account_Balance',type='number', placeholder='0', value='100000')
        ]),
        dhc.P([
            "End Balance: ", dcc.Input(id="end_balance",type='number', placeholder='0', value='0' )
        ]),

        dhc.Table([dhc.Tr([dhc.Td("hudfa"), dhc.Td("dfa")]), dhc.Tr([dhc.Td("hudfxxxxxa"), dhc.Td("dfa")])]),
        dhc.Button('Calculate', id='calculate_button'),
        dcc.Graph(id='plot1'),
        dcc.Store(id="parameters", storage_type='session', data=START_BOOK)
    ])



@app.callback(
    Output("plot1", "figure"), [Input("calculate_button", "n_clicks")],  state=[State('parameters', 'data')])
def update_graph(n, parameters):

    _, _, _, data = get_projection(start_book=parameters)

    fig = go.Figure(data=[
        go.Bar(name='essential', x=data["year"], y=data["essential"]),
        go.Bar(name='surplus', x=data["year"], y=data["surplus"])
    ])

    return fig


@app.callback(Output('parameters', 'data'), [Input('Regular_Account_Balance', 'value')], state=[State('parameters', 'data')])
def update_account_balance(balance, params):
    params["client"][Account.REGULAR] = int(balance)
    return params



# Put your Dash code here


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=False, threaded=True)