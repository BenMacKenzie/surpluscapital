
from enum import Enum
import copy

class Transaction(str, Enum):
    EARNED_INCOME = "EARNED_INCOME",
    PENSION_INCOME = "PENSION_INCOME",
    DIVIDEND_INCOME = "DIVIDEND_INCOME",
    ASSET_GROWTH = "ASSET_GROWTH",
    HOME_APPRECIATION = "HOME_APPRECIATION",
    SALE_OF_REGULAR_ASSET = "SALE_OF_REGULAR_ASSET",
    RRSP_CONVERSION = "RRSP_CONVERSION",
    RRIF_WITHDRAWAL = "RRIF_WITHDRAWAL",
    RRSP_WITHDRAWAL = "RRSP_WITHDRAWAL",
    TFSA_WITHDRAWAL = "TFSA_WITHDRAWAL",
    BOOK_VALUE_ADJUSTMENT = "BOOK_VALUE_ADJUSTMENT",
    SALE_OF_HOME = "SALE_OF_HOME",
    REGULAR_ASSET_INVESTMENT = "REGULAR_ASSET_INVESTMENT",
    NEEDS = "NEEDS",
    TAX =  "TAX",
    REMOVE_SURPLUS_CAPITAL = "REMOVE_SURPLUS_CAPITAL"


class Person(Enum):
    CLIENT = 1,
    SPOUSE = 2,
    JOINT = 3  #needs, clearning account,



class Account(str, Enum):
    REGULAR="NON_REGISTERED_ASSET",
    REGULAR_BOOK_VALUE = "REGULAR_BOOK_VALUE"
    RRSP="RRSP",
    RRIF="RRIF",
    TFSA = "TFSA",
    HOME = "HOME",
    CLEARING = "CLEARING"




def get_future_value(start_year, future_year, value, factor):
    return round(value * (1 + factor) ** (future_year - start_year),0)


def createTransaction(transactions, entry_type, person, account, amount, transaction_type, book_value=0, desc=""):
    transactions.append(
        {
            "entry_type"  : entry_type,
            "person": person,
            "account" : account,
            "amount": amount,
            "transaction_type" : transaction_type,
            "book_value" : book_value,
            "desc": desc

        }
    )

def get_capital(book):

    total = book['joint'][Account.CLEARING]
    total += book['joint'][Account.HOME]

    total += book['client'][Account.REGULAR]
    total += book['client'][Account.RRIF]
    total += book['client'][Account.RRSP]
    total += book['client'][Account.TFSA]

    if 'spouse' not in book.keys():
        return total

    total += book['spouse'][Account.REGULAR]
    total += book['spouse'][Account.RRIF]
    total += book['spouse'][Account.RRSP]
    total += book['spouse'][Account.TFSA]

    return total



def process_transactions(book, transactions):
    book = copy.deepcopy(book)

    for transaction in transactions:
        person = transaction["person"]
        account = transaction["account"]
        amount = transaction["amount"]
        type = transaction["entry_type"]

        if type == "debit":
            book[person][account] -= amount
        else:
            book[person][account] += amount

    return book



#fix to work with complex tax code
def amount_of_regular_asset_to_sell(value, bookvalue, need, tax_rate):
    a = (value - bookvalue)/ value
    b = a * tax_rate * 0.5
    x = need / (1 - b)
    return round(x,0)


#def amont_of_regular_asset_to_sell2(value, bookvalue, need, starting_income, tax_rates):





def get_age(start_age, start_year, current_year):
    age = start_age + current_year - start_year
    return age





def rrsp_converstion_to_rrif(transactions, book, person):

    createTransaction(transactions, "debit", person, Account.RRSP, book[person][Account.RRSP], Transaction.RRSP_CONVERSION, "rrsp conversion")
    createTransaction(transactions, "credit", person, Account.RRIF, book[person][Account.RRIF], Transaction.RRSP_CONVERSION, "rrsp conversion")



