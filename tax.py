def amount_of_deferred_asset_to_sell(need, starting_income, tax_rates):
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



def amount_of_regular_asset_to_sell(need, book_value_ratio, starting_income, tax_rates):

    #tax rates: {"marginal": [(15,000.0.1), (30,000,0.4)], "top": 0.5}
    #book_value_ratio =  (value - book_value) / value
    #0.5 is tax rate adjustment for cap gains

    amount = 0
    for (level, rate) in tax_rates['marginal']:
        rate = rate * 0.5 * book_value_ratio
        if starting_income <= level:

            if (need / (1 - rate)) < level - starting_income:
                amount += need / (1 - rate)
                return amount
            else:
                amount += (level - starting_income)
                need -= (level - starting_income) * (1 - rate)
                starting_income = level


    #only top rate left
    rate = tax_rates['top'] * 0.5 * book_value_ratio
    amount += need / (1 - rate)
    return amount
