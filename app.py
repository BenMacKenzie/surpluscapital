

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



data = {
    "parameters":
        {
        "growth_rate": 0.05,
        "income_rate": 0.02,
        "inflation": 0.02,
        "start_year": 2020,
        "client_age": 67,
        "spouse": True,
        "spouse_age": 63,
        "end_year": 2044,
        "end_balance": 100000,
        "tax_rate": 0.40,
        "pensions": [
        {"name": "client_cpp",
         "amount": 16000,
         "start_year": 2022,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "spouse_cpp",
         "amount": 16000,
         "start_year": 2022,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "client_oas",
         "amount": 7200,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "spouse_oas",
         "amount": 7200,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "client_pension",
         "amount": 0,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "spouse_pension",
         "amount": 0,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         }
        ],
        "income_requirements": 140000,
        },
    "start_book":  {
        "joint" : {Account.CLEARING: 0,
                   Account.HOME: 0},
        "client" : {
            Account.REGULAR: 800000,
            Account.REGULAR_BOOK_VALUE: 800000,
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
        }
    }

}






app.layout = dhc.Div([
        dhc.H2('Surplus Capital', style=text_style),

      #  dhc.P([
      #      "Regular Asset Account Balance:",  dcc.Input(id='Regular_Account_Balance',type='number', placeholder='0', value='100000')
      #  ]),
      #  dhc.P([
      #      "End Balance: ", dcc.Input(id="end_balance",type='number', placeholder='0', value='0' )
      #  ]),

        dhc.Table([
            dhc.Tr([dhc.Td("Regular Asset Account Balance: "), dhc.Td(dcc.Input(id='client_regular_account',type='number', placeholder='0', value='100000'))]),
            dhc.Tr([dhc.Td("End Balance"), dhc.Td(dcc.Input(id="end_balance",type='number', placeholder='0', value='0' ))])

        ]),


        dhc.Button('Calculate', id='calculate_button'),
        dcc.Graph(id='plot1'),

        dcc.Store(id="client", storage_type='session', data=data["start_book"]["client"].copy()),
        dcc.Store(id="spouse", storage_type='session', data=data["start_book"]["spouse"].copy()),
        dcc.Store(id="joint", storage_type='session', data=data["start_book"]["joint"].copy()),
        dcc.Store(id="xxx", storage_type='session', data=data["parameters"]),

        #add multiple stores to make this easier?
    ])



@app.callback(
    Output("plot1", "figure"), [Input("calculate_button", "n_clicks")],  state=[State('xxx', 'data'), State('client', 'data'), State('spouse', 'data'), State('joint', 'data')])
def update_graph(n, xxx, client, spouse, joint):

    d = {}
    d["parameters"] = xxx
    d["start_book"] = {}
    d["start_book"]["client"] = client
    d["start_book"]["spouse"] = spouse
    d["start_book"]["joint"] = joint

    _, _, _, projection = get_projection(d)

    fig = go.Figure(data=[
        go.Bar(name='essential', x=projection["year"], y=projection["essential"]),
        go.Bar(name='surplus', x=projection["year"], y=projection["surplus"])
    ])

    return fig


@app.callback(Output('client', 'data'), [Input('client_regular_account', 'value')], state=[State('client', 'data')])
def update_client_book(reg_account, data):
    data[Account.REGULAR] = int(reg_account)
    return data



@app.callback(Output('xxx', 'data'), [Input('end_balance', 'value')], state=[State('xxx', 'data')])
def update_end_balance(balance, data):
    data["end_balance"]= int(balance)
    return data



# Put your Dash code here


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=False, threaded=True)