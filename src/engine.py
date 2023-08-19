
from transactions import *
import json
from report_utils import create_report
from tax_utils import get_tax_rates



def get_projection(data, calculate_surplus_capital=True):

    start_book= data["start_book"]
    parameters = data["parameters"]

    if not parameters["spouse"]:
        for i in start_book["spouse"]:
            start_book["spouse"][i]=0

    start_book["year"]=parameters["start_year"]


    def liquidate_in_order(transactions, start_book, person, age, tax_rate, income_limit, amount, order):

        book = process_transactions(start_book, transactions)
        target_balance = book['joint'][Account.CLEARING] + amount


        for account in order:
            if account == Account.NON_REGISTERED:
                #pass in needs and pass in an income limit?
                meet_cash_req_from_non_registered_asset(transactions, parameters, book['year'], book, person, tax_rate, amount, income_limit)
            elif account == Account.RRIF:
                meet_cash_req_from_deferred(transactions, parameters, book['year'],book, person, Account.RRIF, tax_rate, amount, income_limit)
            elif account == Account.RRSP:
                meet_cash_req_from_deferred(transactions, parameters, book['year'], book, person, Account.RRIF,
                                            tax_rate, amount, income_limit)

            elif account == Account.LIF:
                meet_cash_req_from_lif(transactions, parameters, book['year'], book, person, age, tax_rate, amount, income_limit)

            elif account == Account.LIRA:
                if age >= 50 and book[person][Account.LIRA] > 0:
                    convert_lira_to_lif(transactions, book, person)
                    book = process_transactions(start_book, transactions)
                    meet_cash_req_from_lif(transactions, parameters, book['year'], book, person, age, tax_rate, amount,
                                           income_limit)

            elif account == Account.TFSA:
                meet_cash_req_from_tfsa(transactions, book, person, amount, income_limit)



            book = process_transactions(start_book, transactions)

            if book['joint'][Account.CLEARING] >= target_balance:
                return

            amount = target_balance - book['joint'][Account.CLEARING]


    #could use the state of book after processing base transactions and empty transactions.
    def sell_assets_to_meet_needs_strategy_1_w_spouse(transactions, tax_rate, start_book, year):

        client_age = get_age(parameters["client_age"], parameters["start_year"], year)
        spouse_age = get_age(parameters["spouse_age"], parameters["start_year"], year)

        book = process_transactions(start_book, transactions)

        needs = 0 - book['joint'][Account.CLEARING]

        target = needs / 2


        liquidate_in_order(transactions, start_book, "client", client_age, tax_rate, 0, target, [Account.NON_REGISTERED, Account.TFSA, Account.RRIF, Account.RRSP, Account.LIF, Account.LIRA])
        liquidate_in_order(transactions, start_book, "spouse", spouse_age, tax_rate, 0, target, [Account.NON_REGISTERED, Account.TFSA, Account.RRIF, Account.RRSP, Account.LIF, Account.LIRA])

        book = process_transactions(start_book, transactions)

        if book['joint'][Account.CLEARING] >= 0:
            return

        needs = 0 - book['joint'][Account.CLEARING]
        target = needs

        liquidate_in_order(transactions, start_book, "client", client_age, tax_rate, 0, target, [Account.NON_REGISTERED, Account.TFSA, Account.RRIF, Account.RRSP, Account.LIF, Account.LIRA])


        book = process_transactions(start_book, transactions)

        if book['joint'][Account.CLEARING] >= 0:
            return

        needs = 0 - book['joint'][Account.CLEARING]
        target = needs

        liquidate_in_order(transactions, start_book, "spouse", spouse_age, tax_rate, 0, target, [Account.NON_REGISTERED, Account.TFSA, Account.RRIF, Account.RRSP, Account.LIF, Account.LIRA])


        return


    def sell_assets_to_meet_needs_strategy_1(transactions, tax_rate, start_book, year):

        book = process_transactions(start_book, transactions)

        needs = 0 - book['joint'][Account.CLEARING]

        target = needs

        client_age = get_age(parameters["client_age"], parameters["start_year"], year)



        liquidate_in_order(transactions, start_book, "client", client_age, tax_rate, 0, target,
                           [Account.NON_REGISTERED, Account.TFSA, Account.RRIF, Account.RRSP, Account.LIF, Account.LIRA])

        return


    def simulate_one_year(start_book, year):
        transactions = []
        tax_rate = get_tax_rates(parameters['province'])
        generate_base_transactions(transactions, start_book, parameters, tax_rate)
        book = process_transactions(start_book, transactions)

        if book['joint'][Account.CLEARING] > 0:
            invest_funds(transactions, book, parameters)

        else:

            if parameters["spouse"]:
                sell_assets_to_meet_needs_strategy_1_w_spouse(transactions, tax_rate, start_book, year)
            else:
                sell_assets_to_meet_needs_strategy_1(transactions, tax_rate, start_book, year)


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
            if book[person][Account.NON_REGISTERED] > delta:
                createTransaction(transactions, "debit", person, Account.NON_REGISTERED, delta, TransactionType.REMOVE_SURPLUS_CAPITAL)
                createTransaction(transactions, "debit", person, Account.NON_REGISTERED_BOOK_VALUE, delta * book[person][Account.NON_REGISTERED_BOOK_VALUE] / book[person][Account.NON_REGISTERED],
                                  TransactionType.REMOVE_SURPLUS_CAPITAL)
                delta = 0

            elif book[person][Account.NON_REGISTERED] > 0:
                createTransaction(transactions, "debit", person, Account.NON_REGISTERED, book[person][Account.NON_REGISTERED], TransactionType.REMOVE_SURPLUS_CAPITAL)
                createTransaction(transactions, "debit", person, Account.NON_REGISTERED_BOOK_VALUE, book[person][Account.NON_REGISTERED_BOOK_VALUE], TransactionType.REMOVE_SURPLUS_CAPITAL)
                delta -= book[person][Account.NON_REGISTERED]

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



        for person in persons:

            if book[person][Account.LIF] > delta:
                createTransaction(transactions, "debit", person, Account.LIF, delta, TransactionType.REMOVE_SURPLUS_CAPITAL)
                delta = 0

            elif book[person][Account.LIF] > 0:
                createTransaction(transactions, "debit", person, Account.LIF, book[person][Account.LIF],
                                  TransactionType.REMOVE_SURPLUS_CAPITAL)

                delta -= book[person][Account.LIF]

            if delta == 0:
                return transactions



        if book["joint"][Account.HOME] > delta:
            createTransaction(transactions, "debit", "joint", Account.HOME, delta,
                              TransactionType.REMOVE_SURPLUS_CAPITAL)
            delta = 0
        elif book["joint"][Account.HOME] > 0:
            createTransaction(transactions, "debit", "joint", Account.HOME, book["joint"][Account.HOME] ,
                              TransactionType.REMOVE_SURPLUS_CAPITAL)
            delta -= book["joint"][Account.HOME]


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
            print(f"essential capital {essential_capital}")
            book = start_book
            surplus_cap_transactions = set_essential_capital(book, essential_capital)
            book = process_transactions(book, surplus_cap_transactions)

            end_capital, sim = create_projection(book, surplus_cap_transactions)



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
                essential_capital = round((high + low) / 2, 2)
            else:
                low = essential_capital
                essential_capital = round((high + low) / 2, 2)


    essential_capital_projection, sc_transactions = find_essential_capital(start_book)

    _, surplus_capital_projection = create_projection(start_book)




    l = len(essential_capital_projection) - 1
    year = [essential_capital_projection[i]["start"]["year"] for i in range(l)]
    year.append(essential_capital_projection[-1]["end"]["year"])
    essential = [round(get_capital(essential_capital_projection[i]["start"])) for i in range(l)]
    essential.append(round(get_capital(essential_capital_projection[-1]["end"])))
    surplus = [round(get_capital(surplus_capital_projection[i]["start"])- get_capital(essential_capital_projection[i]["start"])) for i in range(l)]
    surplus.append(round(get_capital(surplus_capital_projection[-1]["end"]) - get_capital(essential_capital_projection[-1]["end"])))

    g = {}
    g["year"] = year
    g["essential"] = essential
    g["surplus"] = surplus

    report = create_report(surplus_capital_projection, parameters)


    return  g, report





if __name__ == "__main__":
    sc, sim1, sim2, _ = get_projection()
    print("surplus capital = " + str(get_capital(sim2[0]['end'])))
    print(json.dumps(sc))
    print(json.dumps(sim1))
    print(json.dumps(sim2))






#todo: write files, use eums for transactions, report in constant dollars, fix rrif rules, some money is in limbo eg., sale of house, rrif wkthdrawal
#tax based on next year...




