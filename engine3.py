model_inputs = {
        "growth_rate": 0.06,
        "income_rate": 0.02,
        "inflation": 0.03,
        "start_year": 2019,
        "age": 65,
        "spouse_age": 60,
        "regularAsset": 10000,
        "regularAssetSp": 1000000,
        "regularAssetBookValue": 0,
        "regularAssetSpBookValue": 0,
        "rrsp": 0,
        "rrspSp": 0,
        "rrif": 100000,
        "rrifSp": 0,
        "end_year": 2030,
        "end_balance": 200000,
        "tax_rate": 0.5,
        "income_requirements": 50000,
        "pension_income": 10000
    }


transactions = []

def createTransaction(type, account, amount, desc=""):
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


def rrsp_converstion_to_rrif(book, client):
    if client:
        rrspAccount = "rrspAccount"
        rrifAccount = "rrifAccount"

    createTransaction("debit", rrspAccount, book[rrspAccount], "rrsp conversion")
    createTransaction("credit", rrifAccount, book[rrspAccount], "rrsp conversion")




def get_mandatory_rrif_withdrawals(book, year):
    if (model_inputs["age"] + year > 65) and (book["rrif"] > 0):
        createTransaction("debit", "rrif", book["rrif"] / 20, "mandatory rrif withdrawal")
        createTransaction("credit", "clearing", book["rrif"] / 20, "mandatory rrif withdrawal")
    if (model_inputs["spouse_age"] + year > 65) and (book["rrifSp"] > 0):
        createTransaction("debit", "rrifSp", book["rrifSp"] / 20, "mandatory rrif withdrawal")
        createTransaction("credit", "clearing", book["rrifSp"] / 20, "mandatory rrif withdrawal")



def sell_regular_asset(client, book, amount):

    if client:
        account = "regularAsset"
        bookValue = "regularAssetBookValue"
    else:
        account = "regularAssetSp"
        bookValue = "regularAssetSpBookValue"

    total = book[account]
    bookvalue = book[bookValue]

    createTransaction("debit", account, amount, "sell asset")
    createTransaction("debit", bookValue, (amount / total) * bookvalue)
    createTransaction("credit", "clearing", amount)
    createTransaction("debit", "clearing", (amount * (total - bookvalue) / total) * model_inputs["tax_rate"], "tax on sale of asset" )








def generate_base_transactions(current_book):

    year = current_book["year"]

    createTransaction("debit", "clearing",
                      get_future_value(year, model_inputs["pension_income"], model_inputs["inflation"]),
                      "pension_income")

    for account in ["regularAsset", "regularAssetSp"]:
        createTransaction("credit", account, current_book[account] * model_inputs["growth_rate"], "capital appreciation")
        createTransaction("credit", "clearing", current_book[account] * model_inputs["income_rate"], "dividends and interest")
        createTransaction("debit", "clearing",current_book[account] * model_inputs["income_rate"] * model_inputs["tax_rate"], "tax on dividends and interest" )

    for account in ["rrsp", "rrspSp"]:
        if (current_book[account] > 0):
            createTransaction("credit", account, current_book[account] * model_inputs["growth_rate"], "growth")
            createTransaction("credit", account, current_book[account] * model_inputs["income_rate"], "interest and dividend")


    get_mandatory_rrif_withdrawals(current_book, year)
    createTransaction("debit", "clearing", get_future_value(year, model_inputs["income_requirements"], model_inputs["inflation"]), "living expense")




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


def meet_cash_req_from_regular_asset(book, client):
    if client:
        account = "regularAsset"

    else:
        account = "regularAssetSp"

    needs = 0 - book["clearing"]
    if book[account] <= 0:
        return

    regular_asset_needed = amount_of_regular_asset_to_sell(book, client, needs)
    if regular_asset_needed <= book[account]:
        sell_regular_asset(client, book, regular_asset_needed)
    else:
        sell_regular_asset(client, book, book[account])



def invest_funds(book):
    createTransaction("credit", "regularAsset",  book["clearing"], "invest available funds")
    createTransaction("debit", "clearing",  book["clearing"])




def simulate_one_year(start_book):
    generate_base_transactions(start_book)
    book = process_transactions(start_book, transactions)

    if book["clearing"] < 0:
        meet_cash_req_from_regular_asset(book, True)
        book = process_transactions(start_book, transactions)

        if book["clearing"] < 0:
            meet_cash_req_from_regular_asset(book, False)
            book = process_transactions(start_book, transactions)
    else:
        invest_funds(book)

    book = process_transactions(start_book, transactions)
    book["year"] += 1
    return book


def create_projection():
    sim = []
    book = get_start_book()
    sim.append(book)

    for i in range(model_inputs["start_year"], model_inputs["end_year"]):
        book = simulate_one_year(book)
        sim.append(book)

    for s in sim:
        print(s)



create_projection()

#todo...mandatory rrsp conversion to rrif, sale of house, receipt of asset.





