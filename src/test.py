import argparse
import json
import unittest
from ports.vendor_item import VendorItem, VendorItemEncoder
from ports.vendor_order import VendorOrder

class VendorOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("var/vendor_order_1.json") as f:
            cls.vendor_order_1 = json.load(f)
        with open("var/vendor_order_2.json") as f:
            cls.vendor_order_2 = json.load(f)
        with open("var/vendor_item_1.json") as f:
            cls.vendor_item_1 = json.load(f)
        with open("var/vendor_item_2.json") as f:
            cls.vendor_item_2 = json.load(f)
        with open("var/vendor_item_3.json") as f:
            cls.vendor_item_3 = json.load(f)
        with open("var/vendor_orders.json") as f:
            cls.vendor_orders = json.load(f)

    def test_vendor_order_1(self):
        order = VendorOrder(self.vendor_order_1["payload"])
        compare = {"payload": order.to_dict()}
        self.assertEqual(self.vendor_order_1, compare)

    def test_vendor_order_2(self):
        order = VendorOrder(self.vendor_order_2["payload"])
        compare = {"payload": order.to_dict()}
        self.assertEqual(self.vendor_order_2, compare)

    def test_vendor_item_1(self):
        item = VendorItem(self.vendor_item_1)
        compare = item.to_dict()
        self.assertEqual(self.vendor_item_1, compare)

    def test_vendor_item_2(self):
        item = VendorItem(self.vendor_item_2)
        compare = item.to_dict()
        self.assertEqual(self.vendor_item_2, compare)

    def test_vendor_item_3(self):
        item = VendorItem(self.vendor_item_3)
        compare = item.to_dict()
        self.assertEqual(self.vendor_item_3, compare)

    def test_vendor_orders(self):
        orders = []
        for order in self.vendor_orders["payload"]["orders"]:
            order = VendorOrder(order)
            orders.append(order.to_dict())
        self.assertEqual(self.vendor_orders["payload"]["orders"], orders)

    def test_persist(self):
        order = VendorOrder(self.vendor_order_1["payload"])
        order.persist()
        validate = order.retrieve(order.purchase_order_number, order.purchase_order_state)
        self.assertEqual(self.vendor_order_1["payload"], validate)

    def test_persist_multi(self):
        orders = []
        for order in self.vendor_orders["payload"]["orders"]:
            order = VendorOrder(order)
            order.persist()
            validate = order.retrieve(order.purchase_order_number, order.purchase_order_state)
            orders.append(validate)
        self.assertEqual(self.vendor_orders["payload"]["orders"], orders)

def main():
    suite = unittest.TestSuite()
    suite.addTest(VendorOrderTest("test_vendor_order_1"))
    suite.addTest(VendorOrderTest("test_vendor_order_2"))
    suite.addTest(VendorOrderTest("test_vendor_item_1"))
    suite.addTest(VendorOrderTest("test_vendor_item_2"))
    suite.addTest(VendorOrderTest("test_vendor_item_3"))
    suite.addTest(VendorOrderTest("test_vendor_orders"))
    suite.addTest(VendorOrderTest("test_persist"))
    suite.addTest(VendorOrderTest("test_persist_multi"))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    main()
