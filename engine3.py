
from transasctions import *
import logging
import requests


responst = requests.get("ji")

logging.error("hi")


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





