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
    transactions.add(
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



def process_event(book, event):
    book = book.copy()
    for transaction in event:


        if transaction["type"] == "debit":
            book[transaction["account"]] -= transaction["amount"]
        else:
            book[transaction["account"]] += transaction["amount"]
    return book




def get_pension_ammount(year):
    return {
        "type" : "debit",
        "account" : "clearing",
        "amount" : get_future_value(year, model_inputs["pension_income"], model_inputs["inflation"]),
        "desc": "pension income"
    }


def get_mandatory_rrif_withdrawals(book, year):
    transactions = []
    if (model_inputs["age"] + year > 65) and (book["rrif"] > 0):
        transactions.extend(
            [
                {
                    "type": "debit",
                    "account" : "rrif",
                    "amount" : book["rrif"] / 20,  #fix
                    "desc" : "mandatory rrif withdrawal"
                },
                {
                    "type": "credot",
                    "account": "clearing",
                    "amount": book["rrif"] / 20,  # fix
                    "desc": "mandatory rrif withdrawal"
                },
            ]
        )

    if (model_inputs["spouse_age"] + year > 65) and (book["rrifSp"] > 0):
        transactions.extend(
            [
                {
                    "type": "debit",
                    "account" : "rrifSp",
                    "amount" : book["rrifSp"] / 20, #fix
                    "desc" : "mandatory rrif withdrawal"
                },
                {
                    "type": "credot",
                    "account": "clearing",
                    "amount": book["rrifSp"] / 20,  # fix
                    "desc": "mandatory rrif withdrawal"
                },
            ]
        )

    return transactions


def sell_regular_asset(client, book, amount):

    if client:
        account = "regularAsset"
        bookValue = "regularAssetBookValue"
    else:
        account = "regularAssetSp"
        bookValue = "regularAssetSpBookValue"

    total = book[account]
    bookvalue = book[bookValue]

    transactions = []

    transactions.extend(
        [
            {
                "type": "debit",
                "account": account,
                "amount": amount,
                "desc": "sell"
            },


            {
                "type": "debit",
                "account": bookValue,
                "amount": (amount / total) * bookvalue


            },
            {
                "type": "credit",
                "account": "clearing",
                "amount": amount

        },
            {
                "type": "debit",
                "account": "clearing",
                "amount" : (amount * (total - bookvalue) / total) * model_inputs["tax_rate"],
                "desc": "tax on sale of asset"


            },


        ]

    )
    return transactions





def generate_base_transactions(current_book):
    transactions = []
    year = current_book["year"]
    transactions.append(
        get_pension_ammount(current_book["year"])
    )

    for account in ["regularAsset", "regularAssetSp"]:
        if(current_book[account] > 0):
            transactions.append(
                {"type": "credit",
                "account" : account,
                "amount" : current_book[account] * model_inputs["growth_rate"],
                "desc": "capital appreciation"
                }
            )
            transactions.append(
                {"type" : "credit",
                 "account" : "clearing",
                 "amount" : current_book[account] * model_inputs["income_rate"],
                 "desc": "dividends and interest"
                 }
            )

            transactions.append(
                {
                 "type" : "debit",
                 "account" : "clearing",
                 "amount" : current_book[account] * model_inputs["income_rate"] * model_inputs["tax_rate"],
                 "desc": "tax on dividends and interest"

                 }
            )

    for account in ["rrsp", "rrspSp"]:

        if (current_book[account] > 0):
            transactions.append(
                {"type": "credit",
                 "account": account,
                 "amount": current_book[account] * model_inputs["growth_rate"]
                 }
            )
            transactions.append(
                {"type": "credit",
                 "account": account,
                 "amount": current_book[account] * model_inputs["income_rate"]
                 }


            )


    transactions.extend(get_mandatory_rrif_withdrawals(current_book, year))

    transactions.append(
        {
            "type" : "debit",
            "account": "clearing",
            "amount": get_future_value(year, model_inputs["income_requirements"], model_inputs["inflation"]),
            "desc": "living expense"
        }
    )

    return transactions



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
    regular_asset_needed = amount_of_regular_asset_to_sell(book, client, needs)
    if regular_asset_needed <= book[account]:
        transactions = sell_regular_asset(client, book, regular_asset_needed)
    else:
        transactions = sell_regular_asset(client, book, book[account])

    return transactions



def invest_funds(book):
    transactions = []
    transactions.append(
        {
            "type" : "credit",
            "account" : "regiularAsset",
            "amount" :  book["clearing"],
            "desc": "invest available funds"
        }
    )
    transactions.append(
        {
            "type": "debit",
            "account": "clearing",
            "amount": book["clearing"]
        }
    )



book1 = get_start_book()
print(book1)


transactions = generate_base_transactions(book1)


book = process_event(book1, transactions)
print(book)

if book["clearing"] < 0:
    transactions2 = meet_cash_req_from_regular_asset(book, True)
    transactions.extend(transactions2)
    book = process_event(book1, transactions)

    if book["clearing"] < 0:
        transactions2 = meet_cash_req_from_regular_asset(book, False)
        transactions.extend(transactions2)
else:
    transactions2  = invest_funds(book)
    transactions.extend(transactions2)




book = process_event(book1, transactions)
print(book)
for t in transactions:
    print(t)






#todo: need to store all transactions in one place...as long as i always make...mabyu a gettransaction() function

