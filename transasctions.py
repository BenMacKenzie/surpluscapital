
from enum import Enum
import copy
import pandas as pd
import os


from tax import amount_of_deferred_asset_to_sell, amount_of_regular_asset_to_sell, _calculate_tax, calculate_marginal_tax

dir = os.path.dirname(__file__)
fn = os.path.join(dir, 'LIF_withdrawal_rates.csv')
lif_withdrawal = pd.read_csv(fn)



class TransactionType(str, Enum):
    EARNED_INCOME = "EARNED_INCOME",
    PENSION_INCOME = "PENSION_INCOME",
    REGULAR_DIVIDEND = "REGULAR_DIVIDEND",
    REGULAR_ASSET_GROWTH = "REGULAR_ASSET_GROWTH",
    REGISTERERD_DIVIDEND = "REGISTERERD_DIVIDEND",
    REGISTERED_ASSET_GROWTH = "REGISTERED_ASSET_GROWTH",
    HOME_APPRECIATION = "HOME_APPRECIATION",
    SALE_OF_REGULAR_ASSET = "SALE_OF_REGULAR_ASSET",
    RRSP_CONVERSION = "RRSP_CONVERSION",
    LIRA_CONVERSION = "LIRA_CONVERSION",
    RRIF_WITHDRAWAL = "RRIF_WITHDRAWAL",
    RRSP_WITHDRAWAL = "RRSP_WITHDRAWAL",
    TFSA_WITHDRAWAL = "TFSA_WITHDRAWAL",
    LIF_WITHDRAWAL = "LIF_WITHDRAWAL",
    BOOK_VALUE_ADJUSTMENT = "BOOK_VALUE_ADJUSTMENT",
    SALE_OF_HOME = "SALE_OF_HOME",
    REGULAR_ASSET_INVESTMENT = "REGULAR_ASSET_INVESTMENT",
    NEEDS = "NEEDS",
    TAX =  "TAX",
    REMOVE_SURPLUS_CAPITAL = "REMOVE_SURPLUS_CAPITAL",
    CHARITABLE_DONATIONS = "CHARITABLE_DONATIONS"



class Account(str, Enum):
    REGULAR="NON_REGISTERED_ASSET",
    REGULAR_BOOK_VALUE = "REGULAR_BOOK_VALUE"
    RRSP="RRSP",
    RRIF="RRIF",
    TFSA = "TFSA",
    LIRA="LIRA",
    LIF="LIF",
    HOME = "HOME",
    CLEARING = "CLEARING"


class Transaction():
    def __init__(self, entry_type, person, account, amount, transaction_type, book_value=0, desc=""):
        self.entry_type = entry_type
        self.person = person
        self.account = account
        self.amount = amount
        self.transaction_type = transaction_type
        self.book_value = book_value
        self.desc = desc



def get_future_value(start_year, future_year, value, factor):
    return round(value * (1 + factor) ** (future_year - start_year),0)


def createTransaction(transactions, entry_type, person, account, amount, transaction_type, book_value=0, desc=""):
    transaction = Transaction(entry_type, person, account, amount, transaction_type, book_value=book_value, desc=desc)

    transactions.append(transaction)

    return transaction


def get_capital(book):

    total = book['joint'][Account.CLEARING]

    total += book['joint'][Account.HOME]

    total += book['client'][Account.REGULAR]
    total += book['client'][Account.RRIF]
    total += book['client'][Account.RRSP]
    total += book['client'][Account.TFSA]
    total += book['client'][Account.LIRA]
    total += book['client'][Account.LIF]

    if 'spouse' not in book.keys():
        return total

    total += book['spouse'][Account.REGULAR]
    total += book['spouse'][Account.RRIF]
    total += book['spouse'][Account.RRSP]
    total += book['spouse'][Account.TFSA]
    total += book['spouse'][Account.LIRA]
    total += book['spouse'][Account.LIF]

    return total



def process_transactions(book, transactions):
    book = copy.deepcopy(book)

    for transaction in transactions:
        person = transaction.person
        account = transaction.account
        amount = transaction.amount
        type = transaction.entry_type

        if account==Account.CLEARING:
            person = "joint"


        if type == "debit":
            book[person][account] -= amount
        else:
            book[person][account] += amount

    return book




def get_taxable_income(transactions, person):
    taxable_income = 0
    taxable = [TransactionType.SALE_OF_REGULAR_ASSET, TransactionType.RRIF_WITHDRAWAL, TransactionType.RRSP_WITHDRAWAL,
               TransactionType.REGULAR_DIVIDEND, TransactionType.PENSION_INCOME, TransactionType.EARNED_INCOME]

    for transaction in transactions:
        if transaction.person == person:
            if transaction.transaction_type in taxable and transaction.entry_type == "credit":
                if transaction.transaction_type== TransactionType.SALE_OF_REGULAR_ASSET:
                    taxable_income += (transaction.amount - transaction.book_value) * 0.5

                else:
                    taxable_income += transaction.amount

    return taxable_income





