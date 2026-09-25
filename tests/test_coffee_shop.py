import contextlib
import datetime
import io
import unittest

from coffee_shop import CoffeeShop, format_money, normalize_phone
from main import parse_items, parse_price


def quiet(func, *args):
    """Gọi hàm mà không in ra màn hình, trả về (kết quả, output)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = func(*args)
    return result, buffer.getvalue()


class InitTests(unittest.TestCase):
    def test_defaults(self):
        shop = CoffeeShop("Quán A")
        self.assertEqual(shop.menu, {})
        self.assertEqual(shop.orders, [])
        self.assertEqual(shop.vip_customers, set())
        self.assertIsInstance(shop.vip_customers, set)

    def test_shops_do_not_share_data(self):
        a, b = CoffeeShop("A"), CoffeeShop("B")
        a.add_to_menu("Latte", 45000)
        a.add_vip("0901234567")
        self.assertEqual(b.menu, {})
        self.assertEqual(b.vip_customers, set())

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            CoffeeShop("   ")


class MenuTests(unittest.TestCase):
    def setUp(self):
        self.shop = CoffeeShop("Test")

    def test_add_and_update_price(self):
        self.assertTrue(self.shop.add_to_menu("Latte", 45000))
        self.assertFalse(self.shop.add_to_menu("  latte ", 50000))
        self.assertEqual(self.shop.menu, {"Latte": 50000})

    def test_extra_spaces_collapsed(self):
        self.shop.add_to_menu("  Trà   đào  ", 40000)
        self.assertIn("Trà đào", self.shop.menu)

    def test_unicode_nfd_matches_nfc(self):
        self.shop.add_to_menu("Trà đào", 40000)  # NFC
        nfd = "Trà đào"               # cùng chữ nhưng dạng NFD
        self.assertEqual(self.shop.find_item(nfd), "Trà đào")

    def test_invalid_prices(self):
        for bad in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                self.shop.add_to_menu("X", bad)
        for bad in ("45000", None, True):
            with self.assertRaises(TypeError):
                self.shop.add_to_menu("X", bad)
        self.assertEqual(self.shop.menu, {})

    def test_empty_item_name(self):
        with self.assertRaises(ValueError):
            self.shop.add_to_menu("   ", 10000)


class VipTests(unittest.TestCase):
    def test_phone_normalization(self):
        for raw in ("0901234567", "090 123 4567", "090.123.4567",
                    "090-123-4567", "+84901234567", "84901234567"):
            self.assertEqual(normalize_phone(raw), "0901234567")

    def test_invalid_phones(self):
        for bad in ("", "abc", "12345", "090123456789", "1901234567"):
            with self.assertRaises(ValueError):
                normalize_phone(bad)

    def test_add_vip_duplicate(self):
        shop = CoffeeShop("Test")
        self.assertTrue(shop.add_vip("0901234567"))
        self.assertFalse(shop.add_vip("+84 901 234 567"))
        self.assertEqual(shop.vip_customers, {"0901234567"})


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.shop = CoffeeShop("Test", menu={"Espresso": 30000, "Latte": 45000})

    def test_normal_order(self):
        order, out = quiet(self.shop.place_order, "0901234567", ["Espresso", "Latte"])
        self.assertEqual(order["total"], 75000)
        self.assertEqual(order["items"], ["Espresso", "Latte"])
        self.assertEqual(order["phone"], "0901234567")
        self.assertIsInstance(order["time"], datetime.datetime)
        self.assertEqual(set(order), {"phone", "items", "total", "time"})
        self.assertIn("75.000đ", out)
        self.assertEqual(self.shop.orders, [order])

    def test_vip_discount(self):
        self.shop.add_vip("0901234567")
        order, _ = quiet(self.shop.place_order, "+84 901 234 567", ["Latte"])
        self.assertEqual(order["total"], 40500)

    def test_invalid_items_skipped(self):
        order, out = quiet(self.shop.place_order, "0901234567", ["latte", "Trà đào"])
        self.assertEqual(order["items"], ["Latte"])
        self.assertEqual(order["total"], 45000)
        self.assertIn("Trà đào", out)

    def test_duplicate_items_counted(self):
        order, _ = quiet(self.shop.place_order, "0901234567", ["Latte", "Latte"])
        self.assertEqual(order["total"], 90000)

    def test_no_valid_items_not_saved(self):
        for items in ([], ["Trà sữa"], ["", "  "], [None, 123]):
            order, _ = quiet(self.shop.place_order, "0901234567", items)
            self.assertIsNone(order)
        self.assertEqual(self.shop.orders, [])

    def test_bad_arguments(self):
        with self.assertRaises(ValueError):
            self.shop.place_order("abc", ["Latte"])
        with self.assertRaises(TypeError):
            self.shop.place_order("0901234567", "Latte")
        self.assertEqual(self.shop.orders, [])

    def test_price_change_does_not_affect_old_orders(self):
        order, _ = quiet(self.shop.place_order, "0901234567", ["Latte"])
        self.shop.add_to_menu("Latte", 99000)
        self.assertEqual(order["total"], 45000)


class StatsTests(unittest.TestCase):
    def test_unique_items_sold(self):
        shop = CoffeeShop("Test", menu={"Espresso": 30000, "Latte": 45000, "Mocha": 50000})
        self.assertEqual(shop.get_unique_items_sold(), set())
        quiet(shop.place_order, "0901234567", ["Latte", "Espresso"])
        quiet(shop.place_order, "0907654321", ["Latte", "Latte"])
        sold = shop.get_unique_items_sold()
        self.assertIsInstance(sold, set)
        self.assertEqual(sold, {"Latte", "Espresso"})
        self.assertEqual(shop.get_item_sales_count(), {"Latte": 3, "Espresso": 1})
        self.assertEqual(shop.get_total_revenue(), 165000)


class InputParsingTests(unittest.TestCase):
    def test_parse_price(self):
        cases = {
            "45000": 45000, "45.000": 45000, "45,000": 45000, "45k": 45000,
            "45K": 45000, "45.000đ": 45000, "45000 VND": 45000,
            "1.250.000": 1250000, "2.5k": 2500, "2,5": 2.5, " 30000 ": 30000,
        }
        for text, expected in cases.items():
            self.assertEqual(parse_price(text), expected, text)

    def test_parse_price_invalid(self):
        for bad in ("", "abc", "-5000", "1e5", "45.00.0", "k"):
            with self.assertRaises(ValueError, msg=bad):
                parse_price(bad)

    def test_parse_items(self):
        shop = CoffeeShop("Test", menu={"Espresso": 30000, "Latte": 45000})
        self.assertEqual(
            parse_items(" Espresso ,  Latte,, Trà đào ,", shop),
            ["Espresso", "Latte", "Trà đào"],
        )
        self.assertEqual(parse_items("1, 2, 9", shop), ["Espresso", "Latte", "9"])
        self.assertEqual(parse_items(" , ,", shop), [])


class FormatMoneyTests(unittest.TestCase):
    def test_format(self):
        self.assertEqual(format_money(45000), "45.000đ")
        self.assertEqual(format_money(40500.0), "40.500đ")
        self.assertEqual(format_money(1234.5), "1.234,50đ")


if __name__ == "__main__":
    unittest.main()
