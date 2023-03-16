from enum import Enum

class TransactionType(str, Enum):
    EARNED_INCOME = "EARNED_INCOME",
    PENSION_INCOME = "PENSION_INCOME",
    REGULAR_DIVIDEND = "REGULAR_DIVIDEND",
    REGULAR_ASSET_GROWTH = "REGULAR_ASSET_GROWTH",
    REGISTERERD_DIVIDEND = "REGISTERERD_DIVIDEND",
    REGISTERED_ASSET_GROWTH = "REGISTERED_ASSET_GROWTH",
    HOME_APPRECIATION = "HOME_APPRECIATION",
    SALE_OF_REGULAR_ASSET = "SALE_OF_REGULAR_ASSET",
    RRSP_CONVERSION = "RRSP_CONVERSION",
    LIRA_CONVERSION = "LIRA_CONVERSION",
    RRIF_WITHDRAWAL = "RRIF_WITHDRAWAL",
    RRSP_WITHDRAWAL = "RRSP_WITHDRAWAL",
    TFSA_WITHDRAWAL = "TFSA_WITHDRAWAL",
    LIF_WITHDRAWAL = "LIF_WITHDRAWAL",
    BOOK_VALUE_ADJUSTMENT = "BOOK_VALUE_ADJUSTMENT",
    SALE_OF_HOME = "SALE_OF_HOME",
    REGULAR_ASSET_INVESTMENT = "REGULAR_ASSET_INVESTMENT",
    CORE_NEEDS = "CORE_NEEDS",
    HEALTH_CARE_EXPENSE = "HEALTH_CARE_EXPENSES",
    DISCRETIONARY_SPENDING = "DISCRETIONARY_SPENDING",
    TAX =  "TAX",
    REMOVE_SURPLUS_CAPITAL = "REMOVE_SURPLUS_CAPITAL",
    CHARITABLE_DONATIONS = "CHARITABLE_DONATIONS",
    PERMANENT_LIFE_INSURANCE = "PERMANENT_LIFE_INSURANCE",
    TRANSFER_ASSETS_TO_SPOUSE =  "TRANSFER_ASSETS_TO_SPOUSE",
    OVERDRAFT_INTEREST = "OVERDRAFT_INTEREST",
    OAS_CLAWBACK = "OAS_CLAWBACK"