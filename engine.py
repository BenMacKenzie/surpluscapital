
from transasctions import *
import json


def simulate_one_year(start_book, year):
    transactions = []
    generate_base_transactions(transactions, start_book, parameters)
    book = process_transactions(start_book, transactions)

    if book["clearing"] > 0:
        invest_funds(transactions, book)

    else:
        #client regular asset
        meet_cash_req_from_regular_asset(transactions, book, True, parameters["tax_rate"])
        book = process_transactions(start_book, transactions)

        #spouse regular asset
        if book["clearing"] < 0:
            meet_cash_req_from_regular_asset(transactions, book, False, parameters["tax_rate"])
            book = process_transactions(start_book, transactions)

        # client tfsa
        if book["clearing"] < 0:
            meet_cash_req_from_tfsa(transactions, book, "tfsa")
            book = process_transactions(start_book, transactions)

        #spouse tfsa
        if book["clearing"] < 0:
            meet_cash_req_from_tfsa(transactions, book, "tfsaSp")
            book = process_transactions(start_book, transactions)

        #client rrsp
        if book["clearing"] < 0:
            meet_cash_req_from_deferred(transactions, book, "rrsp", parameters["tax_rate"])
            book = process_transactions(start_book, transactions)

        #spouse rrsp
        if book["clearing"] < 0:
            meet_cash_req_from_deferred(transactions, book, "rrspSp", parameters["tax_rate"])
            book = process_transactions(start_book, transactions)

        # client rrif
        if book["clearing"] < 0:
            meet_cash_req_from_deferred(transactions, book, "rrif", parameters["tax_rate"])
            book = process_transactions(start_book, transactions)

        # spouse rrif
        if book["clearing"] < 0:
            meet_cash_req_from_deferred(transactions, book, "rrifSp", parameters["tax_rate"])
            _ = process_transactions(start_book, transactions)



    book = process_transactions(start_book, transactions)
    book["year"] = year
    book["transactions"] = transactions
    return book



def create_projection(book, sc=None):
    sim = []

    if sc:
        book["transactions"] = sc

    for i in range(parameters["start_year"], parameters["end_year"]+1):
        d = {}
        d['start'] = book
        book = simulate_one_year(book, i)
        d['end'] = book
        sim.append(d)

        #this become starting book for next year..just as reference
        book = book.copy()
        book['year'] += 1
        book.pop('transactions')



    return get_capital(d['end']), sim





#set level of essential capital by debiting accounts...note that the meaning of the essential capital is dependend on order

def set_essential_capital(book, essential_capital):
    transactions = []

    delta = get_capital(book) - essential_capital

    if delta <= 0:
        return transactions

    if book["regularAsset"] > 0:
        if book["regularAsset"] > delta:
            createTransaction(transactions, "debit", "regularAsset", delta, "remove surplus capital")
            createTransaction(transactions, "debit", "regularAssetBookValue", delta * book["regularAssetBookValue"]/ book["regularAsset"], "remove surplus capital book value")
            delta = 0

        else:
            createTransaction(transactions, "debit", "regularAsset", book["regularAsset"], "remove surplus capital")
            createTransaction(transactions, "debit", "regularAssetBookValue", book["regularAssetBookValue"], "remove surplus capital book value")

            delta -= book["regularAsset"]

    if delta == 0:
        return transactions

    if book["regularAssetSp"] > 0:
        if book["regularAssetSp"] > delta:
            createTransaction(transactions, "debit", "regularAssetSp", delta, "remove surplus capital")
            createTransaction(transactions, "debit", "regularAssetSpBookValue", delta * book["regularAssetSpBookValue"] / book["regularAssetSp"], "remove surplus capital book value")

            delta = 0
        else:
            createTransaction(transactions, "debit", "regularAssetSp", book["regularAssetSp"], "remove surplus capital")
            createTransaction(transactions, "debit", "regularAssetSpBookValue", book["regularAssetSpBookValue"], "remove surplus capital book value")
            delta -= book["regularAssetSp"]

    if delta == 0:
        return transactions

    if book["tfsa"] > 0:
        if book["tfsa"] > delta:
            createTransaction(transactions, "debit", "tfsa", delta, "remove surplus capital")
            delta = 0
        else:
            createTransaction(transactions, "debit", "tfsa", book["tfsa"], "remove surplus capital")
            delta -= book["tfsa"]

    if delta == 0:
        return transactions

    if book["tfsaSp"] > 0:
        if book["tfsaSp"] > delta:
            createTransaction(transactions, "debit", "tfsaSp", delta, "remove surplus capital")
            delta = 0
        else:
            createTransaction(transactions, "debit", "tfsaSp", book["tfsaSp"], "remove surplus capital")
            delta -= book["tfsaSp"]

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

    return transactions





