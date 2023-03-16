
import json
import os


marginal_tax_rates = {}
my_path = os.path.abspath(os.path.dirname(__file__)) + "/tax.json"

with open(my_path) as t:
    marginal_tax_rates = json.load(t)
    for key, value in marginal_tax_rates.items():
        convert = [[x[0], x[1]/100] for x in value]
        marginal_tax_rates[key] = convert


def get_tax_rates(province):
    federal = marginal_tax_rates["Federal"]
    provincial = marginal_tax_rates[province]
    combined = merge(federal,  provincial)
    return combined


def merge(federal, province):
    p_last = len(province) - 1
    f_last = len(federal) - 1
    combined = []

    f_index = 0
    p_index = 0

    while True:
        if p_index == p_last and f_index == f_last:
            break
        elif p_index == p_last:
            combined.append([federal[f_index][0], federal[f_index][1] + province[p_index][1]])
            f_index += 1
        elif f_index == f_last:
            combined.append([province[p_index][0], federal[f_index][1] + province[p_index][1]])
            p_index += 1
        elif federal[f_index][0] > province[p_index][0]:
            combined.append([province[p_index][0], federal[f_index][1] + province[p_index][1]])
            p_index += 1

        elif federal[f_index][0] < province[p_index][0]:
            combined.append([federal[f_index][0], federal[f_index][1] + province[p_index][1]])
            f_index += 1

        else:
            combined.append([federal[f_index][0], federal[f_index][1] + province[p_index][1]])
            f_index += 1
            p_index += 1

    rates = {"marginal": combined[0:-1], "top": combined[-1][1]}

    return rates