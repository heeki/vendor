import argparse
import json
import unittest
from lib.vendor_order import VendorOrder

class VendorOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("var/response_po_1.json") as f:
            cls.response_po_1 = json.load(f)
        with open("var/response_po_2.json") as f:
            cls.response_po_2 = json.load(f)

    def test_vendor_order_1(self):
        order = VendorOrder(self.response_po_1["payload"])
        compare = {"payload": order.to_dict()}
        self.assertEqual(self.response_po_1, compare)

    def test_vendor_order_2(self):
        order = VendorOrder(self.response_po_2["payload"])
        compare = {"payload": order.to_dict()}
        self.assertEqual(self.response_po_2, compare)

def main():
    suite = unittest.TestSuite()
    suite.addTest(VendorOrderTest("test_vendor_order_1"))
    suite.addTest(VendorOrderTest("test_vendor_order_2"))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    main()
