```
{ 
    "parameters":  {
        "growth_rate": 0.05,
        "income_rate": 0.02,
        "inflation": 0.02,
        "interest_rate": 0.03,
        "start_year": 2021,
        "client_age": 65,
        "client_life_expectancy": 95,
        "spouse": True,
        "spouse_age": 65,
        "spouse_life_expectancy": 95,
        "end_year": 2044,
        "end_balance": 0,
        "Province": "Ontario",
        "pensions": [{"person":  <"client", "spouse">, "name": <"OAS", "CPP", "OTHER_PENSION">, , "start_year": 2040, "end_year": 2050, "amount": 12000, "index_rate": 0.04}],
        "incomes": [{"person":  <"client", "spouse">,  "start_year": 2040, "end_year": 2050, "amount": 12000, "index_rate": 0.04}],
        "pli": ["pli": [{"person": <"client", "spouse">, "amount": 50000}],],
        "income_requirements": [{"type": <"ANNUAL_RETIREMENT_EXPENSES","HEALTH_CARE_EXPENSES","DISCRETIONARY_SPENDING">, "start_year": 2023, "end_year": 2050, "amount": 10000, "index_rate": 0.05}],
        "charitable_donations": [{"start_year": 2023, "end_year": 2050, "amount": 1000, "index_rate": 0.05}]
    },
    
    "start_book":  {
        "joint" : 
                   {"CLEARING": 0,
                   "HOME": 0},
        
        "client" : {
            "NON_REGISTERED_ASSET": 100000,
            "NON_REGISTERED_BOOK_VALUE": 0,
            "TFSA": 20000,
            "RRSP": 0,
            "RRIF": 0,
            "LIF": 0,
            "LIRA": 0
        },
    
        "spouse": {
            "NON_REGISTERED_ASSET": 0,
            "NON_REGISTERED_BOOK_VALUE": 0,
            "TFSA": 20000,
            "RRSP": 500000,
            "RRIF": 0,
            "LIF": 0,
            "LIRA": 0
        }
    }
}
```

To deploy, run `./deploy.sh`. To test, run `./test.sh`, which sends a POST request using the data in `data.json`. This deploys to/invokes the test lambda; to deploy/invoke the prod lambda, add `--prod` 
after those two commands.