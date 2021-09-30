import boto3
import json
import os
from ports.vendor_item import VendorItem, VendorItemEncoder
from adapters.dynamodb import AdptDynamoDB
from adapters.sqs import AdptSQS

class VendorOrderEncoder(json.JSONEncoder):
    def default(self, o):
        return str(o)

class VendorOrder():
    def __init__(self, session, order):
        self.purchase_order_number = order["purchaseOrderNumber"]
        self.purchase_order_state = self._validate(order, "purchaseOrderState")
        self.purchase_order_date = order["orderDetails"]["purchaseOrderDate"]
        self.purchase_order_state_changed_date = self._validate(order["orderDetails"], "purchaseOrderStateChangedDate")
        self.purchase_order_type = order["orderDetails"]["purchaseOrderType"]
        self.payment_method = order["orderDetails"]["paymentMethod"]
        self.buying_party_id = order["orderDetails"]["buyingParty"]["partyId"]
        self.selling_party_id = order["orderDetails"]["sellingParty"]["partyId"]
        self.ship_to_party_id = order["orderDetails"]["shipToParty"]["partyId"]
        self.bill_to_party_id = order["orderDetails"]["billToParty"]["partyId"]
        self.ship_window = self._validate(order["orderDetails"], "shipWindow")
        self.delivery_window = self._validate(order["orderDetails"], "deliveryWindow")
        self.items = []
        for item in order["orderDetails"]["items"]:
            self.items.append(VendorItem(item))
        # aws session
        self.session = session
        self.table = os.environ.get("VENDOR_TABLE")

    def _validate(self, payload, attribute):
        if attribute in payload:
            return payload[attribute]
        else:
            return None

    def to_dict(self, ddb=False):
        internal = {}
        internal["purchaseOrderNumber"] = self.purchase_order_number if not ddb else {"S": self.purchase_order_number}
        if self.purchase_order_state is not None:
            internal["purchaseOrderState"] = self.purchase_order_state if not ddb else {"S": self.purchase_order_state}
        details = {}
        details["purchaseOrderDate"] = self.purchase_order_date
        if self.purchase_order_state_changed_date is not None:
            details["purchaseOrderStateChangedDate"] = self.purchase_order_state_changed_date
        details["purchaseOrderType"] = self.purchase_order_type
        details["paymentMethod"] = self.payment_method
        details["buyingParty"] = {"partyId": self.buying_party_id}
        details["sellingParty"] = {"partyId": self.selling_party_id}
        details["shipToParty"] = {"partyId": self.ship_to_party_id}
        details["billToParty"] = {"partyId": self.bill_to_party_id}
        if self.ship_window is not None:
            details["shipWindow"] = self.ship_window 
        if self.delivery_window is not None:
            details["deliveryWindow"] = self.delivery_window
        details["items"] = [item.to_dict() for item in self.items]
        internal["orderDetails"] = details if not ddb else {"S": json.dumps(details)}
        return internal

    def persist(self):
        ddb = AdptDynamoDB(self.session, self.table)
        return ddb.put(self.to_dict(ddb=True))

    def retrieve(self, purchase_order_number, purchase_order_state):
        ddb = AdptDynamoDB(self.session, self.table)
        response = ddb.get({
            "purchaseOrderNumber": {"S": purchase_order_number},
            "purchaseOrderState": {"S": purchase_order_state}
        })
        return {
            "purchaseOrderNumber": response["purchaseOrderNumber"]["S"],
            "purchaseOrderState": response["purchaseOrderState"]["S"],
            "orderDetails": json.loads(response["orderDetails"]["S"])
        }
