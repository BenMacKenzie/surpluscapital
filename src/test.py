from engine import get_projection
import json
from test_utils import get_value

data = {
    "parameters":
        {
        "growth_rate": 0.05,
        "income_rate": 0.02,
        "inflation": 0.02,
        "interest_rate": 0.03,
        "start_year": 2023,
        "client_age": 65,
        "client_life_expectancy": 95,
        "spouse": True,
        "spouse_age": 65,
        "spouse_life_expectancy": 95,
        "end_year": 2044,
        "end_balance": 0,
        "province": "Ontario",
        "pensions": [{"person": "client", "name": "OAS", "start_year": 2023, "end_year": 2053, "amount": 12000, "index_rate": 0.04},
                     {"person": "spouse", "name": "OAS", "start_year": 2023, "end_year": 2053, "amount": 12000, "index_rate": 0.04}],
        "incomes": [{"person": "spouse", "start_year": 2023, "end_year": 2050, "amount": 120000, "index_rate": 0.04}],
        "pli": [{"person": "client", "amount": 50000}],
        "income_requirements": [{"type": "ANNUAL_RETIREMENT_EXPENSES", "start_year": 2023, "end_year": 2050, "amount": 60000, "index_rate": 0.05}],
        "charitable_donations": [{"start_year": 2023, "end_year": 2050, "amount": 1000, "index_rate": 0.05}]
        },
    "start_book":  {
        "joint" : {"CLEARING": 0,
                   "HOME": 0},
        "client" : {
            "NON_REGISTERED_ASSET": 1000000,
            "NON_REGISTERED_BOOK_VALUE": 0,
            "TFSA": 20000,
            "RRSP": 0,
            "RRIF": 0,
            "LIF": 0,
            "LIRA": 0
        },

        "spouse": {
            "NON_REGISTERED_ASSET": 0,
            "NON_REGISTERED_BOOK_VALUE": 0,
            "TFSA": 20000,
            "RRSP": 500000,
            "RRIF": 0,
            "LIF": 0,
            "LIRA": 0
        }
    }

}

g, report = get_projection(data)
print(g)
print(report)
print(json.dumps(data))



cb = get_value(report, 2023, 'SPOUSE_OAS_CLAWBACK')
print(cb)



