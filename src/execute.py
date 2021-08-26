import json
# from datetime import datetime, timedelta
# from lib.encoders import DateTimeEncoder
from lib.requestor import Requestor
from ports.vendor_order import VendorOrder

def main():
    url = "https://sellingpartnerapi-na.amazon.com/vendor/orders/v1/purchaseOrders"
    params = {
        "createdAfter": "2021-08-25T00:00:00",
        "createdBefore": "2021-08-26T00:00:00",
        "includeDetails": True,
        "limit": 5,
        "sortOrder": "DESC"
    }
    r = Requestor()
    response = r.request(url, params)
    print(response)

if __name__ == "__main__":
    main()
