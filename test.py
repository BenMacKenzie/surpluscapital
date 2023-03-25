import json
import requests

url = "https://5biiioz4fxmkbl4t7vgbmfyysi0yeydd.lambda-url.us-east-1.on.aws/"

data = """{
   "parameters":{
      "growth_rate":0.05,
      "income_rate":0.02,
      "inflation":0.02,
      "interest_rate":0.03,
      "start_year":2021,
      "client_age":65,
      "client_life_expectancy":95,
      "spouse": true,
      "spouse_age":65,
      "spouse_life_expectancy":95,
      "end_year":2044,
      "end_balance":0,
      "province":"Ontario",
      "pensions":[
         {
            "person":"client",
            "name":"OAS",
            "start_year":2040,
            "end_year":2050,
            "amount":12000,
            "index_rate":0.04
         }
      ],
      "incomes":[
         {
            "person":"spouse",
            "start_year":2040,
            "end_year":2050,
            "amount":12000,
            "index_rate":0.04
         }
      ],
      "pli":[
         {
            "person":"client",
            "amount":50000
         }
      ],
      "income_requirements":[
         {
            "type":"CORE_NEEDS",
            "start_year":2023,
            "end_year":2050,
            "amount":10000,
            "index_rate":0.05
         }
      ],
      "charitable_donations":[
         {
            "start_year":2023,
            "end_year":2050,
            "amount":1000,
            "index_rate":0.05
         }
      ]
   },
   "start_book":{
      "joint":{
         "CLEARING":0,
         "HOME":0
      },
      "client":{
         "NON_REGISTERED_ASSET":100000,
         "REGULAR_BOOK_VALUE":0,
         "TFSA":20000,
         "RRSP":0,
         "RRIF":0,
         "LIF":0,
         "LIRA":0,
         "year":2021
      },
      "spouse":{
         "NON_REGISTERED_ASSET":0,
         "REGULAR_BOOK_VALUE":0,
         "TFSA":20000,
         "RRSP":500000,
         "RRIF":0,
         "LIF":0,
         "LIRA":0
      },
      "year":2021,
      "transactions":[

      ]
   }
}"""


headers = {"Content-Type": "application/json"}
print(data)
response = requests.post(url, data=data, headers=headers)
print(response.text)