def find_essential_capital(start_book):
    low = 0
    high = get_capital(start_book)
    essential_capital = high
    desired_end_balance = get_future_value(parameters["start_year"],parameters["end_year"], parameters["end_balance"], parameters["inflation"])

    end_capital, sim = create_projection(start_book)
    if end_capital < desired_end_balance:
        print("no surplus")
        return sim, []


    while True:
        book = start_book
        surplus_cap_transactions = set_essential_capital(book, essential_capital)
        book = process_transactions(book, surplus_cap_transactions)

        end_capital, sim = create_projection(book, surplus_cap_transactions)
        print(end_capital)
        print(essential_capital)
        #close enough
        if abs(desired_end_balance - end_capital) < 1000:
            return sim, surplus_cap_transactions

        #there is no essential capital..all surplus
        elif (end_capital > desired_end_balance) and (essential_capital < 1):
            return sim, surplus_cap_transactions

        elif end_capital > desired_end_balance:
            high = essential_capital
            essential_capital = round((high + low) / 2,0)
        else:
            low = essential_capital
            essential_capital = round((high + low) / 2,0)


'''
parameters = {
        "growth_rate": 0.05,
        "income_rate": 0,
        "inflation": 0.02,
        "start_year": 2019,
        "age": 67,
        "spouse_age": 67,
        "end_year": 2043,
        "end_balance": 2000000,
        "tax_rate": 0.25,
        "pensions": [
        {"name": "client_cpp",
         "amount": 16000,
         "start_year": 2022,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "spouse_cpp",
         "amount": 16000,
         "start_year": 2022,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "client_oas",
         "amount": 7200,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "spouse_oas",
         "amount": 7200,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "client_pension",
         "amount": 50000,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "spouse_pension",
         "amount": 30000,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         }
        ],

        "income_requirements": 200000,
        }


start_book = {
        "regularAsset": 1000000,
        "regularAssetBookValue": 1000000,
        "regularAssetSp": 1000000,
        "regularAssetSpBookValue": 1000000,
        "rrsp": 900000,
        "rrspSp": 900000,
        "tfsa": 100000,
        "tfsaSp": 0,
        "rrif": 0,
        "rrifSp": 0,
        "home" : 0,
        "year": parameters["start_year"],
        "clearing": 0
}
'''
parameters = {
        "growth_rate": 0.05,
        "income_rate": 0,
        "inflation": 0.02,
        "start_year": 2019,
        "age": 67,
        "spouse_age": 0,
        "end_year": 2043,
        "end_balance": 30000,
        "tax_rate": 0.25,
        "pensions": [
        ],
        "income_requirements": 48000,
        }


start_book = {
        "regularAsset": 1000000,
        "regularAssetBookValue": 1000000,
        "regularAssetSp": 0,
        "regularAssetSpBookValue": 0,
        "rrsp": 0,
        "rrspSp": 0,
        "tfsa": 0,
        "tfsaSp": 0,
        "rrif": 0,
        "rrifSp": 0,
        "home" : 0,
        "year": parameters["start_year"],
        "clearing": 0
}

start_surplus_capital_book  = {
        "regularAsset": 0,
        "regularAssetBookValue": 0,
        "regularAssetSp": 0,
        "regularAssetSpBookValue": 0,
        "rrsp": 0,
        "rrspSp": 0,
        "tfsa": 0,
        "tfsaSp": 0,
        "rrif": 0,
        "rrifSp": 0,
        "year": parameters["start_year"],
        "home": 0,
        "clearing": 0
}


sim, sc = find_essential_capital(start_book)



# simulate how surplus capital will grow...actually..probabably no need to do this..
# reverse transactions
for t in sc:
    t["type"] = "credit"

#remove income requiremenrts and pensions
parameters["income_requirements"] = 0
parameters["pensions"] = []


#project surplus capital.
surplus_book = process_transactions(start_surplus_capital_book, sc)
_, sim2= create_projection(surplus_book)

print("surplus capital = " + str(get_capital(sim2[0]['end'])))
print(json.dumps(sc))
print(json.dumps(sim))
print(json.dumps(sim2))




#todo: round values, write files, use eums for transactions, report in constant dollars, fix rrif rules, some money is in limbow eg., sale of house, rrif wkthdrawal

#tax based on next year...




