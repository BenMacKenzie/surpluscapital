
from transactions import *

def sum_columns(d, col_list):
    t = [d[c] for c in col_list]
    z = [sum(z) for z in zip(*t)]
    return z

def subtract_columns(d, x, y):
   diff= [x-y for (x,y) in zip(d[x], d[y])]
   return diff

def round_dict(d):
    for k, v in d.items():
        d[k] = [round(n, 0) for n in v]


def init_report(cols, years):
    d = {}
    for c in cols:
        d[c] = [0] * years

    return d

t = {"a": [1,2,3], "b": [3,4,5], "year": [2001,2002,2003]}
t_tr = {"columns": ["year", 2001, 2002, 2003], "data":[["a", "b"], [1,3], [2.4], [3,5]]}
def transpose_dict(d, c):

    data_cols = [k for k in d.keys() if k != c]
    l = len(d[c])

    data = [[d[col][row] for col in data_cols] for row in range(l)]
    data.insert(0, data_cols)
    columns = [c] + d[c]
    return {"columns": columns, "data": data}

def ld_to_dl(l):
    return {k: [d[k] for d in l] for k in l[0]}


def create_reportx(essential_capital_projection, parameters):
    #get rid of pandas....Ordered_Dict = {k : Not_Ordered_Dict[k] for k in key_order} etc....

    reporting_transactions  = [ "CORE_NEEDS", "HEALTH_CARE_EXPENSES", "DISCRETIONARY_SPENDING", "CHARITABLE_DONATIONS", "OVERDRAFT_INTEREST", "SALE_OF_HOME", "PERMANENT_LIFE_INSURANCE", "EARNED_INCOME", "OTHER_PENSION", "OAS", "CPP", "REGULAR_DIVIDEND", "REGISTERED_DIVIDEND", "REGULAR_ASSET_GROWTH", "REGISTERED_ASSET_GROWTH", "SALE_OF_REGULAR_ASSET",
                               "RRSP_WITHDRAWAL", "RRIF_WITHDRAWAL", "TFSA_WITHDRAWAL", "LIF_WITHDRAWAL", "TAX"]

    spouse_reporting_transactions = ["SPOUSE_EARNED_INCOME", "SPOUSE_OTHER_PENSION", "SPOUSE_OAS", "SPOUSE_CPP", "SPOUSE_REGULAR_DIVIDEND", "SPOUSE_REGISTERED_DIVIDEND", "SPOUSE_REGULAR_ASSET_GROWTH", "SPOUSE_REGISTERED_ASSET_GROWTH",
                                     "SPOUSE_SALE_OF_REGULAR_ASSET", "SPOUSE_RRSP_WITHDRAWAL", "SPOUSE_RRIF_WITHDRAWAL", "SPOUSE_TFSA_WITHDRAWAL", "SPOUSE_LIF_WITHDRAWAL", "SPOUSE_TAX" ]

    if parameters["spouse"]:
        reporting_transactions += spouse_reporting_transactions

    num_years = len(essential_capital_projection)

    df_t = init_report(reporting_transactions, num_years)


    for i in range(len(essential_capital_projection)):
        for t in essential_capital_projection[i]["end"]["transactions"]:
            if t.transaction_type == TransactionType.PENSION_INCOME:
                t_type = t.desc
            else:
                t_type =  t.transaction_type.value

            if t.person == "spouse":
                t_type = "SPOUSE_" + t_type

            if t_type in reporting_transactions:
                if t_type in [ "CORE_NEEDS", "HEALTH_CARE_EXPENSES", "DISCRETIONARY_SPENDING", "CHARITABLE_DONATIONS", "OVERDRAFT_INTEREST", "TAX", "SPOUSE_TAX"]  and t.entry_type == "debit":
                    df_t[t_type][i] += t.amount

                elif  t.entry_type == "credit":
                        df_t[t_type][i] += t.amount


