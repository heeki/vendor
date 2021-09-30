import base64
import boto3
import json
import os
from adapters.sqs import AdptSQS
from lib.requestor import Requestor
from ports.vendor_order import VendorOrder, VendorOrderEncoder
from lib.encoders import DateTimeEncoder

# initialization
r = Requestor()
session = boto3.session.Session()
queue_url = os.environ.get("PO_QUEUE_URL")

# helper functions
def build_response(code, body):
    # headers for cors
    headers = {
        "Access-Control-Allow-Origin": "amazonaws.com",
        "Access-Control-Allow-Credentials": True
    }
    # lambda proxy integration
    response = {
        'isBase64Encoded': False,
        'statusCode': code,
        'headers': headers,
        'body': body
    }
    return response

def get_method(event):
    response = None
    context = event["requestContext"]
    # version 1.0
    if "httpMethod" in context:
        response = context["httpMethod"]
    elif "http" in context and "method" in context["http"]:
        response = context["http"]["method"]
    return response

# function: lambda invoker handler
def handler(event, context):
    print(json.dumps(event))
    method = get_method(event)
    if method == "GET":
        response = {}
        output = build_response(200, "hello")
    elif method == "POST":
        url = "https://sellingpartnerapi-na.amazon.com/vendor/orders/v1/purchaseOrders"
        params = json.loads(event["body"]) if "body" in event else {}
        response = r.request(url, params)
        if response.status_code == 403:
            message = json.dumps(json.loads(response.text))
        else:
            message = json.dumps(response.text)
        print(message)
        sqs = AdptSQS(session, queue_url)
        sqs.send_message(message)
        if "payload" in response and "orders" in response["payload"]:
            for o in response["payload"]["orders"]:
                order = VendorOrder(session, o)
                order.persist()
        output = build_response(response.status_code, response.text)
    return output
