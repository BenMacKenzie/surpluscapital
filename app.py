

import flask
import dash
import dash_html_components as dhc
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import dash_table

from transasctions import *

from engine import get_projection


app = dash.Dash('Surplus Capital')
server = app.server

text_style = dict(color='#444', fontFamily='sans-serif', fontWeight=300)



data = {
    "parameters":
        {
        "growth_rate": 0.05,
        "income_rate": 0.02,
        "inflation": 0.02,
        "interest_rate": 0.03,
        "start_year": 2020,
        "client_age": 65,
        "client_life_expectancy": 95,
        "spouse": True,
        "spouse_age": 65,
        "spouse_life_expectancy": 95,
        "end_year": 2044,
        "end_balance": 0,
        "tax_rate":  {"marginal": [(12070, 0.0), (50000, 0.25), (90000, 0.35), (200000, 0.45)], "top": 0.54},
        "pensions": [

        ],
        "incomes": [],
        "pli": [],
        "income_requirements": [],
        "charitable_donations": [],
        },
    "start_book":  {
        "joint" : {Account.CLEARING: 0,
                   Account.HOME: 0},
        "client" : {
            Account.REGULAR: 0,
            Account.REGULAR_BOOK_VALUE: 0,
            Account.TFSA: 0,
            Account.RRSP: 0,
            Account.RRIF: 0,
            Account.LIF: 0,
            Account.LIRA: 0
        },

        "spouse": {
            Account.REGULAR: 0,
            Account.REGULAR_BOOK_VALUE: 0,
            Account.TFSA: 0,
            Account.RRSP: 0,
            Account.RRIF: 0,
            Account.LIF: 0,
            Account.LIRA: 0
        }
    }

}






