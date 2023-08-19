from transactions import Account, Transaction, TransactionType
from tax import amount_of_non_registered_asset_to_sell

parameters = {
        "growth_rate": 0.05,
        "income_rate": 0.02,
        "inflation": 0.02,
        "interest_rate": 0.03,
        "oas_clawback" : {"base": 72000, "index": 0.0},
        "personal_exemption": {"base": 12896, "index": 0.02},
        "start_year": 2023,
        "client_age": 65,
        "client_life_expectancy": 95,
        "spouse": True,
        "spouse_age": 65,
        "spouse_life_expectancy": 95,
        "end_year": 2044,
        "end_balance": 1000000,
        "province": "Ontario",
        "pensions": [{"person": "client", "name": "OAS", "start_year": 2030, "end_year": 2053, "amount": 12000, "index_rate": 0.04},
                     {"person": "spouse", "name": "OAS", "start_year": 2023, "end_year": 2053, "amount": 12000, "index_rate": 0.04}],
        "incomes": [{"person": "spouse", "start_year": 2023, "end_year": 2050, "amount": 60000, "index_rate": 0.04}],
        "pli": [{"person": "client", "amount": 50000}],
        "income_requirements": [{"person": "spouse", "type": "ANNUAL_RETIREMENT_EXPENSES", "start_year": 2023,
                                 "end_year": 2050, "amount": 60000, "index_rate": 0.05},
                                ],
        "charitable_donations": [{"person": "spouse", "start_year": 2023, "end_year": 2050, "amount": 1000, "index_rate": 0.05}]
        }


oas = Transaction('credit', 'spouse', Account.CLEARING, 13498, TransactionType.PENSION_INCOME, 0, 'OAS')
clawback = Transaction('debit', 'spouse', Account.CLEARING, 1184.7, TransactionType.OAS_CLAWBACK)
transactions = [oas, clawback]
tax_rates = {'marginal': [[46226.0, 0.20049999999999998], [50197.0, 0.2415], [92454.0, 0.2965], [100392, 0.3166], [150000.0, 0.37160000000000004], [155625.0, 0.3816], [220000.0, 0.41159999999999997]], 'top': 0.4216}

x = amount_of_non_registered_asset_to_sell(transactions, parameters, 2026, 'spouse', 18.244975000000522, 0.10667697915907356, 78713.3, tax_rates)

print(x)


