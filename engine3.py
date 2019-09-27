model_inputs = {
        "growth_rate": 0.06,
        "income_rate": 0.02,
        "inflation": 0.0,
        "start_year": 2019,
        "age": 65,
        "spouse_age": 60,
        "regularAsset": 500000,
        "regularAssetSp": 1000000,
        "regularAssetBookValue": 0,
        "regularAssetSpBookValue": 0,
        "rrsp": 100000,
        "rrspSp": 0,
        "rrif": 100000,
        "rrifSp": 0,
        "end_year": 2030,
        "end_balance": 500000,
        "tax_rate": 0.5,
        "income_requirements": 70000,
        "pension_income": 10000
    }




def createTransaction(transactions, type, account, amount, desc=""):
    transactions.append(
        {
            "type"  : type,
            "account" : account,
            "amount": amount,
            "desc": desc

        }
    )


def get_start_book():
    book = {}
    book["regularAsset"] = model_inputs["regularAsset"]
    book["regularAssetSp"] = model_inputs["regularAssetSp"]
    book["regularAssetBookValue"] = model_inputs["regularAssetBookValue"]
    book["regularAssetSpBookValue"] = model_inputs["regularAssetSpBookValue"]
    book["rrsp"] = model_inputs["rrsp"]
    book["rrspSp"] = model_inputs["rrspSp"]
    book["rrif"] = model_inputs["rrif"]
    book["rrifSp"] = model_inputs["rrifSp"]
    book["clearing"]=0
    book["year"] = model_inputs["start_year"]


    return book




def get_future_value(current_year, value, factor):
    return value * (1 + factor) ** (current_year - model_inputs["start_year"])



def process_transactions(book, transactions):
    book = book.copy()
    for transaction in transactions:

        if transaction["type"] == "debit":
            book[transaction["account"]] -= transaction["amount"]
        else:
            book[transaction["account"]] += transaction["amount"]
    return book


def rrsp_converstion_to_rrif(transactions, book, client):
    if client:
        rrspAccount = "rrspAccount"
        rrifAccount = "rrifAccount"

    createTransaction(transactions, "debit", rrspAccount, book[rrspAccount], "rrsp conversion")
    createTransaction(transactions, "credit", rrifAccount, book[rrspAccount], "rrsp conversion")




def get_mandatory_rrif_withdrawals(transactions, book, year):
    if (model_inputs["age"] + year > 65) and (book["rrif"] > 0):
        createTransaction(transactions,"debit", "rrif", book["rrif"] / 20, "mandatory rrif withdrawal")
        createTransaction(transactions,"credit", "clearing", book["rrif"] / 20, "mandatory rrif withdrawal")
    if (model_inputs["spouse_age"] + year > 65) and (book["rrifSp"] > 0):
        createTransaction(transactions, "debit", "rrifSp", book["rrifSp"] / 20, "mandatory rrif withdrawal")
        createTransaction(transactions, "credit", "clearing", book["rrifSp"] / 20, "mandatory rrif withdrawal")



def sell_regular_asset(transactions, client, book, amount):

    if client:
        account = "regularAsset"
        bookValue = "regularAssetBookValue"
    else:
        account = "regularAssetSp"
        bookValue = "regularAssetSpBookValue"

    total = book[account]
    bookvalue = book[bookValue]

    createTransaction(transactions,"debit", account, amount, "sell asset")
    createTransaction(transactions,"debit", bookValue, (amount / total) * bookvalue)
    createTransaction(transactions,"credit", "clearing", amount)
    createTransaction(transactions,"debit", "clearing", (amount * (total - bookvalue) / total) * model_inputs["tax_rate"], "tax on sale of asset" )








def generate_base_transactions(transactions, current_book):

    year = current_book["year"]

    createTransaction(transactions, "debit", "clearing",
                      get_future_value(year, model_inputs["pension_income"], model_inputs["inflation"]),
                      "pension_income")

    for account in ["regularAsset", "regularAssetSp"]:
        createTransaction(transactions,"credit", account, current_book[account] * model_inputs["growth_rate"], "capital appreciation")
        createTransaction(transactions,"credit", "clearing", current_book[account] * model_inputs["income_rate"], "dividends and interest")
        createTransaction(transactions,"debit", "clearing",current_book[account] * model_inputs["income_rate"] * model_inputs["tax_rate"], "tax on dividends and interest" )

    for account in ["rrsp", "rrspSp"]:
        if (current_book[account] > 0):
            createTransaction(transactions,"credit", account, current_book[account] * model_inputs["growth_rate"], "growth")
            createTransaction(transactions,"credit", account, current_book[account] * model_inputs["income_rate"], "interest and dividend")


    get_mandatory_rrif_withdrawals(transactions,current_book, year)
    createTransaction(transactions,"debit", "clearing", get_future_value(year, model_inputs["income_requirements"], model_inputs["inflation"]), "living expense")




def amount_of_regular_asset_to_sell(book, client, need):
    if client:
        account = "regularAsset"
        bookValue = "regularAssetBookValue"
    else:
        account = "regularAssetSp"
        bookValue = "regularAssetSpBookValue"

    a = (book[account]- book[bookValue])/book[account]
    b = a * model_inputs["tax_rate"]

    x = need / (1 - b)

    return x


def meet_cash_req_from_regular_asset(transactions,book, client):
    if client:
        account = "regularAsset"

    else:
        account = "regularAssetSp"

    needs = 0 - book["clearing"]
    if book[account] <= 0:
        return

    regular_asset_needed = amount_of_regular_asset_to_sell(book, client, needs)
    if regular_asset_needed <= book[account]:
        sell_regular_asset(transactions, client, book, regular_asset_needed)
    else:
        sell_regular_asset(transactions, client, book, book[account])



def invest_funds(transactions,book):
    createTransaction(transactions,"credit", "regularAsset",  book["clearing"], "invest available funds")
    createTransaction(transactions,"debit", "clearing",  book["clearing"])


def get_capital(book):
    total = 0
    total += book["regularAsset"]
    total += book["regularAssetSp"]
    total += book["rrsp"]
    total += book["rrspSp"]
    total += book["rrif"]
    total += book["rrifSp"]
    return total

def simulate_one_year(start_book):
    transactions = []
    generate_base_transactions(transactions, start_book)
    book = process_transactions(start_book, transactions)

    if book["clearing"] < 0:
        meet_cash_req_from_regular_asset(transactions, book, True)
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

    for i in range(model_inputs["start_year"], model_inputs["end_year"]):
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


def find_essential_capital():

    book = get_start_book()
    low = 0
    high = get_capital(book)
    essential_capital = high
    desired_end_balance = get_future_value(model_inputs["end_year"], model_inputs["end_balance"], model_inputs["inflation"])

    end_capital, sim = create_projection(book)
    if end_capital < desired_end_balance:
        print("no surplus")
        return end_capital, sim


    while True:
        book = get_start_book()
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



sim, sc = find_essential_capital()
print_list(sim)
print_list(sc)
print(get_capital(sim[-1]))

#todo...mandatory rrsp conversion to rrif, sale of house, receipt of asset.





