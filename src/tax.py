


cap_gains_rate = 0.5
personal_exemption = 12896
old_age_exemption = 7000
old_age_exemption_age = 65
clawback_base = 72000
oas = 10000






def get_oas_clawback(taxable_income):

    if taxable_income > clawback_base:
        clawback = (taxable_income - clawback_base) * .15
        if clawback > oas:
            clawback = oas
    else:
        clawback = 0

    return clawback

def _calculate_tax(taxable_income, tax_rates):
    base = 0
    tax = 0
    taxable_income -= personal_exemption
    taxable_income -= get_oas_clawback(taxable_income)

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

def calculate_marginal_tax(base_income, marginal_income, tax_rates):
    base = _calculate_tax(base_income, tax_rates)
    total = _calculate_tax(base_income + marginal_income, tax_rates)
    return total - base



def amount_of_deferred_asset_to_sell_old(need, starting_income, tax_rates):
    # tax rates: {"marginal": [(15,000.0.1), (30,000,0.4)], "top": 0.5}

    amount = 0
    for (level, rate) in tax_rates['marginal']:
        if starting_income <= level:
            if (need / (1 - rate)) < level - starting_income:
                amount += need / (1 - rate)
                return amount
            else:
                amount += (level - starting_income)
                need -= (level - starting_income) * (1 - rate)
                starting_income = level


    #only top rate left
    amount += need / (1 - tax_rates['top'])
    return amount


#might be better to just double marginal levels, double starting income and halve the tax rates
def amount_of_regular_asset_to_sell_old(need, book_value_ratio, starting_income, tax_rates):

    #tax rates: {"marginal": [(15,000.0.1), (30,000,0.4)], "top": 0.5}
    #book_value_ratio =  (value - book_value) / value
    #0.5 is tax rate adjustment for cap gains

    if book_value_ratio == 0:
        return need

    amount = 0
    for (level, rate) in tax_rates['marginal']:
        rate = rate * 0.5 * book_value_ratio
        if starting_income <= level:
            if  need / (1 - rate) < (level - starting_income)/(0.5 * book_value_ratio):
                amount += need / (1 - rate)
                return amount
            else:
                amount += (level - starting_income) / 0.5
                need -= ((level - starting_income) / 0.5) * (1 - rate)
                starting_income = level


    #only top rate left
    rate = tax_rates['top'] * 0.5 * book_value_ratio
    amount += need / (1 - rate)
    return amount





def amount_of_regular_asset_to_sell(need, book_value_ratio, starting_income, tax_rates):
    low = need
    high = need / (1 - tax_rates["top"])
    x = round((high + low) / 2, 1)

    while True:
        tax = calculate_marginal_tax(starting_income, x * book_value_ratio * cap_gains_rate, tax_rates)
        net_proceeds = x - tax
        y = need - net_proceeds

        if abs(y) < 1:
            break
        elif y > 0:
            low = x
            x = round((high + low) / 2, 1)
        else:
            high = x
            x = round((high + low) / 2, 1)
    return x

def amount_of_deferred_asset_to_sell(need, starting_income, tax_rates):
    low = need
    high = need / (1 - tax_rates["top"])
    x = round((high + low) / 2, 1)

    while True:
        tax = calculate_marginal_tax(starting_income, x,  tax_rates)
        net_proceeds = x - tax
        y = need - net_proceeds
        if abs(y) < 1:
            break
        elif y > 0:
            low = x
            x = round((high + low) / 2, 1)
        else:
            high = x
            x = round((high + low) / 2, 1)
        return x