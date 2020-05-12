
from transasctions import *
import json
import pandas as pd
import numpy as np


def get_projection(data, calculate_surplus_capital=True):

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
                book = process_transactions(start_book, transactions)

            # client lif

            client_age = get_age(parameters["client_age"], parameters["start_year"], year)
            spouse_age = get_age(parameters["spouse_age"], parameters["start_year"], year)

            if book['joint'][Account.CLEARING] < 0:
                meet_cash_req_from_lif(transactions, book, "client", client_age, parameters["tax_rate"])
                book = process_transactions(start_book, transactions)

            # spouse lif

            if book['joint'][Account.CLEARING] < 0:
                meet_cash_req_from_lif(transactions, book, "spouse",  spouse_age, parameters["tax_rate"])
                book = process_transactions(start_book, transactions)

            #last resort..convert LIRA to LIF



            if book['joint'][Account.CLEARING] < 0:
                if client_age >= 55 and book["client"][Account.LIRA] > 0:
                    convert_lira_to_lif(transactions, book, "client")
                    book = process_transactions(start_book, transactions)
                    meet_cash_req_from_lif(transactions, book, "client", client_age, parameters["tax_rate"])
                    book = process_transactions(start_book, transactions)

            if book['joint'][Account.CLEARING] < 0:
                if spouse_age >= 55 and book["spouse"][Account.LIRA] > 0:
                    convert_lira_to_lif(transactions, book, "spouse")
                    book = process_transactions(start_book, transactions)
                    meet_cash_req_from_lif(transactions, book, "spouse", client_age, parameters["tax_rate"])
                    book = process_transactions(start_book, transactions)




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


        reporting_transactions  = ["NEEDS", "CHARITABLE_DONATIONS", "EARNED_INCOME", "OTHER_PENSION", "OAS", "CPP", "REGULAR_DIVIDEND", "REGISTERED_DIVIDEND", "REGULAR_ASSET_GROWTH", "REGISTERED_ASSET_GROWTH", "SALE_OF_REGULAR_ASSET",
                                   "RRSP_WITHDRAWAL", "RRIF_WITHDRAWAL", "TFSA_WITHDRAWAL", "LIF_WITHDRAWAL", "TAX"]

        spouse_reporting_transactions = ["SPOUSE_EARNED_INCOME", "SPOUSE_OTHER_PENSION", "SPOUSE_OAS", "SPOUSE_CPP", "SPOUSE_REGULAR_DIVIDEND", "SPOUSE_REGISTERED_DIVIDEND", "SPOUSE_REGULAR_ASSET_GROWTH", "SPOUSE_REGISTERED_ASSET_GROWTH",
                                         "SPOUSE_SALE_OF_REGULAR_ASSET", "SPOUSE_RRSP_WITHDRAWAL", "SPOUSE_RRIF_WITHDRAWAL", "SPOUSE_TFSA_WITHDRAWAL", "SPOUSE_LIF_WITHDRAWAL", "SPOUSE_TAX" ]

        if parameters["spouse"]:
            reporting_transactions += spouse_reporting_transactions

        num_years = len(essential_capital_projection)

        df_t = pd.DataFrame(np.zeros((num_years, len(reporting_transactions))))
        df_t.columns = reporting_transactions

        for i in range(len(essential_capital_projection)):
            for t in essential_capital_projection[i]["end"]["transactions"]:
                if t.transaction_type == TransactionType.PENSION_INCOME:
                    t_type = t.desc
                else:
                    t_type =  t.transaction_type.value

                if t.person == "spouse":
                    t_type = "SPOUSE_" + t_type

                if t_type in reporting_transactions:
                    if t_type in ["NEEDS", "CHARITABLE_DONATIONS", "TAX", "SPOUSE_TAX"]  and t.entry_type == "debit":
                        df_t.iloc[i][t_type] += t.amount

                    elif  t.entry_type == "credit":
                            df_t.iloc[i][t_type] += t.amount


        spouse_columns = {"NON_REGISTERED_ASSET": "SPOUSE_NON_REGISTERED_ASSET", "REGULAR_BOOK_VALUE": "SPOUSE_REGULAR_BOOK_VALUE", "RRSP": "SPOUSE_RRSP", "RRIF": "SPOUSE_RRIF", "TFSA": "SPOUSE_TFSA", "LIRA": "SPOUSE_LIRA", "LIF": "SPOUSE_LIF", "year": "spouse_year"}

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


        if parameters["spouse"]:
            ordered_columns = ["EARNED_INCOME", "SPOUSE_EARNED_INCOME", "OAS",
                               "SPOUSE_OAS", "CPP", "SPOUSE_CPP",
                               "OTHER_PENSION","SPOUSE_OTHER_PENSION",
                               "REGULAR_DIVIDEND",  "SPOUSE_REGULAR_DIVIDEND",
                               "SALE_OF_REGULAR_ASSET","SPOUSE_SALE_OF_REGULAR_ASSET",
                               "RRSP_WITHDRAWAL",  "SPOUSE_RRSP_WITHDRAWAL",
                               "RRIF_WITHDRAWAL", "SPOUSE_RRIF_WITHDRAWAL",
                               "LIF_WITHDRAWAL", "SPOUSE_LIF_WITHDRAWAL",
                               "TFSA_WITHDRAWAL", "SPOUSE_TFSA_WITHDRAWAL",
                               "total_funds_in",
                               "TAX", "SPOUSE_TAX",
                               "NEEDS", "CHARITABLE_DONATIONS",
                               "total_funds_out",
                               "net_funds_in",
                               "NON_REGISTERED_ASSET", "REGULAR_BOOK_VALUE",
                               "SPOUSE_NON_REGISTERED_ASSET",  "SPOUSE_REGULAR_BOOK_VALUE",
                               "RRSP", "SPOUSE_RRSP",
                               "RRIF", "SPOUSE_RRIF",
                               "LIRA", "SPOUSE_LIRA",
                               "LIF",  "SPOUSE_LIF",
                               "TFSA", "SPOUSE_TFSA",
                               "HOME", "CLEARING", "total_assets"]



            funds_in = df[["EARNED_INCOME", "SPOUSE_EARNED_INCOME", "OAS",
                           "SPOUSE_OAS", "CPP", "SPOUSE_CPP",
                           "OTHER_PENSION", "SPOUSE_OTHER_PENSION",
                           "REGULAR_DIVIDEND", "SPOUSE_REGULAR_DIVIDEND",
                           "SALE_OF_REGULAR_ASSET", "SPOUSE_SALE_OF_REGULAR_ASSET",
                           "RRSP_WITHDRAWAL", "SPOUSE_RRSP_WITHDRAWAL",
                           "RRIF_WITHDRAWAL", "SPOUSE_RRIF_WITHDRAWAL",
                           "LIF_WITHDRAWAL", "SPOUSE_LIF_WITHDRAWAL",
                           "TFSA_WITHDRAWAL", "SPOUSE_TFSA_WITHDRAWAL"]].sum(axis=1)

            df["total_funds_in"] = funds_in

            funds_out = df[[ "TAX", "SPOUSE_TAX",
                               "NEEDS", "CHARITABLE_DONATIONS"]].sum(axis=1)

            df["total_funds_out"] = funds_out

            df["net_funds_in"] = df["total_funds_in"] - df["total_funds_out"]


            total_assets = df[[ "NON_REGISTERED_ASSET", "SPOUSE_NON_REGISTERED_ASSET",
                               "RRSP", "SPOUSE_RRSP", "RRIF", "SPOUSE_RRIF", "TFSA", "SPOUSE_TFSA", "LIRA", "SPOUSE_LIRA", "LIF", "SPOUSE_LIF", "CLEARING", "HOME"]].sum(axis=1)

            df["total_assets"]=total_assets

            df = df[ordered_columns]

        else:
            ordered_columns = ["EARNED_INCOME", "OAS", "CPP", "REGULAR_DIVIDEND", "OTHER_PENSION",
                               "SALE_OF_REGULAR_ASSET",
                               "RRSP_WITHDRAWAL", "RRIF_WITHDRAWAL",
                               "LIF_WITHDRAWAL", "TFSA_WITHDRAWAL",
                               "total_funds_in", "TAX", "NEEDS", "CHARITABLE_DONATIONS", "total_funds_out",
                               "net_funds_in",
                               "NON_REGISTERED_ASSET", "REGULAR_BOOK_VALUE",
                               "RRSP", "RRIF", "TFSA", "LIRA", "LIF",
                               "HOME", "CLEARING", "total_assets"]



            funds_in = df[["EARNED_INCOME",
                           "OAS",
                           "CPP",
                           "OTHER_PENSION",
                           "REGULAR_DIVIDEND",
                           "SALE_OF_REGULAR_ASSET",
                           "RRSP_WITHDRAWAL",
                           "RRIF_WITHDRAWAL",
                           "LIF_WITHDRAWAL",
                           "TFSA_WITHDRAWAL"]].sum(axis=1)

            df["total_funds_in"] = funds_in

            funds_out = df[["TAX",
                            "NEEDS", "CHARITABLE_DONATIONS"]].sum(axis=1)

            df["total_funds_out"] = funds_out

            df["net_funds_in"] = df["total_funds_in"] - df["total_funds_out"]

            total_assets = df[["NON_REGISTERED_ASSET",
                             "RRSP",  "RRIF", "TFSA", "LIRA", "LIF", "HOME", "CLEARING"]].sum(axis=1)

            df["total_assets"] = total_assets

            df = df[ordered_columns]




        df = df.loc[:, (df != 0).any(axis=0)]

        df = df.applymap(lambda x: '{:,.0f}'.format(x))
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
    #for t in sc_transactions:
    #    t.entry_type = "credit"

    #remove income requiremenrts and pensions
    #parameters["income_requirements"] = 0
    #parameters["charitable_donations"] = 0
    #parameters["pensions"] = []
    #parameters["incomes"] = []


    #project surplus capital.
    #surplus_book = process_transactions(start_surplus_capital_book, sc_transactions)
    #_, surplus_capital_projection = create_projection(surplus_book)

    _, surplus_capital_projection = create_projection(start_book)

    a = []

    for i in range(len(essential_capital_projection) - 1):
        a.append([essential_capital_projection[i]["start"]["year"], get_capital(essential_capital_projection[i]["start"]), get_capital(surplus_capital_projection[i]["start"])- get_capital(essential_capital_projection[i]["start"])])

    #report end of year for last year in projection...
    a.append([essential_capital_projection[-1]["end"]["year"], get_capital(essential_capital_projection[-1]["end"]),
              get_capital(surplus_capital_projection[-1]["end"]) - get_capital(essential_capital_projection[-1]["end"]) ])

    report = create_report(surplus_capital_projection)
    return sc_transactions, essential_capital_projection, surplus_capital_projection, pd.DataFrame(a, columns=["year", "essential", "surplus"]), report





if __name__ == "__main__":
    sc, sim1, sim2, _ = get_projection()
    print("surplus capital = " + str(get_capital(sim2[0]['end'])))
    print(json.dumps(sc))
    print(json.dumps(sim1))
    print(json.dumps(sim2))






#todo: write files, use eums for transactions, report in constant dollars, fix rrif rules, some money is in limbo eg., sale of house, rrif wkthdrawal
#tax based on next year...




