
def get_future_value(current_year, value, factor):
    return value * (1 + factor) ** (current_year - parameters["start_year"])


def amount_of_regular_asset_to_sell(book, client, need):
    if client:
        account = "regularAsset"
        bookValue = "regularAssetBookValue"
    else:
        account = "regularAssetSp"
        bookValue = "regularAssetSpBookValue"

    a = (book[account]- book[bookValue])/book[account]
    b = a * parameters["tax_rate"]

    x = need / (1 - b)

    return x

def get_capital(book):
    total = 0
    total += book["regularAsset"]
    total += book["regularAssetSp"]
    total += book["rrsp"]
    total += book["rrspSp"]
    total += book["rrif"]
    total += book["rrifSp"]
    return total


class Simulation:
    def __init__(self, parameters, start_book):
        self.parameters = parameters
        self.book = start_book
        self.transactions = []



    def createTransaction(self, type, account, amount, desc=""):
        self.transactions.append(
        {
            "type"  : type,
            "account" : account,
            "amount": amount,
            "desc": desc

        }
    )


    #do i need to copy?
    def process_transactions(self, transactions):
        book = self.book
        for transaction in transactions:
            if transaction["type"] == "debit":
                book[transaction["account"]] -= transaction["amount"]
            else:
                book[transaction["account"]] += transaction["amount"]
        return book


    def rrsp_converstion_to_rrif(self, client):
        if client:
            rrspAccount = "rrspAccount"
            rrifAccount = "rrifAccount"
        else:
            rrspAccount = "rrspAccountSp"
            rrifAccount = "rrifAccountSp"

        self.createTransaction("debit", rrspAccount, self.book[rrspAccount], "rrsp conversion")
        self.createTransaction("credit", rrifAccount, self.book[rrspAccount], "rrsp conversion")


    def get_mandatory_rrif_withdrawals(self, year):
        if (self.parameters["age"] + year > 65) and (self.book["rrif"] > 0):
            self.createTransaction("debit", "rrif", book["rrif"] / 20, "mandatory rrif withdrawal")
            self.createTransaction("credit", "clearing", book["rrif"] / 20, "mandatory rrif withdrawal")
        if (self.parameters["spouse_age"] + year > 65) and (book["rrifSp"] > 0):
            self.createTransaction("debit", "rrifSp", book["rrifSp"] / 20, "mandatory rrif withdrawal")
            self.createTransaction("credit", "clearing", book["rrifSp"] / 20, "mandatory rrif withdrawal")

    def sell_regular_asset(self, client, amount):

        if client:
            account = "regularAsset"
            bookValue = "regularAssetBookValue"
        else:
            account = "regularAssetSp"
            bookValue = "regularAssetSpBookValue"

        total = self.book[account]
        bookvalue = self.book[bookValue]

        self.createTransaction("debit", account, amount, "sell asset")
        self.createTransaction("debit", bookValue, (amount / total) * bookvalue)
        self.createTransaction("credit", "clearing", amount)
        self.createTransaction("debit", "clearing", (amount * (total - bookvalue) / total) * self.parameters["tax_rate"], "tax on sale of asset")


    def process_pensions(self, year, pensions):
        for pension in pensions:
            if pension["start_year"] <= year and pension["end_year"] >= year:
                self.createTransaction("credit", "clearing", get_future_value(year, pension["amount"], pension["index_rate"]), pension["name"])

    def generate_base_transactions(self):

        year = self.book["year"]

        self.process_pensions(year, parameters["pensions"])

        for account in ["regularAsset", "regularAssetSp"]:
            self.createTransaction("credit", account, self.book[account] * self.parameters["growth_rate"], "capital appreciation")
            self.createTransaction("credit", "clearing", self.book[account] * self.parameters["income_rate"], "dividends and interest")
            self.createTransaction("debit", "clearing", self.book[account] * self.parameters["income_rate"] * self.parameters["tax_rate"], "tax on dividends and interest")

        for account in ["rrsp", "rrspSp"]:
            if (self.book[account] > 0):
                self.createTransaction("credit", account, self.book[account] * self.parameters["growth_rate"], "growth")
                self.createTransaction("credit", account, self.book[account] * self.parameters["income_rate"], "interest and dividend")


        self.get_mandatory_rrif_withdrawals(year)

        self.createTransaction("debit", "clearing", get_future_value(year, self.parameters["income_requirements"], self.parameters["inflation"]), "living expense")







    def meet_cash_req_from_regular_asset(self, book, client):
        if client:
            account = "regularAsset"

        else:
            account = "regularAssetSp"

        needs = 0 - self.book["clearing"]
        if book[account] <= 0:
            return

        regular_asset_needed = amount_of_regular_asset_to_sell(self.book, client, needs)
        if regular_asset_needed <= book[account]:
            self.sell_regular_asset(client, self.book, regular_asset_needed)
        else:
            self.sell_regular_asset(client, self.book, self.book[account])



    def invest_funds(self,book):
        self.createTransaction("credit", "regularAsset",  book["clearing"], "invest available funds")
        self.createTransaction("debit", "clearing",  book["clearing"])



