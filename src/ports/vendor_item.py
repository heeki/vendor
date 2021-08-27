import json

class VendorItemEncoder(json.JSONEncoder):
    def default(self, o):
        return json.dumps(o)

class VendorItem():
    def __init__(self, item):
        self.item_sequence_number = item["itemSequenceNumber"]
        self.amazon_product_identifier = item["amazonProductIdentifier"]
        self.vendor_product_identifier = item["vendorProductIdentifier"]
        self.ordered_quantity = item["orderedQuantity"]
        self.is_back_order_allowed = item["isBackOrderAllowed"]
        self.net_cost = item["netCost"]
        self.list_price = self._validate(item, "listPrice")

    def _validate(self, payload, attribute):
        if attribute in payload:
            return payload[attribute]
        else:
            return None

    def to_dict(self):
        internal = {
            "itemSequenceNumber": self.item_sequence_number,
            "amazonProductIdentifier": self.amazon_product_identifier,
            "vendorProductIdentifier": self.vendor_product_identifier,
            "orderedQuantity": self.ordered_quantity,
            "isBackOrderAllowed": self.is_back_order_allowed,
            "netCost": self.net_cost,
        }
        if self.list_price is not None:
            internal["listPrice"] = self.list_price
        return internal
