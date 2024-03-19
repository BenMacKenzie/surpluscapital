from  engine import get_projection
import json
from test_utils import get_value

data = {
    "parameters":
        {
        "growth_rate": 0.015,
        "income_rate": 0.015,
        "inflation": 0.02,
        "interest_rate": 0,
        "oas_clawback" : {"base": 72000, "index": 0.02},
        "personal_exemption": {"base": 12896, "index": 0.02},
        "start_year": 2023,
        "client_age": 55,
        "client_life_expectancy": 100,
        "spouse": True,
        "spouse_age": 65,
        "spouse_life_expectancy": 95,
        "end_year": 2068,
        "end_balance": 50000,
        "sell_home": 2050,
        "province": "Ontario",
        "pensions": [{"person": "client", "name": "CPP", "start_year": 2033, "end_year": 2068, "amount": 1250, "index_rate": 0.02},
                     {"person": "client", "name": "OAS", "start_year": 2024, "end_year": 2068, "amount": 1500, "index_rate": 0.02},
                     {"person": "client", "name": "OTHER", "start_year": 2025, "end_year": 2068, "amount": 1500,
                      "index_rate": 0.0},

                     {"person": "spouse", "name": "CPP", "start_year": 2023, "end_year": 2053, "amount": 1250,
                      "index_rate": 0.02},
                     {"person": "spouse", "name": "OAS", "start_year": 2023, "end_year": 2053, "amount": 1500,
                      "index_rate": 0.02},
                     {"person": "spouse", "name": "OTHER", "start_year": 2023, "end_year": 2053, "amount": 1500,
                      "index_rate": 0.00}
                     ],
        "incomes": [{"person": "client", "start_year": 2023, "end_year": 2023, "amount": 10000, "index_rate": 0.02},
                    {"person": "spouse", "start_year": 2025, "end_year": 2025, "amount": 30000, "index_rate": 0.02},
                    {"person": "client", "start_year": 2024, "end_year": 2024, "amount": 20000, "index_rate": 0.02},
                    {"person": "spouse", "start_year": 2025, "end_year": 2025, "amount": 40000, "index_rate": 0.02}
                   ],
        "pli": [{"person": "client", "amount": 400000},
                {"person": "spouse", "amount": 300000}],
        "income_requirements": [{"person": "client", "type": "ANNUAL_RETIREMENT_EXPENSES", "start_year": 2023,
                                 "end_year": 2068, "amount": 27000, "index_rate": 0.02},
                                {"person": "spouse", "type": "HEALTH_CARE_EXPENSES", "start_year": 2023,
                                 "end_year": 2068, "amount": 22000, "index_rate": 0.02}],
        "ONE_OFF_EXPENSES":[{"start_year": 2023, "end_year": 2024, "amount": 5000, "index_rate": 0.02}],
        "charitable_donations": [{"person": "spouse", "start_year": 2030, "end_year": 2031, "amount": 1250, "index_rate": 0.02}]
        },
    "start_book":  {
        "joint" : {"CLEARING": 0,
                   "HOME": 800000
                   },
        "client" : {
            "NON_REGISTERED_ASSET": 40000,
            "NON_REGISTERED_BOOK_VALUE": 10000,
            "TFSA": 1000,
            "RRSP": 2000,
            "RRIF": 3000,
            "LIF": 5000,
            "LIRA": 4000
        },

        "spouse": {
            "NON_REGISTERED_ASSET": 60000,
            "NON_REGISTERED_BOOK_VALUE": 20000,
            "TFSA": 1000,
            "RRSP": 2000,
            "RRIF": 3000,
            "LIF": 5000,
            "LIRA": 4000
        }
    }
}


g, report = get_projection(data)
print(g)
print(report)
print(json.dumps(data))


a = get_value(report, 2023, 'TFSA')
print(f"TFSA {a}")
a = get_value(report, 2023, 'RRSP')
print(f"RRSP {a}")
a = get_value(report, 2023, 'RRIF')
print(f"RRIF {a}")
a = get_value(report, 2023, 'LIRA')
print(f"LIRA {a}")
a = get_value(report, 2023, 'LIF')
print(f"LIF {a}")
a = get_value(report, 2023, 'NON_REGISTERED_ASSET')
print(f"NON_REGISTERED_ASSET  {a}")

a = get_value(report, 2023, 'SPOUSE_TFSA')
print(f"SPOUSE_TFSA {a}")
a = get_value(report, 2023, 'SPOUSE_RRSP')
print(f"SPOUSE_RRSP {a}")
a = get_value(report, 2023, 'SPOUSE_RRIF')
print(f"SPOUSE_RRIF {a}")
a = get_value(report, 2023, 'SPOUSE_LIRA')
print(f"SPOUSE_LIRA {a}")
a = get_value(report, 2023, 'SPOUSE_LIF')
print(f"SPOUSE_LIF {a}")
a = get_value(report, 2023, 'SPOUSE_NON_REGISTERED_ASSET')
print(f"SPOUSE_NON_REGISTERED_ASSET  {a}")

a = get_value(report, 2040, 'HOME')
print(f"HOME  {a}")