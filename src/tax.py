from transaction_types import TransactionType
from utils import get_future_value


cap_gains_rate = 0.5
old_age_exemption = 7000
old_age_exemption_age = 65
max_oas = 10000




def get_taxable_income(transactions, person, deduct_clawback=True):
    taxable_income = 0
    taxable = [TransactionType.SALE_OF_NON_REGISTERED_ASSET, TransactionType.RRIF_WITHDRAWAL, TransactionType.RRSP_WITHDRAWAL,
               TransactionType.NON_REGISTERED_DIVIDEND, TransactionType.PENSION_INCOME, TransactionType.EARNED_INCOME]

    for transaction in transactions:
        if transaction.person == person:
            if transaction.transaction_type in taxable and transaction.entry_type == "credit":
                if transaction.transaction_type == TransactionType.SALE_OF_NON_REGISTERED_ASSET:
                    taxable_income += (transaction.amount - transaction.book_value) * 0.5

                else:
                    taxable_income += transaction.amount
            elif transaction.transaction_type == TransactionType.CHARITABLE_DONATIONS:
                taxable_income -= transaction.amount
            elif transaction.transaction_type == TransactionType.OAS_CLAWBACK and deduct_clawback:
                 taxable_income -= transaction.amount

    return taxable_income




def get_oas_amount(transactions, person):
    for transaction in transactions:
        if transaction.person == person:
            if transaction.transaction_type == TransactionType.PENSION_INCOME and transaction.desc == "OAS":
                return transaction.amount
    return 0


def get_current_oas_clawback(transactions, person):
    clawback = 0
    for transaction in transactions:
        if transaction.person == person and transaction.transaction_type == TransactionType.OAS_CLAWBACK:
            clawback += transaction.amount

    return clawback




def get_oas_clawback(transactions, parameters, current_year, person, delta=0):
    oas = get_oas_amount(transactions, person)
    taxable_income = get_taxable_income(transactions, person, deduct_clawback=False)
    taxable_income += delta
    current_clawback = get_current_oas_clawback(transactions, person)

    clawback_base = get_future_value(parameters["start_year"], current_year,
                                     parameters["oas_clawback"]["base"], parameters["oas_clawback"]["index"])

    if oas == 0:
        return 0

    if taxable_income > clawback_base:
        clawback = (taxable_income - clawback_base) * .15
        if clawback > oas:
            clawback = oas

        clawback -= current_clawback

        return clawback

    return 0

def _calculate_tax(parameters, current_year, taxable_income, tax_rates):
    base = 0
    tax = 0
    personal_exemption = get_future_value(parameters["start_year"], current_year, parameters["personal_exemption"]["base"],
                                          parameters["personal_exemption"]["index"])
    taxable_income -= personal_exemption


    if taxable_income <= 0:
        return 0

    for (level, rate) in tax_rates["marginal"]:
        if taxable_income <= level:
            tax += (taxable_income - base) * rate
            return tax
        else:
            tax += (level - base) * rate
            base = level

    tax += (taxable_income - tax_rates["marginal"][-1][0]) * tax_rates["top"]

    return tax

def calculate_marginal_tax(parameters, current_year, base_income, marginal_income, tax_rates):
    base = _calculate_tax(parameters, current_year, base_income, tax_rates)
    total = _calculate_tax(parameters, current_year, base_income + marginal_income, tax_rates)
    return total - base







def amount_of_non_registered_asset_to_sell(transactions, parameters, current_year, person, need, book_value_ratio, starting_income, tax_rates):
    low = need
    high = need / (1 - tax_rates["top"]) + max_oas
    x = round((high + low) / 2, 1)
    iterations = 0
    while True:
        iterations += 1


        tax = calculate_marginal_tax(parameters, current_year, starting_income, x * book_value_ratio * cap_gains_rate, tax_rates)
        oas_clawback = get_oas_clawback(transactions, parameters, current_year, person, x * book_value_ratio * cap_gains_rate)
        net_proceeds = x - tax - oas_clawback
        y = need - net_proceeds

        if abs(y) < 100:
            break
        elif y > 0:
            low = x
            x = round((high + low) / 2, 1)
        else:
            high = x
            x = round((high + low) / 2, 1)
    return x

def amount_of_deferred_asset_to_sell(parameters, current_year, transactions, person, need, starting_income, tax_rates):
    low = need
    high = need / (1 - tax_rates["top"]) + max_oas #add maximum oas clawback
    x = round((high + low) / 2, 1)
    iterations = 0
    while True:
        iterations += 1

        tax = calculate_marginal_tax(parameters, current_year, starting_income, x,  tax_rates)
        oas_clawback = get_oas_clawback(transactions, parameters, current_year, person, x)
        net_proceeds = x - tax - oas_clawback
        y = need - net_proceeds
        if abs(y) < 100:
            break
        elif y > 0:
            low = x
            x = round((high + low) / 2, 1)
        else:
            high = x
            x = round((high + low) / 2, 1)

    return x