def get_age(start_age, start_year, current_year):
    age = start_age + current_year - start_year
    return age





def rrsp_converstion_to_rrif(transactions, book, person):

    createTransaction(transactions, "debit", person, Account.RRSP, book[person][Account.RRSP], TransactionType.RRSP_CONVERSION, desc="rrsp conversion")
    createTransaction(transactions, "credit", person, Account.RRIF, book[person][Account.RRSP], TransactionType.RRSP_CONVERSION, desc="rrsp conversion")



def convert_lira_to_lif(transactions, book, person):

    createTransaction(transactions, "debit", person, Account.LIRA, book[person][Account.LIRA], TransactionType.LIRA_CONVERSION, desc="lira conversion")
    createTransaction(transactions, "credit", person, Account.LIF, book[person][Account.LIRA], TransactionType.LIRA_CONVERSION, desc="lira conversion")






def get_mandatory_rrif_withdrawals(transactions, book, age, person, tax_rate):

    if book[person][Account.RRIF] > 0 and age >= 65:
        if age == 90:
            amount = book[person][Account.RRIF]
        else:
            amount = round(book[person][Account.RRIF] / (90 - age), 0)
        createTransaction(transactions, "debit", person, Account.RRIF, amount, TransactionType.RRIF_WITHDRAWAL, desc="mandatory rrif withdrawal")
        createTransaction(transactions, "credit",person, Account.CLEARING, amount, TransactionType.RRIF_WITHDRAWAL, desc="mandatory rrif withdrawal")


def get_mandatory_lif_withdrawals(transactions, book, age, person, tax_rate):

    if book[person][Account.LIF] > 0 and age >= 50:

        rate =  lif_withdrawal.loc[lif_withdrawal['AGE']==age].iloc[0]['MINIMUM']
        amount = book[person][Account.RRIF] * rate  #fix this

        createTransaction(transactions, "debit", person, Account.RRIF, amount, TransactionType.LIF_WITHDRAWAL, desc="mandatory lif withdrawal")
        createTransaction(transactions, "credit",person, Account.CLEARING, amount, TransactionType.LIF_WITHDRAWAL, desc="mandatory lif withdrawal")


def sell_regular_asset(transactions, person, book, amount, tax_rate):
    income = get_taxable_income(transactions, person)
    total = book[person][Account.REGULAR]
    bookvalue =book[person][Account.REGULAR_BOOK_VALUE]
    createTransaction(transactions,"debit", person, Account.REGULAR, amount, TransactionType.SALE_OF_REGULAR_ASSET, book_value=round((amount / total) * bookvalue, 0), desc="sell asset")
    createTransaction(transactions,"debit", person, Account.REGULAR_BOOK_VALUE, round((amount / total) * bookvalue,0), TransactionType.BOOK_VALUE_ADJUSTMENT)
    createTransaction(transactions,"credit", person, Account.CLEARING, amount, TransactionType.SALE_OF_REGULAR_ASSET)

    realized_cap_gain = (amount * (total - bookvalue) / total) * 0.5
    tax = calculate_marginal_tax(income, realized_cap_gain, tax_rate)
    createTransaction(transactions,"debit", person, Account.CLEARING, tax, TransactionType.TAX, desc="tax on sale of asset")



def sell_deferred(transactions, person,  account, amount, tax_rate):
    income = get_taxable_income(transactions, person)
    if account == Account.RRSP:
        transaction=TransactionType.RRSP_WITHDRAWAL
        desc="tax on sale of rrsp"
    elif account == Account.RRIF:
        transaction = TransactionType.RRIF_WITHDRAWAL
        desc="tax on sale of rrif"
    elif account == Account.LIF:
        transaction = TransactionType.LIF_WITHDRAWAL
        desc="tax on sale of lif"
    else:
        return

    createTransaction(transactions, "debit", person, account, amount, transaction)
    createTransaction(transactions, "credit", person, Account.CLEARING, amount, transaction)
    tax = calculate_marginal_tax(income, amount, tax_rate)
    createTransaction(transactions, "debit", person, Account.CLEARING, tax, TransactionType.TAX, desc=desc)



def sell_tfsa(transactions, person, amount):
    createTransaction(transactions, "debit", person, Account.TFSA, amount, TransactionType.TFSA_WITHDRAWAL)
    createTransaction(transactions, "credit", person, Account.CLEARING, amount, TransactionType.TFSA_WITHDRAWAL)


