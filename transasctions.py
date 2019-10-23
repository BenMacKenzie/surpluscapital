from utils import *




def rrsp_converstion_to_rrif(transactions, book, client):
    if client:
        rrspAccount = "rrspAccount"
        rrifAccount = "rrifAccount"
    else:
        rrspAccount = "rrspAccountSp"
        rrifAccount = "rrifAccountSp"

    createTransaction(transactions, "debit", rrspAccount, book[rrspAccount], "rrsp conversion")
    createTransaction(transactions, "credit", rrifAccount, book[rrspAccount], "rrsp conversion")


def get_mandatory_rrif_withdrawals(transactions, book, year):
    if (parameters["age"] + year > 65) and (book["rrif"] > 0):
        createTransaction(transactions,"debit", "rrif", book["rrif"] / 20, "mandatory rrif withdrawal")
        createTransaction(transactions,"credit", "clearing", book["rrif"] / 20, "mandatory rrif withdrawal")
    if (parameters["spouse_age"] + year > 65) and (book["rrifSp"] > 0):
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
    createTransaction(transactions,"debit", "clearing", (amount * (total - bookvalue) / total) * parameters["tax_rate"], "tax on sale of asset")


def process_pensions(transactions, year, pensions):
    for pension in pensions:
        if pension["start_year"] <= year and pension["end_year"] >= year:
            createTransaction(transactions, "credit", "clearing", get_future_value(year, pension["amount"], pension["index_rate"]), pension["name"])

def generate_base_transactions(transactions, current_book):

    year = current_book["year"]

    process_pensions(transactions, year, parameters["pensions"])

    for account in ["regularAsset", "regularAssetSp"]:
        createTransaction(transactions,"credit", account, current_book[account] * parameters["growth_rate"], "capital appreciation")
        createTransaction(transactions,"credit", "clearing", current_book[account] * parameters["income_rate"], "dividends and interest")
        createTransaction(transactions,"debit", "clearing", current_book[account] * parameters["income_rate"] * parameters["tax_rate"], "tax on dividends and interest")

    for account in ["rrsp", "rrspSp"]:
        if (current_book[account] > 0):
            createTransaction(transactions,"credit", account, current_book[account] * parameters["growth_rate"], "growth")
            createTransaction(transactions,"credit", account, current_book[account] * parameters["income_rate"], "interest and dividend")


    get_mandatory_rrif_withdrawals(transactions,current_book, year)

    createTransaction(transactions,"debit", "clearing", get_future_value(year, parameters["income_requirements"], parameters["inflation"]), "living expense")



def meet_cash_req_from_regular_asset(transactions, book, client):
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

