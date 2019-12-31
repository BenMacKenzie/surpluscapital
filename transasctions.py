from utils import *


def rrsp_converstion_to_rrif(transactions, book, rrspAccount, rrifAccount):


    createTransaction(transactions, "debit", rrspAccount, book[rrspAccount], "rrsp conversion")
    createTransaction(transactions, "credit", rrifAccount, book[rrspAccount], "rrsp conversion")


#use real rrif schedule
def get_mandatory_rrif_withdrawals(transactions, book, age, account, tax_rate):

    if book[account] > 0 and age >= 65:
        amount = round(book[account] / (90 - age), 0)
        createTransaction(transactions, "debit", account, amount, "mandatory rrif withdrawal")
        createTransaction(transactions, "credit", "clearing", amount, "mandatory rrif withdrawal")
        createTransaction(transactions, "debit", "clearing", amount*tax_rate, "tax on rrif withdrawal")



def sell_regular_asset(transactions, client, book, amount, tax_rate):

    if client:
        account = "regularAsset"
        bookValue = "regularAssetBookValue"
    else:
        account = "regularAssetSp"
        bookValue = "regularAssetSpBookValue"

    total = book[account]
    bookvalue = book[bookValue]

    createTransaction(transactions,"debit", account, amount, "sell asset")
    createTransaction(transactions,"debit", bookValue, round((amount / total) * bookvalue,0))
    createTransaction(transactions,"credit", "clearing", amount)
    createTransaction(transactions,"debit", "clearing", round((amount * (total - bookvalue) / total) * tax_rate * .5,0), "tax on sale of asset")


def sell_rrsp(transactions, account, amount, tax_rate):
    createTransaction(transactions, "debit", account, amount, "sell " + account)
    createTransaction(transactions, "credit", "clearing", amount)
    createTransaction(transactions, "debit", "clearing", round(amount * tax_rate,0), "tax on sale of rrsp")



def sell_tfsa(transactions, account, amount):
    createTransaction(transactions, "debit", account, amount, "sell " + account)
    createTransaction(transactions, "credit", "clearing", amount)


def process_pensions(transactions, start_year, year, pensions, tax_rate):
    for pension in pensions:
        if pension["start_year"] <= year and pension["end_year"] >= year:
            pension_amount= get_future_value(start_year, year, pension["amount"], pension["index_rate"])
            createTransaction(transactions, "credit", "clearing",pension_amount, pension["name"])
            createTransaction(transactions, "debit", "clearing", round(pension_amount * tax_rate, 0), "tax on " + pension["name"])



def generate_base_transactions(transactions, current_book, parameters):

    year = current_book["year"]
    createTransaction(transactions, "debit", "clearing", get_future_value(parameters["start_year"], year, parameters["income_requirements"], parameters["inflation"]), "living expense")
    process_pensions(transactions, parameters["start_year"], year, parameters["pensions"], parameters["tax_rate"])

    if get_age(year, parameters['start_year'], parameters['client_age']) == 71:
        rrsp_converstion_to_rrif(transactions, current_book, 'rrsp', 'rrif' )

    if parameters["spouse"] and get_age(year, parameters['start_year'], parameters['spouse_age']) == 71:
        rrsp_converstion_to_rrif(transactions, current_book, 'rrspSp', 'rrifSp')

    if "sell_home" in parameters.keys() and parameters["sell_home"] == year:
        createTransaction(transactions, "credit", "clearing", current_book["home"], "sell home")
        createTransaction(transactions, "debit", "home", current_book["home"], "sell home")



    #now let's roll this book forward:
    current_book = process_transactions(current_book, transactions)

    if current_book["home"] > 0:
        createTransaction(transactions, "credit", "home", round(current_book["home"] * parameters["inflation"], 0), "home appreciation")

    get_mandatory_rrif_withdrawals(transactions, current_book, get_age(year, parameters['start_year'], parameters['client_age']), 'rrif', parameters["tax_rate"])

    if parameters["spouse"]:
        get_mandatory_rrif_withdrawals(transactions, current_book, get_age(year, parameters['start_year'], parameters['spouse_age']), 'rrifSp', parameters["tax_rate"])

    for account in ["regularAsset", "regularAssetSp"]:
        if(current_book[account] > 0 and parameters["growth_rate"] > 0):
            createTransaction(transactions,"credit", account, round(current_book[account] * parameters["growth_rate"],0), "capital appreciation on " + str(current_book[account]))
        if (current_book[account] > 0 and parameters["income_rate"] > 0):
            createTransaction(transactions,"credit", "clearing", round(current_book[account] * parameters["income_rate"],0), "dividends and interest")
            createTransaction(transactions,"debit", "clearing", round(current_book[account] * parameters["income_rate"] * parameters["tax_rate"],0), "tax on dividends and interest")

    for account in ["rrsp", "rrspSp"]:
        if (current_book[account] > 0 and parameters["growth_rate"] > 0):
            createTransaction(transactions,"credit", account, round(current_book[account] * parameters["growth_rate"],0), "growth")
        if (current_book[account] > 0 and parameters["income_rate"] > 0):
            createTransaction(transactions,"credit", account, round(current_book[account] * parameters["income_rate"],0), "interest and dividend")

    for account in ["tfsa", "tfsaSp"]:
        if (current_book[account] > 0 and parameters["growth_rate"] > 0):
            createTransaction(transactions, "credit", account, round(current_book[account] * parameters["growth_rate"],0), "growth")
        if (current_book[account] > 0 and parameters["income_rate"] > 0):
            createTransaction(transactions, "credit", account, round(current_book[account] * parameters["income_rate"],0), "interest and dividend")



def meet_cash_req_from_regular_asset(transactions, book, client, tax_rate):
    if client:
        account = "regularAsset"
        bookValue = "regularAssetBookValue"

    else:
        account = "regularAssetSp"
        bookValue = "regularAssetSpBookValue"

    needs = 0 - book["clearing"]
    if book[account] <= 0:
        return

    regular_asset_needed = amount_of_regular_asset_to_sell(book[account], book[bookValue], needs, tax_rate)
    if regular_asset_needed <= book[account]:
        sell_regular_asset(transactions, client, book, regular_asset_needed, tax_rate)
    else:
        sell_regular_asset(transactions, client, book, book[account], tax_rate)


def meet_cash_req_from_deferred(transactions, book, account, tax_rate):

    needs = 0 - book["clearing"]

    if book[account] <= 0:
        return

    deferred_asset_needed = round(needs / (1 - tax_rate),0)
    if deferred_asset_needed <= book[account]:
        sell_rrsp(transactions, account, deferred_asset_needed, tax_rate)
    else:
        sell_rrsp(transactions, account, book[account], tax_rate)


def meet_cash_req_from_tfsa(transactions, book, account):
    needs = 0 - book["clearing"]

    if book[account] <= 0:
        return

    if needs <= book[account]:
        sell_tfsa(transactions, account, needs)
    else:
        sell_tfsa(transactions, account, book[account])



def invest_funds(transactions,book):
    createTransaction(transactions,"credit", "regularAsset",  book["clearing"], "invest available funds")
    createTransaction(transactions,"debit", "clearing",  book["clearing"])

