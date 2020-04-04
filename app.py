

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
       # "tax_rate":  {"marginal": [(15000., 0.1), (30000, 0.4)], "top": 0.5},
        "tax_rate":  {"marginal": [(12070, 0.0), (50000, 0.25), (90000, 0.35), (200000, 0.45)], "top": 0.54},
        "pensions": [

        ],
        "income_requirements": 0,
        },
    "start_book":  {
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
        }
    }

}






app.layout = dhc.Div([
        dhc.H2('Surplus Capital', style=text_style),


        dhc.Table([
            dhc.Tr([dhc.Td(""), dhc.Td("client"), dhc.Td("spouse")]),
            dhc.Tr([dhc.Td("Age: "),
                    dhc.Td(dcc.Input(id='client_age', type='number', placeholder='0', value='65')),
                    dhc.Td(dcc.Input(id='spouse_age', type='number', placeholder='0', value='65'))]),

            dhc.Tr([dhc.Td("Regular Asset: "), dhc.Td(dcc.Input(id='client_regular_account',type='number', placeholder='0', value='100000')), dhc.Td(dcc.Input(id='spouse_regular_account',type='number', placeholder='0', value='0'))]),
            dhc.Tr([dhc.Td("Regular Asset Book Value: "), dhc.Td(dcc.Input(id='client_regular_account_bv', type='number', placeholder='0', value='0')), dhc.Td(dcc.Input(id='spouse_regular_account_bv', type='number', placeholder='0', value='0'))]),

            dhc.Tr([dhc.Td("TFSA: "), dhc.Td(dcc.Input(id='client_tfsa_account', type='number', placeholder='0', value='0')), dhc.Td(dcc.Input(id='spouse_tfsa_account', type='number', placeholder='0', value='0'))]),
            dhc.Tr([dhc.Td("RRIF: "), dhc.Td(dcc.Input(id='client_rrif_account', type='number', placeholder='0', value='0')), dhc.Td(dcc.Input(id='spouse_rrif_account', type='number', placeholder='0', value='0'))]),

            dhc.Tr([dhc.Td("RRSP: "), dhc.Td(dcc.Input(id='client_rrsp_account', type='number', placeholder='0', value='0')), dhc.Td(dcc.Input(id='spouse_rrsp_account', type='number', placeholder='0', value='0'))]),

        ]),

    dhc.Table([
        dhc.Tr([dhc.Td("pension name"), dhc.Td("amount"), dhc.Td("start year"), dhc.Td("end year"), dhc.Td("index")]),
        dhc.Tr([dhc.Td("client pension: "),
                dhc.Td(dcc.Input(id='client_pension_amount', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='client_pension_start_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='client_pension_end_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Dropdown('client_pension_index',
                                    options=[{'label': '0', 'value': '0.0'},
                                             {'label': '1%', 'value': '0.01'},
                                             {'label': '2%', 'value': '0.02'},
                                             {'label': '3%', 'value': '0.03'},
                                             {'label': '4%', 'value': '0.04'},
                                             {'label': '5%', 'value': '0.05'},
                                             ], value='0.02'))]),

        dhc.Tr([dhc.Td("spouse pension: "),
            dhc.Td(dcc.Input(id='spouse_pension_amount', type='number', placeholder='0', value='0')),
            dhc.Td(dcc.Input(id='spouse_pension_start_year', type='number', placeholder='0', value='0')),
            dhc.Td(dcc.Input(id='spouse_pension_end_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Dropdown('spouse_pension_index',
                                    options=[{'label': '0', 'value': '0.0'},
                                             {'label': '1%', 'value': '0.01'},
                                             {'label': '2%', 'value': '0.02'},
                                             {'label': '3%', 'value': '0.03'},
                                             {'label': '4%', 'value': '0.04'},
                                             {'label': '5%', 'value': '0.05'},
                                             ], value='0.02'))]),

    ]),


    dhc.Div(),

        dhc.Table([
            dhc.Tr([dhc.Td("End Year"),  dhc.Td(dcc.Input(id="end_year", type='number', placeholder='0', value='2040'))]),

            dhc.Tr([dhc.Td("Income Requirements"), dhc.Td(dcc.Input(id="income_requirements", type='number', placeholder='0', value='100000'))]),
            dhc.Tr([dhc.Td("End Balance"), dhc.Td(dcc.Input(id="end_balance",type='number', placeholder='0', value='0' ))]),
            dhc.Tr([dhc.Td("Growth Rate"), dhc.Td(dcc.Dropdown('growth_rate',
                                options=[{'label': '0', 'value': '0.0'},
                                         {'label': '1%', 'value': '0.01'},
                                         {'label': '2%', 'value': '0.02'},
                                         {'label': '3%', 'value': '0.03'},
                                         {'label': '4%', 'value': '0.04'},
                                         {'label': '5%', 'value': '0.05'},
                                         ], value='0.05'))]),
            dhc.Tr([dhc.Td("Income Rate"), dhc.Td(dcc.Dropdown('income_rate',
                                options=[{'label': '0', 'value': '0.0'},
                                         {'label': '1%', 'value': '0.01'},
                                         {'label': '2%', 'value': '0.02'},
                                         {'label': '3%', 'value': '0.03'},
                                         {'label': '4%', 'value': '0.04'},
                                         {'label': '5%', 'value': '0.05'},
                                        ], value='0.02'))]),

            dhc.Tr([dhc.Td("Inflation Rate"), dhc.Td(dcc.Dropdown('inflation_rate',
                                options=[{'label': '0', 'value': '0.0'},
                                         {'label': '1%', 'value': '0.01'},
                                         {'label': '2%', 'value': '0.02'},
                                         {'label': '3%', 'value': '0.03'},
                                         {'label': '4%', 'value': '0.04'},
                                         {'label': '5%', 'value': '0.05'},
                                        ], value='0.02'))]),

        ]),


        dhc.Button('Calculate', id='calculate_button'),
        dcc.Graph(id='plot1'),

        dcc.Store(id="client", storage_type='memory', data=data["start_book"]["client"].copy()),
        dcc.Store(id="spouse", storage_type='memory', data=data["start_book"]["spouse"].copy()),
        dcc.Store(id="joint", storage_type='memory', data=data["start_book"]["joint"].copy()),
        dcc.Store(id="xxx", storage_type='memory', data=data["parameters"]),


        dcc.Textarea(id='projection_text', style={'width': '100%', 'height': 500})


    ])



@app.callback(
    [Output("plot1", "figure"), Output("projection_text", "value")], [Input("calculate_button", "n_clicks")],  state=[State('xxx', 'data'), State('client', 'data'), State('spouse', 'data'), State('joint', 'data')])
def update_graph(n, xxx, client, spouse, joint):

    d = {}
    d["parameters"] = xxx
    d["start_book"] = {}
    d["start_book"]["client"] = client
    d["start_book"]["spouse"] = spouse
    d["start_book"]["joint"] = joint

    sc_transactions, essential_capital_projection, surplus_capital_projection, projection = get_projection(d)

    fig = go.Figure(data=[
        go.Bar(name='essential', x=projection["year"], y=projection["essential"]),
        go.Bar(name='surplus', x=projection["year"], y=projection["surplus"])
    ])

    text = ""
    for rec in essential_capital_projection:
        text += str(rec["start"]) + "\n"


    return (fig, text)




@app.callback(Output('client', 'data'), [Input('client_regular_account', 'value'),
                                         Input('client_regular_account_bv', 'value'),
                                         Input('client_tfsa_account', 'value'),
                                         Input('client_rrif_account', 'value'),
                                         Input('client_rrsp_account', 'value')],

                                        state=[State('client', 'data')])
def update_client_book(reg_account, reg_account_bv, tfsa, rrif, rrsp, data):
    data[Account.REGULAR] = int(reg_account)
    data[Account.REGULAR_BOOK_VALUE] = int(reg_account_bv)
    data[Account.TFSA] = int(tfsa)
    data[Account.RRSP] = int(rrsp)
    data[Account.RRIF] = int(rrif)
    return data




@app.callback(Output('spouse', 'data'), [Input('spouse_regular_account', 'value'),
                                         Input('spouse_regular_account_bv', 'value'),
                                         Input('spouse_tfsa_account', 'value'),
                                         Input('spouse_rrif_account', 'value'),
                                         Input('spouse_rrsp_account', 'value')
                                         ],
                                        state=[State('spouse', 'data')])
def update_spouse_book(reg_account, reg_account_bv, tfsa, rrif, rrsp, data):
    data[Account.REGULAR] = int(reg_account)
    data[Account.REGULAR_BOOK_VALUE] = int(reg_account_bv)
    data[Account.TFSA] = int(tfsa)
    data[Account.RRIF] = int(rrif)
    data[Account.RRSP] = int(rrsp)
    return data

@app.callback(Output('xxx', 'data'), [Input('end_balance', 'value'),
                                      Input('growth_rate', 'value'),
                                      Input('income_rate', 'value'),
                                      Input('inflation_rate', 'value'),
                                      Input('income_requirements', 'value'),
                                      Input('client_age', 'value'),
                                      Input('spouse_age', 'value'),
                                      Input('end_year', 'value'),
                                      Input('client_pension_amount', 'value'),
                                      Input('client_pension_start_year', 'value'),
                                      Input('client_pension_end_year', 'value'),
                                      Input('client_pension_index', 'value'),
                                      Input('spouse_pension_amount', 'value'),
                                      Input('spouse_pension_start_year', 'value'),
                                      Input('spouse_pension_end_year', 'value'),
                                      Input('spouse_pension_index', 'value')

                                      ], state=[State('xxx', 'data')])
def update_end_balance(balance, growth_rate, income_rate, inflation_rate, income_requirements,
                       client_age, spouse_age, end_year,
                       client_pension_amount, client_pension_start, client_pension_end, client_pension_index,
                       spouse_pension_amount, spouse_pension_start, spouse_pension_end, spouse_pension_index,
                       data):
    data["end_balance"]= int(balance)
    data["growth_rate"] = float(growth_rate)
    data["income_rate"] = float(income_rate)
    data["inflation"] = float(inflation_rate)
    data["income_requirements"] = int(income_requirements)
    data["client_age"]=int(client_age)
    data["spouse_age"] = int(spouse_age)
    data["end_year"]=int(end_year)

    data["pensions"] = []

    if client_pension_amount != '0':
        client_pension = {}
        client_pension["name"] = "client_pension"
        client_pension["person"] = "client"
        client_pension["amount"] = int(client_pension_amount)
        client_pension["start_year"] = int(client_pension_start)
        client_pension["end_year"] = int(client_pension_end)
        client_pension["index_rate"] = float(client_pension_index)
        data["pensions"].append(client_pension)

    if spouse_pension_amount != '0':
        spouse_pension = {}
        spouse_pension["name"] = "spouse_pension"
        spouse_pension["person"] = "spouse"
        spouse_pension["amount"] = int(spouse_pension_amount)
        spouse_pension["start_year"] = int(spouse_pension_start)
        spouse_pension["end_year"] = int(spouse_pension_end)
        spouse_pension["index_rate"] = float(spouse_pension_index)
        data["pensions"].append(spouse_pension)

    return data



# Put your Dash code here


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=False, threaded=True)