#the projections are lists of dictinaries....need to convert to dictionary of lists
    client_proj = [record['start']['client'] for record in essential_capital_projection[:-1]]
    client_proj.append(essential_capital_projection[-1]['end']['client'])
    for i in range(len(essential_capital_projection)):
        client_proj[i]["year"] = essential_capital_projection[i]["start"]["year"]

    client_proj = ld_to_dl(client_proj)
    _spouse_proj = [record['start']['spouse'] for record in essential_capital_projection[:-1]]
    _spouse_proj.append(essential_capital_projection[-1]['end']['spouse'])
    _spouse_proj = ld_to_dl(_spouse_proj)
    spouse_columns = ["SPOUSE_NON_REGISTERED_ASSET", "SPOUSE_REGULAR_BOOK_VALUE",
                      "SPOUSE_RRSP", "SPOUSE_RRIF", "SPOUSE_TFSA", "SPOUSE_LIRA", "SPOUSE_LIF", "spouse_year"]

    spouse_proj = dict(zip(spouse_columns, list(_spouse_proj.values())))

    joint_proj = [record['start']['joint'] for record in essential_capital_projection[:-1]]
    joint_proj.append(essential_capital_projection[-1]['end']['joint'])
    joint_proj = ld_to_dl(joint_proj)


        #spouse_proj[i]["year"] = essential_capital_projection[i]["start"]["year"]


    df_t.update(client_proj)
    df_t.update(spouse_proj)
    df_t.update(joint_proj)


    round_dict(df_t)


    if parameters["spouse"]:
        ordered_columns = ["year","EARNED_INCOME", "SPOUSE_EARNED_INCOME", "OAS",
                           "SPOUSE_OAS", "CPP", "SPOUSE_CPP",
                           "OTHER_PENSION","SPOUSE_OTHER_PENSION",
                           "REGULAR_DIVIDEND",  "SPOUSE_REGULAR_DIVIDEND",
                           "SALE_OF_REGULAR_ASSET","SPOUSE_SALE_OF_REGULAR_ASSET",
                           "RRSP_WITHDRAWAL",  "SPOUSE_RRSP_WITHDRAWAL",
                           "RRIF_WITHDRAWAL", "SPOUSE_RRIF_WITHDRAWAL",
                           "LIF_WITHDRAWAL", "SPOUSE_LIF_WITHDRAWAL",
                           "TFSA_WITHDRAWAL", "SPOUSE_TFSA_WITHDRAWAL",
                           "SALE_OF_HOME", "PERMANENT_LIFE_INSURANCE",
                           "total_funds_in",
                           "TAX", "SPOUSE_TAX",
                           "CORE_NEEDS", "HEALTH_CARE_EXPENSES", "DISCRETIONARY_SPENDING",
                           "CHARITABLE_DONATIONS",
                           "OVERDRAFT_INTEREST",
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



        funds_in = sum_columns(df_t, ["EARNED_INCOME", "SPOUSE_EARNED_INCOME", "OAS",
                       "SPOUSE_OAS", "CPP", "SPOUSE_CPP",
                       "OTHER_PENSION", "SPOUSE_OTHER_PENSION",
                       "REGULAR_DIVIDEND", "SPOUSE_REGULAR_DIVIDEND",
                       "SALE_OF_REGULAR_ASSET", "SPOUSE_SALE_OF_REGULAR_ASSET",
                       "RRSP_WITHDRAWAL", "SPOUSE_RRSP_WITHDRAWAL",
                       "RRIF_WITHDRAWAL", "SPOUSE_RRIF_WITHDRAWAL",
                       "LIF_WITHDRAWAL", "SPOUSE_LIF_WITHDRAWAL",
                       "TFSA_WITHDRAWAL", "SPOUSE_TFSA_WITHDRAWAL", "SALE_OF_HOME", "PERMANENT_LIFE_INSURANCE"])

        df_t["total_funds_in"] = funds_in

        funds_out = sum_columns(df_t,[ "TAX", "SPOUSE_TAX",
                         "CORE_NEEDS", "HEALTH_CARE_EXPENSES", "DISCRETIONARY_SPENDING", "CHARITABLE_DONATIONS", "OVERDRAFT_INTEREST"])

        df_t["total_funds_out"] = funds_out

        df_t["net_funds_in"] = subtract_columns(df_t, "total_funds_in", "total_funds_out")

        total_assets = sum_columns(df_t,  ["NON_REGISTERED_ASSET", "SPOUSE_NON_REGISTERED_ASSET",
                           "RRSP", "SPOUSE_RRSP", "RRIF", "SPOUSE_RRIF", "TFSA", "SPOUSE_TFSA", "LIRA", "SPOUSE_LIRA", "LIF", "SPOUSE_LIF", "CLEARING", "HOME"])

        df_t["total_assets"]=total_assets

        df = {k : df_t[k] for k in ordered_columns}



    else:
        ordered_columns = ["year", "EARNED_INCOME", "OAS", "CPP", "REGULAR_DIVIDEND", "OTHER_PENSION",
                           "SALE_OF_REGULAR_ASSET",
                           "RRSP_WITHDRAWAL", "RRIF_WITHDRAWAL",
                           "LIF_WITHDRAWAL", "TFSA_WITHDRAWAL",
                           "SALE_OF_HOME", "PERMANENT_LIFE_INSURANCE",
                           "total_funds_in", "TAX",
                           "CORE_NEEDS", "HEALTH_CARE_EXPENSES", "DISCRETIONARY_SPENDING",
                           "CHARITABLE_DONATIONS",
                           "OVERDRAFT_INTEREST",
                           "total_funds_out",
                           "net_funds_in",
                           "NON_REGISTERED_ASSET", "REGULAR_BOOK_VALUE",
                           "RRSP", "RRIF", "TFSA", "LIRA", "LIF",
                           "HOME", "CLEARING", "total_assets"]



        funds_in = sum_columns(df_t,["EARNED_INCOME",
                       "OAS",
                       "CPP",
                       "OTHER_PENSION",
                       "REGULAR_DIVIDEND",
                       "SALE_OF_REGULAR_ASSET",
                       "RRSP_WITHDRAWAL",
                       "RRIF_WITHDRAWAL",
                       "LIF_WITHDRAWAL",
                       "TFSA_WITHDRAWAL",
                       "SALE_OF_HOME",
                       "PERMANENT_LIFE_INSURANCE"])

        df_t["total_funds_in"] = funds_in

        funds_out = sum_columns(df_t, ["TAX",
                         "CORE_NEEDS", "HEALTH_CARE_EXPENSES", "DISCRETIONARY_SPENDING", "CHARITABLE_DONATIONS", "OVERDRAFT_INTEREST"])

        df_t["total_funds_out"] = funds_out

        df_t["net_funds_in"] = subtract_columns(df_t, "total_funds_in", "total_funds_out")


        total_assets = sum_columns(df_t, ["NON_REGISTERED_ASSET",
                         "RRSP",  "RRIF", "TFSA", "LIRA", "LIF", "HOME", "CLEARING"])

        df_t["total_assets"] = total_assets

        df = {k : df_t[k] for k in ordered_columns}



    df = {k: df[k] for k in df.keys() if any(v != 0 for v in df[k])}

    df = transpose_dict(df, "year")

    return df

    #i want to return a dict like {"columns": ["year", "2021", "2022", "2023"...], "data":[["OAS", "REGULAR"...], [...values for 2022...] etc...}