app.layout = dhc.Div([
        dhc.H2('Surplus Capital', style=text_style),


        dhc.Table([
            dhc.Tr([dhc.Td("Plan Type"), dhc.Td(dcc.Dropdown('plan_type', options=[{'label': 'joint', 'value': 'joint'}, {'label': 'client', 'value': 'client'}], value='joint'))]),
            dhc.Tr([dhc.Td(""), dhc.Td("client"), dhc.Td("spouse")]),
            dhc.Tr([dhc.Td("Age: "),
                    dhc.Td(dcc.Input(id='client_age', type='number', placeholder='0', value='65')),
                    dhc.Td(dcc.Input(id='spouse_age', type='number', placeholder='0', value='65'))]),

            dhc.Tr([dhc.Td("Life Expectancey: "),
                    dhc.Td(dcc.Input(id='client_life_expectancy', type='number', placeholder='0', value='95')),
                    dhc.Td(dcc.Input(id='spouse_life_expectancy', type='number', placeholder='0', value='95'))]),

            dhc.Tr([dhc.Td("Regular Asset: "), dhc.Td(dcc.Input(id='client_regular_account',type='number', placeholder='0', value='0')), dhc.Td(dcc.Input(id='spouse_regular_account',type='number', placeholder='0', value='0'))]),
            dhc.Tr([dhc.Td("Regular Asset Book Value: "), dhc.Td(dcc.Input(id='client_regular_account_bv', type='number', placeholder='0', value='0')), dhc.Td(dcc.Input(id='spouse_regular_account_bv', type='number', placeholder='0', value='0'))]),

            dhc.Tr([dhc.Td("TFSA: "), dhc.Td(dcc.Input(id='client_tfsa_account', type='number', placeholder='0', value='0')), dhc.Td(dcc.Input(id='spouse_tfsa_account', type='number', placeholder='0', value='0'))]),
            dhc.Tr([dhc.Td("RRIF: "), dhc.Td(dcc.Input(id='client_rrif_account', type='number', placeholder='0', value='0')), dhc.Td(dcc.Input(id='spouse_rrif_account', type='number', placeholder='0', value='0'))]),

            dhc.Tr([dhc.Td("RRSP: "), dhc.Td(dcc.Input(id='client_rrsp_account', type='number', placeholder='0', value='0')), dhc.Td(dcc.Input(id='spouse_rrsp_account', type='number', placeholder='0', value='0'))]),
            dhc.Tr([dhc.Td("LIRA: "), dhc.Td(dcc.Input(id='client_lira_account', type='number', placeholder='0', value='0')),dhc.Td(dcc.Input(id='spouse_lira_account', type='number', placeholder='0', value='0'))]),

            dhc.Tr([dhc.Td("LIF: "), dhc.Td(dcc.Input(id='client_lif_account', type='number', placeholder='0', value='0')), dhc.Td(dcc.Input(id='spouse_lif_account', type='number', placeholder='0', value='0'))]),

            dhc.Tr([dhc.Td("Home"), dhc.Td(dcc.Input(id='home_value', type='number', placeholder='0', value='0')), dhc.Td(dcc.Checklist(id='sell_home', options=[{'label': 'Sell Home', 'value': 'yes'}])), dhc.Td(dcc.Input(id='sell_home_year', type='number', placeholder='0', value='0'))])

        ]),

dhc.Table([
        dhc.Tr([dhc.Td("earned income"), dhc.Td("amount"), dhc.Td("start year"), dhc.Td("end year"), dhc.Td("index")]),
        dhc.Tr([dhc.Td("client: "),
                dhc.Td(dcc.Input(id='client_income_amount', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='client_income_start_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='client_income_end_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Dropdown('client_income_index',
                                    options=[{'label': '0', 'value': '0.0'},
                                             {'label': '1%', 'value': '0.01'},
                                             {'label': '2%', 'value': '0.02'},
                                             {'label': '3%', 'value': '0.03'},
                                             {'label': '4%', 'value': '0.04'},
                                             {'label': '5%', 'value': '0.05'},
                                             ], value='0.02'))]),
        dhc.Tr([dhc.Td("spouse:"),
                dhc.Td(dcc.Input(id='spouse_income_amount', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='spouse_income_start_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='spouse_income_end_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Dropdown('spouse_income_index',
                                    options=[{'label': '0', 'value': '0.0'},
                                             {'label': '1%', 'value': '0.01'},
                                             {'label': '2%', 'value': '0.02'},
                                             {'label': '3%', 'value': '0.03'},
                                             {'label': '4%', 'value': '0.04'},
                                             {'label': '5%', 'value': '0.05'},
                                             ], value='0.02'))])]),


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
        dhc.Tr([dhc.Td("client oas: "),
                dhc.Td(dcc.Input(id='client_oas_amount', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='client_oas_start_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='client_oas_end_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Dropdown('client_oas_index',
                                    options=[{'label': '0', 'value': '0.0'},
                                             {'label': '1%', 'value': '0.01'},
                                             {'label': '2%', 'value': '0.02'},
                                             {'label': '3%', 'value': '0.03'},
                                             {'label': '4%', 'value': '0.04'},
                                             {'label': '5%', 'value': '0.05'},
                                             ], value='0.02'))]),
        dhc.Tr([dhc.Td("client cpp: "),
                dhc.Td(dcc.Input(id='client_cpp_amount', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='client_cpp_start_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='client_cpp_end_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Dropdown('client_cpp_index',
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

        dhc.Tr([dhc.Td("spouse oas: "),
            dhc.Td(dcc.Input(id='spouse_oas_amount', type='number', placeholder='0', value='0')),
            dhc.Td(dcc.Input(id='spouse_oas_start_year', type='number', placeholder='0', value='0')),
            dhc.Td(dcc.Input(id='spouse_oas_end_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Dropdown('spouse_oas_index',
                                    options=[{'label': '0', 'value': '0.0'},
                                             {'label': '1%', 'value': '0.01'},
                                             {'label': '2%', 'value': '0.02'},
                                             {'label': '3%', 'value': '0.03'},
                                             {'label': '4%', 'value': '0.04'},
                                             {'label': '5%', 'value': '0.05'},
                                             ], value='0.02'))]),


        dhc.Tr([dhc.Td("spouse cpp: "),
            dhc.Td(dcc.Input(id='spouse_cpp_amount', type='number', placeholder='0', value='0')),
            dhc.Td(dcc.Input(id='spouse_cpp_start_year', type='number', placeholder='0', value='0')),
            dhc.Td(dcc.Input(id='spouse_cpp_end_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Dropdown('spouse_cpp_index',
                                    options=[{'label': '0', 'value': '0.0'},
                                             {'label': '1%', 'value': '0.01'},
                                             {'label': '2%', 'value': '0.02'},
                                             {'label': '3%', 'value': '0.03'},
                                             {'label': '4%', 'value': '0.04'},
                                             {'label': '5%', 'value': '0.05'},
                                             ], value='0.02'))]),



    ]),



    dhc.Table([
        dhc.Tr([dhc.Td("permanent life insurance"), dhc.Td("amount")]),
        dhc.Tr([dhc.Td("client: "),
                dhc.Td(dcc.Input(id='client_pli_amount', type='number', placeholder='0', value='0'))
              ]),
        dhc.Tr([dhc.Td("spouse: "),
                dhc.Td(dcc.Input(id='spouse_pli_amount', type='number', placeholder='0', value='0'))
                ]),
       ]),





    dhc.Div(),


    dhc.Table([
        dhc.Tr([dhc.Td(""), dhc.Td("amount"), dhc.Td("start year"), dhc.Td("end year"), dhc.Td("index")]),
        dhc.Tr([dhc.Td("donaation "),
                dhc.Td(dcc.Input(id='charitable_donation_amount', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='charitable_donation_start_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Input(id='charitable_donation_end_year', type='number', placeholder='0', value='0')),
                dhc.Td(dcc.Dropdown('charitable_donation_index',
                                    options=[{'label': '0', 'value': '0.0'},
                                             {'label': '1%', 'value': '0.01'},
                                             {'label': '2%', 'value': '0.02'},
                                             {'label': '3%', 'value': '0.03'},
                                             {'label': '4%', 'value': '0.04'},
                                             {'label': '5%', 'value': '0.05'},
                                             ], value='0.02'))])]),


        dhc.Table([

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

        dhc.Div(id='error'),

        dcc.Graph(id='plot1'),

        dash_table.DataTable(id='reportxxx', style_table={'overflowX': 'scroll'}),


        dcc.Store(id="client", storage_type='memory', data=data["start_book"]["client"].copy()),
        dcc.Store(id="spouse", storage_type='memory', data=data["start_book"]["spouse"].copy()),
        dcc.Store(id="joint", storage_type='memory', data=data["start_book"]["joint"].copy()),
        dcc.Store(id="xxx", storage_type='memory', data=data["parameters"]),




    ])
spouse_fields = ["spouse_age", "spouse_life_expectancy", "spouse_regular_account", "spouse_regular_account_bv", "spouse_tfsa_account", "spouse_rrsp_account", "spouse_rrif_account", "spouse_lira_account", "spouse_lif_account",
                 "spouse_income_amount", "spouse_income_start_year", "spouse_income_end_year", "spouse_income_index",
                                      'spouse_pli_amount',
                                      'spouse_pension_amount',
                                      'spouse_pension_start_year',
                                      'spouse_pension_end_year',
                                      'spouse_pension_index',
                                      'spouse_oas_amount',
                                      'spouse_oas_start_year',
                                      'spouse_oas_end_year',
                                      'spouse_oas_index',
                                      'spouse_cpp_amount',
                                      'spouse_cpp_start_year',
                                      'spouse_cpp_end_year',
                                      'spouse_cpp_index']


sf_o = [Output(s, "disabled") for s in spouse_fields]


@app.callback(sf_o,  [Input("plan_type", "value")]
)
def update_plan_type(plantype):
    if plantype == "joint":
 #       return [{'display': 'inline'} for _ in spouse_fields]
        return [False for _ in spouse_fields]
    else:
        return [True  for _ in spouse_fields]
  #      return [{'display': 'none'} for _ in spouse_fields]




@app.callback(
    [Output("plot1", "figure"), Output("reportxxx", "columns"),
     Output("reportxxx", "data"), Output("error", "children")], [Input("calculate_button", "n_clicks")],
    state=[State('xxx', 'data'), State('client', 'data'), State('spouse', 'data'), State('joint', 'data')])
def update_graph(n, xxx, client, spouse, joint):
    myexceptions = "Errors: "
    d = {}
    d["parameters"] = xxx
    d["start_book"] = {}
    d["start_book"]["client"] = client
    d["start_book"]["spouse"] = spouse
    d["start_book"]["joint"] = joint


   #catch exdception here...

   # try:
    sc_transactions, essential_capital_projection, surplus_capital_projection, projection, report = get_projection(d)

    fig = go.Figure(data=[
        go.Bar(name='essential', x=projection["year"], y=projection["essential"]),
        go.Bar(name='surplus', x=projection["year"], y=projection["surplus"])
    ])

    fig.update_layout(barmode='stack')

    #except Exception as e:
    #    myexceptions = myexceptions + str(e)
    #    return None, None, None, myexceptions



    client_proj = [record['start']['client'] for record in essential_capital_projection[:-1]]
    client_proj.append(essential_capital_projection[-1]['end']['client'])

    spouse_proj = [record['start']['spouse'] for record in essential_capital_projection[:-1]]
    spouse_proj.append(essential_capital_projection[-1]['end']['spouse'])

    joint_proj = [record['start']['joint'] for record in essential_capital_projection[:-1]]
    joint_proj.append(essential_capital_projection[-1]['end']['joint'])



    report_column_names = [{"name": i, "id": i} for i in report.columns]

    return fig, report_column_names, report.to_dict("records"), ""




@app.callback(Output('joint', 'data'),  [Input('home_value', 'value')], state=[State("joint", "data")])
def update_joint(home_value, data):
    data[Account.HOME] = int(home_value)
    return data



@app.callback(Output('client', 'data'), [Input('client_regular_account', 'value'),
                                         Input('client_regular_account_bv', 'value'),
                                         Input('client_tfsa_account', 'value'),
                                         Input('client_rrif_account', 'value'),
                                         Input('client_rrsp_account', 'value'),
                                         Input('client_lira_account', 'value'),
                                         Input('client_lif_account', 'value'),

                                         ],

                                        state=[State('client', 'data')])
def update_client_book(reg_account, reg_account_bv, tfsa, rrif, rrsp, lira, lif, data):
    data[Account.REGULAR] = int(reg_account)
    data[Account.REGULAR_BOOK_VALUE] = int(reg_account_bv)
    data[Account.TFSA] = int(tfsa)
    data[Account.RRSP] = int(rrsp)
    data[Account.RRIF] = int(rrif)
    data[Account.LIRA] = int(lira)
    data[Account.LIF] = int(lif)


    return data




@app.callback(Output('spouse', 'data'), [Input('spouse_regular_account', 'value'),
                                         Input('spouse_regular_account_bv', 'value'),
                                         Input('spouse_tfsa_account', 'value'),
                                         Input('spouse_rrif_account', 'value'),
                                         Input('spouse_rrsp_account', 'value'),
                                         Input('spouse_lira_account', 'value'),
                                         Input('spouse_lif_account', 'value')
                                         ],
                                        state=[State('spouse', 'data')])
def update_spouse_book(reg_account, reg_account_bv, tfsa, rrif, rrsp, lira, lif, data):
    data[Account.REGULAR] = int(reg_account)
    data[Account.REGULAR_BOOK_VALUE] = int(reg_account_bv)
    data[Account.TFSA] = int(tfsa)
    data[Account.RRIF] = int(rrif)
    data[Account.RRSP] = int(rrsp)
    data[Account.LIRA] = int(lira)
    data[Account.LIF] = int(lif)
    return data

@app.callback(Output('xxx', 'data'), [Input('end_balance', 'value'),
                                      Input('growth_rate', 'value'),
                                      Input('income_rate', 'value'),
                                      Input('inflation_rate', 'value'),
                                      Input('income_requirements', 'value'),
                                      Input('charitable_donation_amount', 'value'),
                                      Input('charitable_donation_start_year', 'value'),
                                      Input('charitable_donation_end_year', 'value'),
                                      Input('charitable_donation_index', 'value'),
                                      Input('client_age', 'value'),
                                      Input('spouse_age', 'value'),
                                      Input('client_life_expectancy', 'value'),
                                      Input('spouse_life_expectancy', 'value'),
                                      Input('client_income_amount', 'value'),
                                      Input('client_income_start_year', 'value'),
                                      Input('client_income_end_year', 'value'),
                                      Input('client_income_index', 'value'),
                                      Input('client_pli_amount', 'value'),
                                      Input('client_pension_amount', 'value'),
                                      Input('client_pension_start_year', 'value'),
                                      Input('client_pension_end_year', 'value'),
                                      Input('client_pension_index', 'value'),
                                      Input('client_oas_amount', 'value'),
                                      Input('client_oas_start_year', 'value'),
                                      Input('client_oas_end_year', 'value'),
                                      Input('client_oas_index', 'value'),
                                      Input('client_cpp_amount', 'value'),
                                      Input('client_cpp_start_year', 'value'),
                                      Input('client_cpp_end_year', 'value'),
                                      Input('client_cpp_index', 'value'),
                                      Input('spouse_income_amount', 'value'),
                                      Input('spouse_income_start_year', 'value'),
                                      Input('spouse_income_end_year', 'value'),
                                      Input('spouse_income_index', 'value'),
                                      Input('spouse_pli_amount', 'value'),
                                      Input('spouse_pension_amount', 'value'),
                                      Input('spouse_pension_start_year', 'value'),
                                      Input('spouse_pension_end_year', 'value'),
                                      Input('spouse_pension_index', 'value'),
                                      Input('spouse_oas_amount', 'value'),
                                      Input('spouse_oas_start_year', 'value'),
                                      Input('spouse_oas_end_year', 'value'),
                                      Input('spouse_oas_index', 'value'),
                                      Input('spouse_cpp_amount', 'value'),
                                      Input('spouse_cpp_start_year', 'value'),
                                      Input('spouse_cpp_end_year', 'value'),
                                      Input('spouse_cpp_index', 'value'),
                                      Input('sell_home', 'value'),
                                      Input('sell_home_year', 'value'),
                                      Input("plan_type", 'value')

                                      ], state=[State('xxx', 'data')])
def update_end_balance(balance, growth_rate, income_rate, inflation_rate, income_requirements,
                       charitable_donation_amount, charitable_donation_start_year, charitable_donation_end_year, charitable_donation_index,
                       client_age, spouse_age, client_life_expectancy, spouse_life_expectancy,
                       client_income_amount, client_income_start, client_income_end, client_income_index,
                       client_pli_amount,
                       client_pension_amount, client_pension_start, client_pension_end, client_pension_index,
                       client_oas_amount, client_oas_start, client_oas_end, client_oas_index,
                       client_cpp_amount, client_cpp_start, client_cpp_end, client_cpp_index,
                       spouse_income_amount, spouse_income_start, spouse_income_end, spouse_income_index,
                       spouse_pli_amount,
                       spouse_pension_amount, spouse_pension_start, spouse_pension_end, spouse_pension_index,
                       spouse_oas_amount, spouse_oas_start, spouse_oas_end, spouse_oas_index,
                       spouse_cpp_amount, spouse_cpp_start, spouse_cpp_end, spouse_cpp_index,
                       sell_home, sell_home_year, plan_type,
                       data):

    data["start_year"] = 2020 #fix this
    data["end_balance"]= int(balance)
    data["growth_rate"] = float(growth_rate)
    data["income_rate"] = float(income_rate)
    data["inflation"] = float(inflation_rate)




    data["client_age"]=int(client_age)
    data["spouse_age"] = int(spouse_age)

    data["client_life_expectancy"]=int(client_life_expectancy)
    data["spouse_life_expectancy"] = int(spouse_life_expectancy)

    if plan_type == "client":
        data["spouse"] = False
        data["end_year"] =  data["start_year"] + data["client_life_expectancy"] -  data["client_age"]
    else:
        data["spouse"] = True
        data["end_year"] = max([ data["start_year"] + data["client_life_expectancy"] -  data["client_age"],  data["start_year"] + data["spouse_life_expectancy"] -  data["spouse_age"]])



    data["income_requirements"] = []
    core_income = {"start_year": 2020, "end_year": data["end_year"], "amount":  int(income_requirements), "index_rate": data["inflation"], "type": "CORE_NEEDS"}
    data["income_requirements"].append(core_income)
    core_income = {"start_year": 2020, "end_year": data["end_year"], "amount": 0, "index_rate": data["inflation"], "type": "HEALTH_CARE_EXPENSES"}
    data["income_requirements"].append(core_income)
    core_income = {"start_year": 2020, "end_year": data["end_year"], "amount": 0,  "index_rate": data["inflation"], "type": "DISCRETIONARY_SPENDING"}
    data["income_requirements"].append(core_income)


    data["charitable_donations"] = []
    if charitable_donation_amount != '0':
        donation = {}
        donation['start_year'] = charitable_donation_start_year
        donation['end_year'] = charitable_donation_end_year
        donation["amount"] =    int(charitable_donation_amount)
        donation['index_rate'] = float(charitable_donation_index)

        data["charitable_donations"].append(donation)




    data["incomes"] = []
    if client_income_amount != '0':
        client_pension = {}
        client_pension["name"] = "client_income"
        client_pension["person"] = "client"
        client_pension["amount"] = int(client_income_amount)
        client_pension["start_year"] = int(client_income_start)
        client_pension["end_year"] = int(client_income_end)
        client_pension["index_rate"] = float(client_income_index)
        data["incomes"].append(client_pension)

    if spouse_income_amount != '0':
        client_pension = {}
        client_pension["name"] = "spouse_income"
        client_pension["person"] = "spouse"
        client_pension["amount"] = int(spouse_income_amount)
        client_pension["start_year"] = int(spouse_income_start)
        client_pension["end_year"] = int(spouse_income_end)
        client_pension["index_rate"] = float(spouse_income_index)
        data["incomes"].append(client_pension)


    data["pli"] = []

    if client_pli_amount != '0':
        client_pli = {}
        client_pli["person"] = "client"
        client_pli["amount"] = int(client_pli_amount)
        data["pli"].append(client_pli)

    if spouse_pli_amount != '0':
        spouse_pli = {}
        spouse_pli["person"] = "spouse"
        spouse_pli["amount"] = int(spouse_pli_amount)
        data["pli"].append(spouse_pli)

    data["pensions"] = []

    if client_pension_amount != '0':
        client_pension = {}
        client_pension["name"] = "OTHER_PENSION"
        client_pension["person"] = "client"
        client_pension["amount"] = int(client_pension_amount)
        client_pension["start_year"] = int(client_pension_start)
        client_pension["end_year"] = int(client_pension_end)
        client_pension["index_rate"] = float(client_pension_index)
        data["pensions"].append(client_pension)

    if client_oas_amount != '0':
        client_oas = {}
        client_oas["name"] = "OAS"
        client_oas["person"] = "client"
        client_oas["amount"] = int(client_oas_amount)
        client_oas["start_year"] = int(client_oas_start)
        client_oas["end_year"] = int(client_oas_end)
        client_oas["index_rate"] = float(client_oas_index)
        data["pensions"].append(client_oas)

    if client_cpp_amount != '0':
        client_cpp = {}
        client_cpp["name"] = "CPP"
        client_cpp["person"] = "client"
        client_cpp["amount"] = int(client_cpp_amount)
        client_cpp["start_year"] = int(client_cpp_start)
        client_cpp["end_year"] = int(client_cpp_end)
        client_cpp["index_rate"] = float(client_cpp_index)
        data["pensions"].append(client_cpp)

    if spouse_pension_amount != '0':
        spouse_pension = {}
        spouse_pension["name"] = "OTHER_PENSION"
        spouse_pension["person"] = "spouse"
        spouse_pension["amount"] = int(spouse_pension_amount)
        spouse_pension["start_year"] = int(spouse_pension_start)
        spouse_pension["end_year"] = int(spouse_pension_end)
        spouse_pension["index_rate"] = float(spouse_pension_index)
        data["pensions"].append(spouse_pension)


    if spouse_oas_amount != '0':
        spouse_oas= {}
        spouse_oas["name"] = "OAS"
        spouse_oas["person"] = "spouse"
        spouse_oas["amount"] = int(spouse_oas_amount)
        spouse_oas["start_year"] = int(spouse_oas_start)
        spouse_oas["end_year"] = int(spouse_oas_end)
        spouse_oas["index_rate"] = float(spouse_oas_index)
        data["pensions"].append(spouse_oas)

    if spouse_cpp_amount != '0':
        spouse_pension = {}
        spouse_pension["name"] = "CPP"
        spouse_pension["person"] = "spouse"
        spouse_pension["amount"] = int(spouse_cpp_amount)
        spouse_pension["start_year"] = int(spouse_cpp_start)
        spouse_pension["end_year"] = int(spouse_cpp_end)
        spouse_pension["index_rate"] = float(spouse_cpp_index)
        data["pensions"].append(spouse_pension)

    if sell_home != []:
        data["sell_home"] = sell_home_year


    return data



# Put your Dash code here


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=False, threaded=True)