def process_pensions(transactions, start_year, year, pensions):
    for pension in pensions:
        if pension["start_year"] <= year and pension["end_year"] >= year:

            pension_amount= get_future_value(start_year, year, pension["amount"], pension["index_rate"])
            createTransaction(transactions, "credit", pension["person"], Account.CLEARING, pension_amount, TransactionType.PENSION_INCOME, desc=pension["name"])



def process_incomes(transactions, start_year, year, incomes):
    for inccome in incomes:
        if inccome["start_year"] <= year and inccome["end_year"] >= year:

            pension_amount= get_future_value(start_year, year, inccome["amount"], inccome["index_rate"])
            createTransaction(transactions, "credit", inccome["person"], Account.CLEARING, pension_amount, TransactionType.EARNED_INCOME)


def calculate_tax(transactions, person, tax_rates):
    taxable_income=get_taxable_income(transactions, person)
    tax = _calculate_tax(taxable_income, tax_rates)
    return tax




def generate_base_transactions(transactions, current_book, parameters):

    tax_rate = parameters["tax_rate"]
    year = current_book["year"]
    createTransaction(transactions, "debit", "joint", Account.CLEARING, get_future_value(parameters["start_year"], year, parameters["income_requirements"], parameters["inflation"]), TransactionType.NEEDS, desc="living expense")
    createTransaction(transactions, "debit", "joint", Account.CLEARING, get_future_value(parameters["start_year"], year, parameters["charitable_donations"], parameters["inflation"]), TransactionType.CHARITABLE_DONATIONS, desc="living expense")

    process_pensions(transactions, parameters["start_year"], year, parameters["pensions"])
    process_incomes(transactions, parameters["start_year"], year, parameters["incomes"])

    if get_age(year, parameters['start_year'], parameters['client_age']) == 71:
        rrsp_converstion_to_rrif(transactions, current_book,'client' )
        convert_lira_to_lif(transactions, current_book, "client")

    if parameters["spouse"] and get_age(year, parameters['start_year'], parameters['spouse_age']) == 71:
        rrsp_converstion_to_rrif(transactions, current_book, 'spouse')
        convert_lira_to_lif(transactions, current_book, 'spouse')

    if "sell_home" in parameters.keys() and parameters["sell_home"] == year:
        createTransaction(transactions, "credit", "joint", Account.CLEARING, current_book["joint"][Account.HOME], TransactionType.SALE_OF_HOME)
        createTransaction(transactions, "debit", "joint", Account.HOME, current_book["joint"][Account.HOME], TransactionType.SALE_OF_HOME)


    current_book = process_transactions(current_book, transactions)

    if current_book["joint"][Account.HOME] > 0:
        createTransaction(transactions, "credit", "joint", Account.HOME, round(current_book["joint"][Account.HOME] * parameters["inflation"], 0), TransactionType.HOME_APPRECIATION)

    get_mandatory_rrif_withdrawals(transactions, current_book, get_age(year, parameters['start_year'], parameters['client_age']), 'client', parameters["tax_rate"])

    if parameters["spouse"]:
        get_mandatory_rrif_withdrawals(transactions, current_book, get_age(year, parameters['start_year'], parameters['spouse_age']), 'spouse', parameters["tax_rate"])


    for person in ["client", "spouse"]:

        if (current_book[person][Account.REGULAR] > 0 and parameters["growth_rate"] > 0):
            createTransaction(transactions,"credit", person, Account.REGULAR, round(current_book[person][Account.REGULAR] * parameters["growth_rate"],0), TransactionType.REGULAR_ASSET_GROWTH)
        if (current_book[person][Account.REGULAR] > 0 and parameters["income_rate"] > 0):
            createTransaction(transactions,"credit", person, Account.CLEARING, round(current_book[person][Account.REGULAR] * parameters["income_rate"],0), TransactionType.REGULAR_DIVIDEND)

        for account in [Account.RRSP, Account.RRIF, Account.TFSA, Account.LIRA, Account.LIF]:
            if (current_book[person][account] > 0 and parameters["growth_rate"] > 0):
                createTransaction(transactions, "credit", person, account,
                                  round(current_book[person][account] * parameters["growth_rate"], 0),
                                  TransactionType.REGISTERED_ASSET_GROWTH)
            if (current_book[person][account] > 0 and parameters["income_rate"] > 0):
                createTransaction(transactions, "credit", person, account,
                                  round(current_book[person][account] * parameters["income_rate"], 0),
                                  TransactionType.REGISTERERD_DIVIDEND)

    client_tax = calculate_tax(transactions,  "client", tax_rate)
    createTransaction(transactions, "debit", "client", Account.CLEARING, client_tax, TransactionType.TAX, desc="client tax before sale of assets")
    spouse_tax = calculate_tax(transactions, "spouse", tax_rate)
    createTransaction(transactions, "debit", "spouse", Account.CLEARING, spouse_tax, TransactionType.TAX, desc="spouse tax before sale of assets")