def get_mandatory_rrif_withdrawals(transactions, book, age, person, tax_rate):

    if book[person][Account.RRIF] > 0 and age >= 65:
        amount = round(book[person][Account.RRIF] / (90 - age), 0)
        createTransaction(transactions, "debit", book[person][Account.RRIF], amount, Transaction.RRIF_WITHDRAWAL, "mandatory rrif withdrawal")
        createTransaction(transactions, "credit", book["joint"][Account.CLEARING], amount, Transaction.RRIF_WITHDRAWAL, "mandatory rrif withdrawal")
        #createTransaction(transactions, "debit", "clearing", amount*tax_rate, "tax on rrif withdrawal")



def sell_regular_asset(transactions, person, book, amount, tax_rate):

    total = book[person][Account.REGULAR]
    bookvalue =book[person][Account.REGULAR_BOOK_VALUE]
    createTransaction(transactions,"debit", person, Account.REGULAR, amount, Transaction.SALE_OF_REGULAR_ASSET, book_value=round((amount / total) * bookvalue,0), desc="sell asset")
    createTransaction(transactions,"debit", person, Account.REGULAR_BOOK_VALUE, round((amount / total) * bookvalue,0), Transaction.BOOK_VALUE_ADJUSTMENT)
    createTransaction(transactions,"credit", "joint", Account.CLEARING, amount, Transaction.SALE_OF_REGULAR_ASSET)
 #   createTransaction(transactions,"debit", "clearing", round((amount * (total - bookvalue) / total) * tax_rate * .5,0), "tax on sale of asset")


def sell_deferred(transactions, person,  account, amount, tax_rate):
    if account == Account.RRSP:
        transaction=Transaction.RRSP_WITHDRAWAL
    elif account == Account.RRIF:
        transaction = Transaction.RRIF_WITHDRAWAL
    else:
        return

    createTransaction(transactions, "debit", person, account, amount, transaction)
    createTransaction(transactions, "credit", "joint", Account.CLEARING, amount, transaction)
#   createTransaction(transactions, "debit", "clearing", round(amount * tax_rate,0), "tax on sale of rrsp")


def sell_tfsa(transactions, person, amount):
    createTransaction(transactions, "debit", person, Account.TFSA, amount, Transaction.TFSA_WITHDRAWAL)
    createTransaction(transactions, "credit", "joint", Account.CLEARING, amount, Transaction.TFSA_WITHDRAWAL)


def process_pensions(transactions, start_year, year, pensions, tax_rate):
    for pension in pensions:
        if pension["start_year"] <= year and pension["end_year"] >= year:
            pension_amount= get_future_value(start_year, year, pension["amount"], pension["index_rate"])
            createTransaction(transactions, "credit", "joint",Account.CLEARING,pension_amount, Transaction.PENSION_INCOME)
            #createTransaction(transactions, "debit", "joint", "clearing", round(pension_amount * tax_rate, 0), "tax on " + pension["name"])

def _calculate_tax(taxable_income, tax_rates):
    #tax rates: {"marginal": [(15,000.0.1), (30,000,0.4)], "top": 0.5}
    base = 0
    tax = 0
    for (level, rate) in tax_rates["marginal"]:
        if taxable_income <= level:
            tax += (taxable_income - base) * rate
            return tax
        else:
            tax += (level - base) * rate

    tax += (taxable_income - ["marginal"][-1][0]) * tax_rates["top"]

    return tax




#def calculate_tax(transactions, tax_rate):






