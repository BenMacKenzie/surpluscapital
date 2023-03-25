import json

from transactions import *
import json
from utils import create_reportx
import base64
from engine import get_projection

def lambda_handler(event, context):
    print(f"Raw event: {event}")
    if "isBase64Encoded" in event and event["isBase64Encoded"]:
        data = json.loads(base64.b64decode(event["body"]))
    else:
        data = json.loads(event["body"])
    print(data)
    essential_capital, report = get_projection(data)

    return {
        'statusCode': 200,
        'body': json.dumps({
            "essential_capital": essential_capital,
            "report": report
        })
    }