def simulate_one_year(parameters, start_book):
    sim = Simulation(parameters, start_book)
    sim.generate_base_transactions(start_book)
    book = sim.process_transactions()

    if book["clearing"] < 0:
        sim.meet_cash_req_from_regular_asset(True)
        book = process_transactions(start_book, transactions)

        if book["clearing"] < 0:
            meet_cash_req_from_regular_asset(transactions, book, False)
            book = process_transactions(start_book, transactions)
    else:
        invest_funds(transactions, book)

    book = process_transactions(start_book, transactions)
    book["year"] += 1
    return book


def create_projection(book):
    sim = []
    sim.append(book)

    for i in range(parameters["start_year"], parameters["end_year"]):
        book = simulate_one_year(book)
        sim.append(book)

    return get_capital(book), sim



#todo..adjust bookvalue aswell


def set_essential_capital(book, essential_capital):
    transactions = []

    delta = get_capital(book) - essential_capital

    if delta <= 0:
        return transactions

    if book["regularAsset"] > 0:
        if book["regularAsset"] > delta:
            createTransaction(transactions, "debit", "regularAsset", delta, "remove surplus capital")
            delta = 0
        else:
            createTransaction(transactions, "debit", "regularAsset", book["regularAsset"], "remove surplus capital")
            delta -= book["regularAsset"]

    if delta == 0:
        return transactions

    if book["regularAssetSp"] > 0:
        if book["regularAssetSp"] > delta:
            createTransaction(transactions, "debit", "regularAssetSp", delta, "remove surplus capital")
            delta = 0
        else:
            createTransaction(transactions, "debit", "regularAssetSp", book["regularAssetSp"], "remove surplus capital")
            delta -= book["regularAssetSp"]

    if delta == 0:
        return transactions

    if book["rrsp"] > 0:
        if book["rrsp"] > delta:
            createTransaction(transactions, "debit", "rrsp", delta, "remove surplus capital")
            delta = 0
        else:
            createTransaction(transactions, "debit", "rrsp", book["rrsp"], "remove surplus capital")
            delta -= book["rrsp"]

    if delta == 0:
        return transactions

    if book["rrspSp"] > 0:
        if book["rrspSp"] > delta:
            createTransaction(transactions, "debit", "rrspSp", delta, "remove surplus capital")
            delta = 0
        else:
            createTransaction(transactions, "debit", "rrspSp", book["rrspSp"], "remove surplus capital")
            delta -= book["rrspSp"]

def print_list(list):
    for l  in list:
        print(l)





def find_essential_capital(start_book):
    low = 0
    high = get_capital(start_book)
    essential_capital = high
    desired_end_balance = get_future_value(parameters["end_year"], parameters["end_balance"], parameters["inflation"])

    end_capital, sim = create_projection(start_book)
    if end_capital < desired_end_balance:
        print("no surplus")
        return sim, []


    while True:
        book = start_book
        surplus_cap_transactions = set_essential_capital(book, essential_capital)
        book = process_transactions(book, surplus_cap_transactions)

        end_capital, sim = create_projection(book)

        if abs(desired_end_balance - end_capital) < 1:
            return sim, surplus_cap_transactions
        elif end_capital > desired_end_balance:
            high = essential_capital
            essential_capital = (high + low) / 2
        else:
            low = essential_capital
            essential_capital = (high + low) / 2



parameters = {
        "growth_rate": 0.06,
        "income_rate": 0.02,
        "inflation": 0.1,
        "start_year": 2019,
        "age": 65,
        "spouse_age": 60,
        "end_year": 2030,
        "end_balance": 500000,
        "tax_rate": 0.5,
        "pensions": [
            {"name": "client_oas",
             "amount": 10000,
             "start_year": 2019,
             "end_year":  2030,
             "index_rate": 0.1
             },
             {"name": "client_cpp",
              "amount": 15000,
              "start_year": 2019,
              "end_year": 2030,
              "index_rate": 0.1
              }
            ],
        "income_requirements": 70000,
        }


start_book = {
        "regularAsset": 500000,
        "regularAssetSp": 1000000,
        "regularAssetBookValue": 0,
        "regularAssetSpBookValue": 0,
        "rrsp": 100000,
        "rrspSp": 0,
        "rrif": 100000,
        "rrifSp": 0,
        "year": parameters["start_year"],
        "clearing": 0
}

start_surplus_capital_book  = {
        "regularAsset": 0,
        "regularAssetSp": 0,
        "regularAssetBookValue": 0,
        "regularAssetSpBookValue": 0,
        "rrsp": 0,
        "rrspSp": 0,
        "rrif": 0,
        "rrifSp": 0,
        "year": parameters["start_year"],
        "clearing": 0
}


sim, sc = find_essential_capital(start_book)
print_list(sim)
print_list(sc)
print(get_capital(sim[-1]))

# reverse transactions
for t in sc:
    t["type"] = "credit"

parameters["income_requirements"] = 0
parameters["pensions"] = []


surplus_book = process_transactions(start_surplus_capital_book, sc)
_, sim= create_projection(surplus_book)
print("surplus")
print_list(sim)




#todo...mandatory rrsp conversion to rrif, sale of house, receipt of asset, project surplus capital, does surplus capital, handle book value of surplus