def generate_base_transactions(transactions, current_book, parameters):

    year = current_book["year"]
    createTransaction(transactions, "debit", "joint", Account.CLEARING, get_future_value(parameters["start_year"], year, parameters["income_requirements"], parameters["inflation"]), Transaction.NEEDS, "living expense")
    process_pensions(transactions, parameters["start_year"], year, parameters["pensions"], parameters["tax_rate"])

    if get_age(year, parameters['start_year'], parameters['client_age']) == 71:
        rrsp_converstion_to_rrif(transactions, current_book,'client' )

    if parameters["spouse"] and get_age(year, parameters['start_year'], parameters['spouse_age']) == 71:
        rrsp_converstion_to_rrif(transactions, current_book, 'spouse')

    if "sell_home" in parameters.keys() and parameters["sell_home"] == year:
        createTransaction(transactions, "credit", "joint", Account.CLEARING, current_book["joint"][Account.HOME],Transaction.SALE_OF_HOME)
        createTransaction(transactions, "debit", "joint",  Account.HOME, current_book["joint"][Account.HOME],Transaction.SALE_OF_HOME)


    current_book = process_transactions(current_book, transactions)

    if current_book["joint"][Account.HOME] > 0:
        createTransaction(transactions, "credit", "joint", Account.HOME, round(current_book["joing"][Account.HOME] * parameters["inflation"], 0), Transaction.HOME_APPRECIATION)

    get_mandatory_rrif_withdrawals(transactions, current_book, get_age(year, parameters['start_year'], parameters['client_age']), 'client', parameters["tax_rate"])

    if parameters["spouse"]:
        get_mandatory_rrif_withdrawals(transactions, current_book, get_age(year, parameters['start_year'], parameters['spouse_age']), 'spouse', parameters["tax_rate"])

    #can consolidate with below...since tax will be done elsewhere...
    for person in ["client", "spouse"]:
        if(current_book[person][Account.REGULAR] > 0 and parameters["growth_rate"] > 0):
            createTransaction(transactions,"credit", person, Account.REGULAR, round(current_book[person][Account.REGULAR] * parameters["growth_rate"],0), Transaction.ASSET_GROWTH)
        if (current_book[person][Account.REGULAR] > 0 and parameters["income_rate"] > 0):
            createTransaction(transactions,"credit",'joint', Account.CLEARING, round(current_book[person][Account.REGULAR] * parameters["income_rate"],0),Transaction.DIVIDEND_INCOME)
          #  createTransaction(transactions,"debit", Account.CLEARING, round(current_book[person][Account.REGULAR] * parameters["income_rate"] * parameters["tax_rate"],0), "tax on dividends and interest")

    for person in ["client", "spouse"]:
        for account in [Account.RRSP, Account.RRSP, Account.TFSA]:
            if (current_book[person][account] > 0 and parameters["growth_rate"] > 0):
                createTransaction(transactions,"credit", person, account, round(current_book[person][account] * parameters["growth_rate"],0), Transaction.ASSET_GROWTH)
            if (current_book[person][account] > 0 and parameters["income_rate"] > 0):
                createTransaction(transactions,"credit", person, account, round(current_book[person][account] * parameters["income_rate"],0), Transaction.DIVIDEND_INCOME)

    #tax = calculate_tax(transactions, parameters['tax_rate'])


def meet_cash_req_from_regular_asset(transactions, book, person, tax_rate):


    needs = 0 - book['joint'][Account.CLEARING]
    if book[person][Account.REGULAR] <= 0:
        return

    regular_asset_needed = amount_of_regular_asset_to_sell(book[person][Account.REGULAR], book[person][Account.REGULAR_BOOK_VALUE], needs, tax_rate)
    if regular_asset_needed <= book[person][Account.REGULAR]:
        sell_regular_asset(transactions, person, book, regular_asset_needed, tax_rate)
    else:
        sell_regular_asset(transactions, person, book, book[person][Account.REGULAR], tax_rate)


def meet_cash_req_from_deferred(transactions, book, person, account, tax_rate):

    needs = 0 - book['joint'][Account.CLEARING]

    if book[person][account] <= 0:
        return

    deferred_asset_needed = round(needs / (1 - tax_rate),0)

    if deferred_asset_needed <= book[person][account]:
        sell_deferred(transactions, person, account, deferred_asset_needed, tax_rate)
    else:
        sell_deferred(transactions, account,  book[person][account], tax_rate)


def meet_cash_req_from_tfsa(transactions, book, person):

    needs = 0 - book['joint'][Account.CLEARING]

    if book[person][Account.TFSA] <= 0:
        return

    if needs <= book[person][Account.TFSA]:
        sell_tfsa(transactions, person, needs)
    else:
        sell_tfsa(transactions, person, book[person][Account.TFSA])



def invest_funds(transactions,book):
    createTransaction(transactions, "credit", "client",  Account.REGULAR,  book["joint"][Account.CLEARING], Transaction.REGULAR_ASSET_INVESTMENT)
    createTransaction(transactions, "debit", "joint", Account.CLEARING,  book["joint"][Account.CLEARING], Transaction.REGULAR_ASSET_INVESTMENT)

