
from transasctions import *
import json
import pandas as pd
import numpy as np



PARAMETERS = {
        "growth_rate": 0.05,
        "income_rate": 0.02,
        "inflation": 0.02,
        "start_year": 2020,
        "client_age": 67,
        "spouse": True,
        "spouse_age": 63,
        "end_year": 2044,
        "end_balance": 100000,
        "tax_rate": {"marginal": [(15000., 0.1), (30000, 0.4)], "top": 0.5},
        "pensions": [
        {"name": "client_cpp",
         "person": "client",
         "amount": 16000,
         "start_year": 2022,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "spouse_cpp",
         "person": "spouse",
         "amount": 16000,
         "start_year": 2022,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "client_oas",
         "person": "client",
         "amount": 7200,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "spouse_oas",
         "person": "spouse",
         "amount": 7200,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "client_pension",
         "person": "client",
         "amount": 0,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         },
        {"name": "spouse_pension",
         "person": "spouse",
         "amount": 0,
         "start_year": 2019,
         "end_year": 2043,
         "index_rate": 0.02
         }
        ],
        "income_requirements": 140000,
        }

START_BOOK = {
        "joint" : {Account.CLEARING: 0,
                   Account.HOME: 0},
        "client" : {
            Account.REGULAR: 800000,
            Account.REGULAR_BOOK_VALUE: 800000,
            Account.TFSA: 1000000,
            Account.RRSP: 0,
            Account.RRIF: 0
        },

        "spouse": {
            Account.REGULAR: 1000000,
            Account.REGULAR_BOOK_VALUE: 500000,
            Account.TFSA: 0,
            Account.RRSP: 0,
            Account.RRIF: 0
        },


}

START_SURPLUS_CAPITAL_BOOK = {
    "joint": {Account.CLEARING: 0,
              Account.HOME: 0},
    "client": {
        Account.REGULAR: 0,
        Account.REGULAR_BOOK_VALUE: 0,
        Account.TFSA: 0,
        Account.RRSP: 0,
        Account.RRIF: 0
    },

    "spouse": {
        Account.REGULAR: 0,
        Account.REGULAR_BOOK_VALUE: 0,
        Account.TFSA: 0,
        Account.RRSP: 0,
        Account.RRIF: 0
    },

}

