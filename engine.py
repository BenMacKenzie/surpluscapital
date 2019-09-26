






class Balance:

    def __init__(self, params, year, open_balance):
        self.params = params
        self.year = year
        self.open_balance = open_balance
        self.income_requirements = self.get_future_value(params["inflation"], params["income_requirements"], year)
        self.pension_income = params["pension_income"]
        self.income_from_assets = self.open_balance * params["ror"]
        self.total_income = self.income_from_assets + self.pension_income
        self.taxes = self.total_income * params["tax_rate"]


        self.surplus_income = self.total_income - self.income_requirements - self.taxes

        if self.surplus_income > 0:
            self.open_asset_delta = self.surplus_income

        else:
            self.open_asset_delta = self.surplus_income / (1 - params["tax_rate"])

        self.end_year_balance = self.open_balance + self.open_asset_delta


    def get_next_year(self):
        return Balance(self.params, self.year+1, self.end_year_balance)

    def get_future_value(self, rate, base, year):
        return base * (1 + rate) ** (year - self.params["start_year"])



    def print(self):
        print(str(self.year) + " " + str(self.end_year_balance) + " ")


def project(params):
    projection = []
    current_year = Balance(params, params["start_year"], params["start_open_balance"])
    for i in range(params["start_year"], params["end_year"]+1):
        projection.append(current_year)
        current_year = current_year.get_next_year()

    return projection, projection[-1].end_year_balance



def find_essential_capital():

    params = {
        "ror": 0.06,
        "inflation": 0.03,
        "start_year": 2019,
        "age": 65,
        "spouse_age": 60,
        "start_open_balance": 1000000,
        "book_value": 0,
        "sp_open_balance": 0,
        "registered_balance": 0,
        "sp_registered_balance": 0,
        "end_year": 2030,
        "end_balance": 200000,
        "tax_rate": 0.5,
        "income_requirements": 50000,
        "pension_income": 10000
    }
    essential_capital = params["start_open_balance"]
    projection, end = project(params)

    if end < params["end_balance"]:  #there is no surplus capital
        return projection, params["start_open_balance"]

    low = 0
    high = params["start_open_balance"]

    while True:
        params["start_open_balance"] = essential_capital
        projection, end = project(params)

        if abs(end-params["end_balance"]) < 1:
            return projection, essential_capital
        elif end > params["end_balance"]:
            high = essential_capital
            essential_capital = (high + low) / 2
        else:
            low = essential_capital
            essential_capital = (high + low) / 2









projection, essential_capital = find_essential_capital()

print(essential_capital)

for year in projection:
    year.print()








