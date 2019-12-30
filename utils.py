def get_future_value(start_year, future_year, value, factor):
    return round(value * (1 + factor) ** (future_year - start_year),0)


def createTransaction(transactions, type, account, amount, desc=""):
    transactions.append(
        {
            "type"  : type,
            "account" : account,
            "amount": amount,
            "desc": desc

        }
    )

def get_capital(book):
    total = 0
    total += book["regularAsset"]
    total += book["regularAssetSp"]
    total += book["rrsp"]
    total += book["rrspSp"]
    total += book["rrif"]
    total += book["rrifSp"]
    total += book['clearing']
    total += book["home"]
    return total


def process_transactions(book, transactions):
    book = book.copy()
    for transaction in transactions:
        if transaction["type"] == "debit":
            book[transaction["account"]] -= transaction["amount"]
        else:
            book[transaction["account"]] += transaction["amount"]
    return book




def amount_of_regular_asset_to_sell(value, bookvalue, need, tax_rate):
    a = (value - bookvalue)/ value
    b = a * tax_rate * 0.5
    x = need / (1 - b)
    return round(x,0)



def get_age(start_age, start_year, current_year):
    age = start_age + current_year - start_year
    return age

