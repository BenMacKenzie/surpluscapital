from  engine import get_projection
import json
from test_utils import get_value

data = {'parameters':
            {'growth_rate': 0.015, 'income_rate': 0.015, 'inflation': 0.025, 'interest_rate': 0, 'start_year': 2023, 'client_age': 55, 'client_life_expectancy': 100, 'spouse': True, 'spouse_age': 65, 'spouse_life_expectancy': 95, 'end_year': 2068, 'end_balance': 500000, 'oas_clawback': {'base': 72000, 'index': 0.02}, 'personal_exemption': {'base': 12896, 'index': 0.02}, 'tax_rate': {'marginal': [[12070, 0], [50000, 0.25], [90000, 0.35], [200000, 0.45]], 'top': 0.54}, 'province': 'Ontario',
             'pensions': [{'person': 'client', 'name': 'CPP', 'start_year': 2028, 'end_year': 2068, 'amount': 2500, 'index_rate': 0.025},
                          {'person': 'client', 'name': 'OAS', 'start_year': 2033, 'end_year': 2068, 'amount': 3000, 'index_rate': 0.025},
                          {'person': 'client', 'name': 'OTHER_PENSION', 'start_year': 2036, 'end_year': 2068, 'amount': 6000, 'index_rate': 0.025},
                          {'person': 'spouse', 'name': 'CPP', 'start_year': 2023, 'end_year': 2053, 'amount': 3000, 'index_rate': 0.025},
                          {'person': 'spouse', 'name': 'OTHER_PENSION', 'start_year': 2023, 'end_year': 2053, 'amount': 5600, 'index_rate': 0.025},
                          {'person': 'spouse', 'name': 'OAS', 'start_year': 2023, 'end_year': 2053, 'amount': 3000, 'index_rate': 0.025}],
             'incomes': [{'person': 'client', 'start_year': 2023, 'end_year': 2023, 'amount': 10000, 'index_rate': 0.025},
                         {'person': 'spouse', 'start_year': 2025, 'end_year': 2025, 'amount': 11000, 'index_rate': 0.025},
                         {'person': 'client', 'start_year': 2024, 'end_year': 2024, 'amount': 12000, 'index_rate': 0.025},
                         {'person': 'spouse', 'start_year': 2026, 'end_year': 2026, 'amount': 9500, 'index_rate': 0.025}],
             'pli': [{'person': 'client', 'amount': 100000}, {'person': 'spouse', 'amount': 200000}],
             'income_requirements': [{'person': 'client', 'type': 'ANNUAL_RETIREMENT_EXPENSES', 'start_year': 2023, 'end_year': 2068, 'amount': 10000, 'index_rate': 0.025},
                                     {'person': 'client', 'type': 'HEALTH_CARE_EXPENSES', 'start_year': 2023, 'end_year': 2068, 'amount': 11000, 'index_rate': 0.025},
                                     {'person': 'spouse', 'type': 'ANNUAL_RETIREMENT_EXPENSES', 'start_year': 2023, 'end_year': 2053, 'amount': 12000, 'index_rate': 0.025},
                                     {'person': 'spouse', 'type': 'HEALTH_CARE_EXPENSES', 'start_year': 2023, 'end_year': 2053, 'amount': 12000, 'index_rate': 0.025},
                                     {'person': 'client', 'type': 'ONE_OFF_EXPENSES', 'start_year': 2023, 'end_year': 2023, 'amount': 400, 'index_rate': 0.025},
                                     {'person': 'spouse', 'type': 'ONE_OFF_EXPENSES', 'start_year': 2024, 'end_year': 2024, 'amount': 500, 'index_rate': 0.025}],
             'charitable_donations': [{'person': 'client', 'start_year': 2023, 'end_year': 2023, 'amount': 200, 'index_rate': 0.025},
                                      {'person': 'spouse', 'start_year': 2023, 'end_year': 2023, 'amount': 300, 'index_rate': 0.025}]},
        'start_book': {'joint': {'CLEARING': 0, 'HOME': 800000, 'sell_home': 2050},
                       'client': {'TFSA': 1000, 'RRSP': 2000, 'RRIF': 3000, 'LIRA': 4000, 'LIF': 5000, 'NON_REGISTERED_ASSET': 40000, 'NON_REGISTERED_BOOK_VALUE': 10000},
                       'spouse': {'TFSA': 1000, 'RRSP': 2000, 'RRIF': 3000, 'LIRA': 4000, 'LIF': 5000, 'NON_REGISTERED_ASSET': 60000, 'NON_REGISTERED_BOOK_VALUE': 20000}}

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

