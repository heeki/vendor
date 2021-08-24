import json
from ports.vendor_item import VendorItem

class VendorOrder:
    def __init__(self, order):
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
        self.items = []
        for item in order["orderDetails"]["items"]:
            self.items.append(VendorItem(item))

    def _validate(self, payload, attribute):
        if attribute in payload:
            return payload[attribute]
        else:
            return None

    def to_dict(self):
        internal = {
            "purchaseOrderNumber": self.purchase_order_number,
            "orderDetails": {
                "purchaseOrderDate": self.purchase_order_date,
                "purchaseOrderType": self.purchase_order_type,
                "paymentMethod": self.payment_method,
                "buyingParty": {
                    "partyId": self.buying_party_id
                },
                "sellingParty": {
                    "partyId": self.selling_party_id
                },
                "shipToParty": {
                    "partyId": self.ship_to_party_id
                },
                "billToParty": {
                    "partyId": self.bill_to_party_id
                },
                "items": [json.loads(str(item)) for item in self.items]
            }
        }
        if self.purchase_order_state is not None:
            internal["purchaseOrderState"] = self.purchase_order_state
        if self.purchase_order_state_changed_date is not None:
            internal["orderDetails"]["purchaseOrderStateChangedDate"] = self.purchase_order_state_changed_date
        if self.ship_window is not None:
            internal["orderDetails"]["shipWindow"] = self.ship_window
        return internal