def get_projection(data):

    start_book= data["start_book"]
    parameters = data["parameters"]
    start_surplus_capital_book =  {
        "joint": {Account.CLEARING: 0,
                  Account.HOME: 0},
        "client": {
            Account.REGULAR: 0,
            Account.REGULAR_BOOK_VALUE: 0,
            Account.TFSA: 0,
            Account.RRSP: 0,
            Account.RRIF: 0
        },

        "spouse": {
            Account.REGULAR: 0,
            Account.REGULAR_BOOK_VALUE: 0,
            Account.TFSA: 0,
            Account.RRSP: 0,
            Account.RRIF: 0
        }
    }

    start_surplus_capital_book['year'] = parameters["start_year"]
    start_book["year"]=parameters["start_year"]


    def simulate_one_year(start_book, year):
        transactions = []
        generate_base_transactions(transactions, start_book, parameters)
        book = process_transactions(start_book, transactions)

        print(book['joint'][Account.CLEARING])

        if book['joint'][Account.CLEARING] > 0:
            invest_funds(transactions, book, parameters)

        else:
            #client regular asset

            meet_cash_req_from_regular_asset(transactions, book, "client", parameters["tax_rate"])
            book = process_transactions(start_book, transactions)

            #spouse regular asset
            if book['joint'][Account.CLEARING] < 0:
                meet_cash_req_from_regular_asset(transactions, book, "spouse", parameters["tax_rate"])
                book = process_transactions(start_book, transactions)

            # client tfsa
            if book['joint'][Account.CLEARING] < 0:
                meet_cash_req_from_tfsa(transactions, book, "client")
                book = process_transactions(start_book, transactions)

            #spouse tfsa
            if book['joint'][Account.CLEARING] < 0:
                meet_cash_req_from_tfsa(transactions, book, "spouse")
                book = process_transactions(start_book, transactions)

            #client rrsp
            if book['joint'][Account.CLEARING] < 0:
                meet_cash_req_from_deferred(transactions, book, "client", Account.RRSP, parameters["tax_rate"])
                book = process_transactions(start_book, transactions)

            #spouse rrsp
            if book['joint'][Account.CLEARING] < 0:
                meet_cash_req_from_deferred(transactions, book, "spouse", Account.RRSP, parameters["tax_rate"])
                book = process_transactions(start_book, transactions)

            # client rrif
            if book['joint'][Account.CLEARING] < 0:
                meet_cash_req_from_deferred(transactions, book, "client", Account.RRIF, parameters["tax_rate"])
                book = process_transactions(start_book, transactions)

            # spouse rrif
            if book['joint'][Account.CLEARING] < 0:
                meet_cash_req_from_deferred(transactions, book, "spouse", Account.RRIF, parameters["tax_rate"])
                _ = process_transactions(start_book, transactions)



        book = process_transactions(start_book, transactions)
        book["year"] = year
        book["transactions"] = transactions
        return book



    def create_projection(book, sc=None):
        sim = []

        if sc:
            book["transactions"] = sc
        else:
            book["transactions"] = []

        for i in range(parameters["start_year"], parameters["end_year"]+1):
            d = {}
            d['start'] = book
            book = simulate_one_year(book, i)
            d['end'] = book
            sim.append(d)

            #this become starting book for next year..just as reference
            book = book.copy()
            book['year'] += 1
            #book.pop('transactions')



        return get_capital(d['end']), sim

    #set level of essential capital by debiting accounts...note that the meaning of the essential capital is dependend on order

    def set_essential_capital(book, essential_capital):
        transactions = []

        delta = get_capital(book) - essential_capital

        if delta <= 0:
            return transactions

        if parameters['spouse']:
            persons = ['client', 'spouse']
        else:
            persons = ['client']


        for person in persons:
            if book[person][Account.REGULAR] > delta:
                createTransaction(transactions, "debit", person, Account.REGULAR, delta, TransactionType.REMOVE_SURPLUS_CAPITAL)
                createTransaction(transactions, "debit", person, Account.REGULAR_BOOK_VALUE, delta * book[person][Account.REGULAR_BOOK_VALUE] / book[person][Account.REGULAR],
                                  TransactionType.REMOVE_SURPLUS_CAPITAL)
                delta = 0

            elif book[person][Account.REGULAR] > 0:
                createTransaction(transactions, "debit", person, Account.REGULAR, book[person][Account.REGULAR], TransactionType.REMOVE_SURPLUS_CAPITAL)
                createTransaction(transactions, "debit", person, Account.REGULAR_BOOK_VALUE, book[person][Account.REGULAR_BOOK_VALUE], TransactionType.REMOVE_SURPLUS_CAPITAL)
                delta -= book[person][Account.REGULAR]

            if delta == 0:
                return transactions


        for person in persons:

            if book[person][Account.TFSA] > delta:
                createTransaction(transactions, "debit", person, Account.TFSA, delta, TransactionType.REMOVE_SURPLUS_CAPITAL)
                delta = 0

            elif book[person][Account.TFSA] > 0:
                createTransaction(transactions, "debit", person, Account.TFSA, book[person][Account.TFSA],
                                  TransactionType.REMOVE_SURPLUS_CAPITAL)

                delta -= book[person][Account.TFSA]

            if delta == 0:
                return transactions


        for person in persons:

            if book[person][Account.RRSP] > delta:
                createTransaction(transactions, "debit", person, Account.RRSP, delta, TransactionType.REMOVE_SURPLUS_CAPITAL)
                delta = 0

            elif book[person][Account.RRSP] > 0:
                createTransaction(transactions, "debit", person, Account.RRSP, book[person][Account.RRSP],
                                  TransactionType.REMOVE_SURPLUS_CAPITAL)

                delta -= book[person][Account.RRSP]

            if delta == 0:
                return transactions


        for person in persons:

            if book[person][Account.RRIF] > delta:
                createTransaction(transactions, "debit", person, Account.RRIF, delta, TransactionType.REMOVE_SURPLUS_CAPITAL)
                delta = 0

            elif book[person][Account.RRIF] > 0:
                createTransaction(transactions, "debit", person, Account.RRIF, book[person][Account.RRIF],
                                  TransactionType.REMOVE_SURPLUS_CAPITAL)

                delta -= book[person][Account.RRIF]

            if delta == 0:
                return transactions


        return transactions


    def create_report(essential_capital_projection):


        reporting_transactions  = ["NEEDS", "EARNED_INCOME", "PENSION_INCOME", "DIVIDEND_INCOME", "SALE_OF_REGULAR_ASSET",
                                   "RRSP_WITHDRAWAL", "RRIF_WITHDRAWAL", "TFSA_WITHDRAWAL", "TAX"]

        spouse_reporting_transactions = ["SPOUSE_EARNED_INCOME", "SPOUSE_PENSION_INCOME", "SPOUSE_DIVIDEND_INCOME", "SPOUSE_SALE_OF_REGULAR_ASSET",
                                   "SPOUSE_RRSP_WITHDRAWAL", "SPOUSE_RRIF_WITHDRAWAL", "SPOUSE_TFSA_WITHDRAWAL", "SPOUSE_TAX" ]

        if parameters["spouse"]:
            reporting_transactions += spouse_reporting_transactions

        num_years = len(essential_capital_projection)

        df_t = pd.DataFrame(np.zeros((num_years, len(reporting_transactions))))
        df_t.columns = reporting_transactions

        for i in range(len(essential_capital_projection)):
            for t in essential_capital_projection[i]["end"]["transactions"]:
                t_type =  t["transaction_type"].value
                if t["person"] == "spouse":
                    t_type = "SPOUSE_" + t_type

                if t_type in reporting_transactions:
                    if t_type in ["NEEDS", "TAX", "SPOUSE_TAX"]  and t["entry_type"] == "debit":
                        df_t.iloc[i][t_type] += t["amount"]

                    elif  t["entry_type"] == "credit":
                            df_t.iloc[i][t_type] += t["amount"]


        spouse_columns = {"NON_REGISTERED_ASSET": "SPOUSE_NON_REGISTERED_ASSET", "REGULAR_BOOK_VALUE": "SPOUSE_REGULAR_BOOK_VALUE", "RRSP": "SPOUSE_RRSP", "RRIF": "SPOUSE_RRIF", "TFSA": "SPOUSE_TFSA", "year": "spouse_year"}

        client_proj = [record['start']['client'] for record in essential_capital_projection[:-1]]
        client_proj.append(essential_capital_projection[-1]['end']['client'])

        spouse_proj = [record['start']['spouse'] for record in essential_capital_projection[:-1]]
        spouse_proj.append(essential_capital_projection[-1]['end']['spouse'])


        joint_proj = [record['start']['joint'] for record in essential_capital_projection[:-1]]
        joint_proj.append(essential_capital_projection[-1]['end']['joint'])

        for i in range(len(essential_capital_projection)):
            client_proj[i]["year"] = essential_capital_projection[i]["start"]["year"]
            #spouse_proj[i]["year"] = essential_capital_projection[i]["start"]["year"]


        df_c = pd.DataFrame(client_proj)
        df_s = pd.DataFrame(spouse_proj)
        df_s.rename(columns=spouse_columns, inplace=True)
        df_j = pd.DataFrame(joint_proj)

        df = pd.concat([df_c, df_s, df_j, df_t], axis=1)

        df = df.round(0)

        col_names = [y for y in df["year"]]


        df.drop(['year'], 1, inplace=True)

        df = df.T

        df.columns = col_names

        df = df.reset_index()


        df.rename(columns={'index': 'year'}, inplace=True)


        return df


    #TODO...problem with transactions...in first year, start transactions are just handling surplus capital....the real transactions for the
    #year are in end, subsequently, tranaction are in start....or possibly first entry in project is not the first year...
    def find_essential_capital(start_book):
        low = 0
        high = get_capital(start_book)
        essential_capital = high

        #make adjustment if you don't want to sell home.
        #if start_book["joint"][Account.HOME] > parameters["end_balance"]  and  "sell_home" not in parameters.keys():
        #    parameters["end_balance"] = start_book["joint"][Account.HOME]


        desired_end_balance = get_future_value(parameters["start_year"],parameters["end_year"], parameters["end_balance"], parameters["inflation"])

        end_capital, sim = create_projection(start_book)
        if end_capital < desired_end_balance:
            print("no surplus")
            return sim, []


        print(f"essential capital {essential_capital}")

        while True:
            book = start_book
            surplus_cap_transactions = set_essential_capital(book, essential_capital)
            book = process_transactions(book, surplus_cap_transactions)

            end_capital, sim = create_projection(book, surplus_cap_transactions)


            #close enough
            if essential_capital == 0:
                return sim, surplus_cap_transactions

            #if abs(desired_end_balance - end_capital) / essential_capital  < 0.005:
            if abs(desired_end_balance - end_capital)  < 1000:
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


    essential_capital_projection, sc_transactions = find_essential_capital(start_book)

    # reverse transactions
    for t in sc_transactions:
        t["entry_type"] = "credit"

    #remove income requiremenrts and pensions
    parameters["income_requirements"] = 0
    parameters["pensions"] = []


    #project surplus capital.
    surplus_book = process_transactions(start_surplus_capital_book, sc_transactions)
    _, surplus_capital_projection = create_projection(surplus_book)

    a = []

    for i in range(len(essential_capital_projection) - 1):
        a.append([essential_capital_projection[i]["start"]["year"], get_capital(essential_capital_projection[i]["start"]), get_capital(surplus_capital_projection[i]["start"])])

    #report end of year for last year in projection...
    a.append([essential_capital_projection[-1]["end"]["year"], get_capital(essential_capital_projection[-1]["end"]),
              get_capital(surplus_capital_projection[-1]["end"])])

    report = create_report(essential_capital_projection)
    return sc_transactions, essential_capital_projection, surplus_capital_projection, pd.DataFrame(a, columns=["year", "essential", "surplus"]), report





if __name__ == "__main__":
    sc, sim1, sim2, _ = get_projection()
    print("surplus capital = " + str(get_capital(sim2[0]['end'])))
    print(json.dumps(sc))
    print(json.dumps(sim1))
    print(json.dumps(sim2))






#todo: write files, use eums for transactions, report in constant dollars, fix rrif rules, some money is in limbo eg., sale of house, rrif wkthdrawal
#tax based on next year...




