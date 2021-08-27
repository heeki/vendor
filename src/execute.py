import argparse
import json
# from datetime import datetime, timedelta
# from lib.encoders import DateTimeEncoder
from lib.requestor import Requestor
from ports.vendor_order import VendorOrder, VendorOrderEncoder

def main():
    url = "https://sellingpartnerapi-na.amazon.com/vendor/orders/v1/purchaseOrders"
    params = {
        "createdAfter": "2021-08-25T00:00:00",
        "createdBefore": "2021-08-26T00:00:00",
        "includeDetails": True,
        "limit": 5,
        "sortOrder": "DESC"
    }
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", required=True, help="live|mock")
    args = ap.parse_args()
    if args.type == "live":
        r = Requestor()
        response = r.request(url, params)
        print(response)
    elif args.type == "mock":
        with open("var/vendor_orders.json") as f:
            response = json.load(f)
        orders = []
        for order in response["payload"]["orders"]:
            order = VendorOrder(order)
            orders.append(order.to_dict())
        print(json.dumps(orders, cls=VendorOrderEncoder))

if __name__ == "__main__":
    main()
