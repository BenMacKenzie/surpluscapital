def get_future_value(current_year, value, factor):
    return value * (1 + factor) ** (current_year - parameters["start_year"])


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
    return total


def print_list(list):
    for l  in list:
        print(l)



def process_transactions(book, transactions):
    book = book.copy()
    for transaction in transactions:
        if transaction["type"] == "debit":
            book[transaction["account"]] -= transaction["amount"]
        else:
            book[transaction["account"]] += transaction["amount"]
    return book


def amount_of_regular_asset_to_sell(book, client, need):
    if client:
        account = "regularAsset"
        bookValue = "regularAssetBookValue"
    else:
        account = "regularAssetSp"
        bookValue = "regularAssetSpBookValue"

    a = (book[account]- book[bookValue])/book[account]
    b = a * parameters["tax_rate"]

    x = need / (1 - b)

    return x