def meet_cash_req_from_regular_asset(transactions, book, person, tax_rate, needs, income_limit=0):

    taxable_income = get_taxable_income(transactions, person)
    #needs = 0 - book['joint'][Account.CLEARING]
    if book[person][Account.REGULAR] <= 0:
        return
    book_value_ratio =  (book[person][Account.REGULAR] - book[person][Account.REGULAR_BOOK_VALUE]) / book[person][Account.REGULAR]

    regular_asset_needed = amount_of_regular_asset_to_sell(needs, book_value_ratio, taxable_income, tax_rate)

    if income_limit > 0:
        if taxable_income >= income_limit:
            return #do nothing
        if regular_asset_needed * book_value_ratio + taxable_income > income_limit:
            regular_asset_needed = (income_limit - taxable_income) / book_value_ratio


    if regular_asset_needed <= book[person][Account.REGULAR]:
        sell_regular_asset(transactions, person, book, regular_asset_needed, tax_rate)
    else:
        sell_regular_asset(transactions, person, book, book[person][Account.REGULAR], tax_rate)


def meet_cash_req_from_deferred(transactions, book, person, account, tax_rate, needs, income_limit=0):
    taxable_income = get_taxable_income(transactions, person)
    #needs = 0 - book['joint'][Account.CLEARING]

    if book[person][account] <= 0:
        return

    deferred_asset_needed = amount_of_deferred_asset_to_sell(needs, taxable_income, tax_rate)

    if income_limit > 0:
        if taxable_income > income_limit:
            return
        if deferred_asset_needed + taxable_income > income_limit:
            deferred_asset_needed = income_limit - taxable_income


    if deferred_asset_needed <= book[person][account]:
        sell_deferred(transactions, person, account, deferred_asset_needed, tax_rate)
    else:
        sell_deferred(transactions, person, account,  book[person][account], tax_rate)


def meet_cash_req_from_lif(transactions, book, person, age, tax_rate, needs, income_limit):
    taxable_income = get_taxable_income(transactions, person)
    #needs = 0 - book['joint'][Account.CLEARING]

    if book[person][Account.LIF] <= 0:
        return

    rate = lif_withdrawal.loc[lif_withdrawal['AGE'] == age].iloc[0]['MAXIMUM_ONTARIO']
    max_lif_withdrawal = book[person][Account.LIF] * rate

    deferred_asset_needed = amount_of_deferred_asset_to_sell(needs, taxable_income, tax_rate)

    if income_limit > 0:
        if taxable_income > income_limit:
            return
        if deferred_asset_needed + taxable_income > income_limit:
            deferred_asset_needed = income_limit - taxable_income

    if deferred_asset_needed <= max_lif_withdrawal:
        sell_deferred(transactions, person, Account.LIF, deferred_asset_needed, tax_rate)
    else:
        sell_deferred(transactions, person, Account.LIF,  max_lif_withdrawal, tax_rate)



def meet_cash_req_from_tfsa(transactions, book, person, needs, income_limit):

    taxable_income = get_taxable_income(transactions, person)

    if book[person][Account.TFSA] <= 0:
        return

    if income_limit > 0 and taxable_income >= income_limit:
        return


    if needs <= book[person][Account.TFSA]:
        sell_tfsa(transactions, person, needs)
    else:
        sell_tfsa(transactions, person, book[person][Account.TFSA])



def invest_funds(transactions,book, parameters):
    amount_to_invest = book["joint"][Account.CLEARING]
    createTransaction(transactions, "debit", "joint", Account.CLEARING, book["joint"][Account.CLEARING],
                      TransactionType.REGULAR_ASSET_INVESTMENT)

    if parameters["spouse"]:
        amount_to_invest = amount_to_invest / 2
        createTransaction(transactions, "credit", "client", Account.REGULAR, amount_to_invest, TransactionType.REGULAR_ASSET_INVESTMENT)
        createTransaction(transactions, "credit", "spouse", Account.REGULAR, amount_to_invest,
                          TransactionType.REGULAR_ASSET_INVESTMENT)
        createTransaction(transactions, "credit", "client", Account.REGULAR_BOOK_VALUE, amount_to_invest,
                          TransactionType.REGULAR_ASSET_INVESTMENT)
        createTransaction(transactions, "credit", "spouse", Account.REGULAR_BOOK_VALUE, amount_to_invest,
                          TransactionType.REGULAR_ASSET_INVESTMENT)
    else:
        createTransaction(transactions, "credit", "client", Account.REGULAR, amount_to_invest,
                          TransactionType.REGULAR_ASSET_INVESTMENT)
        createTransaction(transactions, "credit", "client", Account.REGULAR_BOOK_VALUE, amount_to_invest,
                          TransactionType.REGULAR_ASSET_INVESTMENT)
