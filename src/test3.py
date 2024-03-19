from  engine import get_projection
import json
from test_utils import get_value

data = {
    "parameters": {
        "growth_rate": 0.015,
        "income_rate": 0.015,
        "inflation": 0.02,
        "interest_rate": 0,
        "start_year": 2023,
        "client_age": 55,
        "client_life_expectancy": 100,
        "spouse": True,
        "spouse_age": 65,
        "spouse_life_expectancy": 100,
        "end_year": 2068,
        "end_balance": 100000,
        "oas_clawback": {
            "base": 72000,
            "index": 0.02
        },
        "personal_exemption": {
            "base": 12896,
            "index": 0.02
        },
        "sell_home": 2025,
        "tax_rate": {
            "marginal": [
                [
                    12070,
                    0
                ],
                [
                    50000,
                    0.25
                ],
                [
                    90000,
                    0.35
                ],
                [
                    200000,
                    0.45
                ]
            ],
            "top": 0.54
        },
        "province": "Ontario",
        "pensions": [
            {
                "person": "client",
                "name": "CPP",
                "start_year": 2023,
                "end_year": 2068,
                "amount": 4545,
                "index_rate": 0.02
            },
            {
                "person": "client",
                "name": "OAS",
                "start_year": 2023,
                "end_year": 2068,
                "amount": 300,
                "index_rate": 0.02
            },
            {
                "person": "client",
                "name": "OTHER_PENSION",
                "start_year": 2023,
                "end_year": 2068,
                "amount": 400,
                "index_rate": 0
            },
            {
                "person": "spouse",
                "name": "CPP",
                "start_year": 2023,
                "end_year": 2058,
                "amount": 12,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "name": "OTHER_PENSION",
                "start_year": 2023,
                "end_year": 2058,
                "amount": 12,
                "index_rate": 0
            },
            {
                "person": "spouse",
                "name": "OAS",
                "start_year": 2023,
                "end_year": 2058,
                "amount": 12,
                "index_rate": 0.02
            }
        ],
        "incomes": [
            {
                "person": "client",
                "start_year": 2023,
                "end_year": 2023,
                "amount": 1000,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "start_year": 2023,
                "end_year": 2023,
                "amount": 1000,
                "index_rate": 0.02
            },
            {
                "person": "client",
                "start_year": 2024,
                "end_year": 2024,
                "amount": 2000,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "start_year": 2024,
                "end_year": 2024,
                "amount": 2000,
                "index_rate": 0.02
            }
        ],
        "pli": [
            {
                "person": "client",
                "amount": 10
            },
            {
                "person": "spouse",
                "amount": 10
            }
        ],
        "income_requirements": [
            {
                "person": "client",
                "type": "ANNUAL_RETIREMENT_EXPENSES",
                "start_year": 2023,
                "end_year": 2043,
                "amount": 30,
                "index_rate": 0.02
            },
            {
                "person": "client",
                "type": "HEALTH_CARE_EXPENSES",
                "start_year": 2023,
                "end_year": 2043,
                "amount": 30,
                "index_rate": 0.02
            },
            {
                "person": "client",
                "type": "ANNUAL_RETIREMENT_EXPENSES",
                "start_year": 2044,
                "end_year": 2053,
                "amount": 40,
                "index_rate": 0.02
            },
            {
                "person": "client",
                "type": "HEALTH_CARE_EXPENSES",
                "start_year": 2044,
                "end_year": 2053,
                "amount": 40,
                "index_rate": 0.02
            },
            {
                "person": "client",
                "type": "ANNUAL_RETIREMENT_EXPENSES",
                "start_year": 2054,
                "end_year": 2068,
                "amount": 50,
                "index_rate": 0.02
            },
            {
                "person": "client",
                "type": "HEALTH_CARE_EXPENSES",
                "start_year": 2054,
                "end_year": 2068,
                "amount": 50,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "type": "ANNUAL_RETIREMENT_EXPENSES",
                "start_year": 2023,
                "end_year": 2033,
                "amount": 30,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "type": "HEALTH_CARE_EXPENSES",
                "start_year": 2023,
                "end_year": 2033,
                "amount": 30,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "type": "ANNUAL_RETIREMENT_EXPENSES",
                "start_year": 2034,
                "end_year": 2043,
                "amount": 40,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "type": "HEALTH_CARE_EXPENSES",
                "start_year": 2034,
                "end_year": 2043,
                "amount": 40,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "type": "ANNUAL_RETIREMENT_EXPENSES",
                "start_year": 2044,
                "end_year": 2058,
                "amount": 50,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "type": "HEALTH_CARE_EXPENSES",
                "start_year": 2044,
                "end_year": 2058,
                "amount": 50,
                "index_rate": 0.02
            },
            {
                "person": "client",
                "type": "ONE_OFF_EXPENSES",
                "start_year": 2025,
                "end_year": 2025,
                "amount": 10,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "type": "ONE_OFF_EXPENSES",
                "start_year": 2025,
                "end_year": 2025,
                "amount": 10,
                "index_rate": 0.02
            }
        ],
        "charitable_donations": [
            {
                "person": "client",
                "start_year": 2026,
                "end_year": 2026,
                "amount": 20,
                "index_rate": 0.02
            },
            {
                "person": "spouse",
                "start_year": 2026,
                "end_year": 2026,
                "amount": 20,
                "index_rate": 0.02
            }
        ]
    },
    "start_book": {
        "joint": {
            "CLEARING": 0,
            "HOME": 100000
        },
        "client": {
            "TFSA": 20,
            "RRSP": 20,
            "RRIF": 20,
            "LIRA": 20,

            "LIF": 0,
            "NON_REGISTERED_ASSET": 10,
            "NON_REGISTERED_BOOK_VALUE": 10
        },
        "spouse": {
            "TFSA": 20,
            "RRSP": 20,
            "RRIF": 20,
            "LIRA": 20,
            "LIF": 0,
            "NON_REGISTERED_ASSET": 10,
            "NON_REGISTERED_BOOK_VALUE": 10
        },
        "transactions": []
    }
}
g, report = get_projection(data)
print(g)
print(report)
print(json.dumps(data))
