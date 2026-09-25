"""Cấu trúc dữ liệu cho hệ thống quản lý quán cà phê."""

import datetime
import math
import re
import unicodedata

VIP_DISCOUNT_RATE = 0.10


def normalize_text(text):
    """Chuẩn hoá chuỗi: Unicode NFC, bỏ khoảng trắng thừa ở đầu/cuối và giữa các từ."""
    text = unicodedata.normalize("NFC", text)
    return " ".join(text.split())


def normalize_phone(phone_number):
    """Chuẩn hoá số điện thoại Việt Nam về dạng 0xxxxxxxxx.

    Chấp nhận khoảng trắng, dấu chấm, gạch ngang, ngoặc và tiền tố +84/84.
    Ném ValueError nếu số không hợp lệ.
    """
    if not isinstance(phone_number, str):
        raise TypeError("Số điện thoại phải là chuỗi (str).")

    phone = re.sub(r"[\s.\-()]", "", phone_number)
    if phone.startswith("+84"):
        phone = "0" + phone[3:]
    elif phone.startswith("84") and len(phone) in (11, 12):
        phone = "0" + phone[2:]

    if not re.fullmatch(r"0\d{9,10}", phone):
        raise ValueError(
            f"Số điện thoại '{phone_number}' không hợp lệ "
            "(cần 10-11 chữ số, bắt đầu bằng 0 hoặc +84)."
        )
    return phone


def format_money(amount):
    """Định dạng tiền kiểu Việt Nam: 45000 -> '45.000đ'."""
    rounded = round(amount)
    if math.isclose(amount, rounded):
        return f"{rounded:,}".replace(",", ".") + "đ"
    return f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".") + "đ"


class CoffeeShop:
    def __init__(self, name, menu=None, orders=None, vip_customers=None):
        if not isinstance(name, str) or not normalize_text(name):
            raise ValueError("Tên quán không được để trống.")

        self.name = normalize_text(name)
        # Không dùng {} / [] / set() làm giá trị mặc định trực tiếp để tránh
        # lỗi "mutable default argument" (các quán dùng chung một menu).
        self.menu = {}
        self.orders = list(orders) if orders is not None else []
        self.vip_customers = set()

        for item, price in (menu or {}).items():
            self.add_to_menu(item, price)
        for phone in vip_customers or set():
            self.add_vip(phone)

    def __repr__(self):
        return (
            f"CoffeeShop(name={self.name!r}, menu={len(self.menu)} món, "
            f"orders={len(self.orders)}, vip={len(self.vip_customers)})"
        )

    # ------------------------------------------------------------------ #
    # Tiện ích nội bộ
    # ------------------------------------------------------------------ #
    def find_item(self, item):
        """Tìm tên món chuẩn trong menu, không phân biệt hoa/thường và khoảng trắng.

        Trả về tên món đúng như trong menu, hoặc None nếu không có.
        """
        if not isinstance(item, str):
            return None
        key = normalize_text(item).casefold()
        for name in self.menu:
            if name.casefold() == key:
                return name
        return None

    def is_vip(self, phone_number):
        try:
            return normalize_phone(phone_number) in self.vip_customers
        except (TypeError, ValueError):
            return False

    # ------------------------------------------------------------------ #
    # Các phương thức theo đề bài
    # ------------------------------------------------------------------ #
    def add_to_menu(self, item, price):
        """Thêm món mới vào menu, hoặc cập nhật giá nếu món đã tồn tại.

        Trả về True nếu là món mới, False nếu chỉ cập nhật giá.
        """
        if not isinstance(item, str) or not normalize_text(item):
            raise ValueError("Tên món không được để trống.")
        # bool là lớp con của int nên phải loại riêng (True không phải giá tiền).
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise TypeError("Giá tiền phải là số.")
        if not math.isfinite(price) or price <= 0:
            raise ValueError("Giá tiền phải là số dương hợp lệ.")

        existing = self.find_item(item)
        if existing is not None:
            self.menu[existing] = price
            return False

        self.menu[normalize_text(item)] = price
        return True

    def add_vip(self, phone_number):
        """Thêm số điện thoại vào danh sách VIP.

        Trả về True nếu là khách VIP mới, False nếu số đã có sẵn.
        """
        phone = normalize_phone(phone_number)
        if phone in self.vip_customers:
            return False
        self.vip_customers.add(phone)
        return True

    def place_order(self, phone_number, items_list):
        """Đặt hàng: chỉ tính tiền các món có trong menu, VIP được giảm 10%.

        Trả về dict đơn hàng đã lưu, hoặc None nếu không có món hợp lệ nào.
        """
        phone = normalize_phone(phone_number)
        if isinstance(items_list, str) or not isinstance(items_list, (list, tuple)):
            raise TypeError("Danh sách món phải là list.")

        valid_items, invalid_items = [], []
        for item in items_list:
            name = self.find_item(item)
            if name is not None:
                valid_items.append(name)
            elif isinstance(item, str) and normalize_text(item):
                invalid_items.append(normalize_text(item))

        if invalid_items:
            print(f"Bỏ qua món không có trong menu: {', '.join(invalid_items)}")

        if not valid_items:
            print("Đặt hàng thất bại: không có món hợp lệ nào trong đơn.")
            return None

        subtotal = sum(self.menu[item] for item in valid_items)
        is_vip = phone in self.vip_customers
        discount = subtotal * VIP_DISCOUNT_RATE if is_vip else 0
        total = round(subtotal - discount, 2)

        order = {
            "phone": phone,
            "items": valid_items,
            "total": total,
            "time": datetime.datetime.now(),
        }
        self.orders.append(order)

        if is_vip:
            print(
                f"Khách VIP - giảm {VIP_DISCOUNT_RATE:.0%}: "
                f"{format_money(subtotal)} - {format_money(discount)}"
            )
        print(f"Đặt hàng thành công! Tổng tiền: {format_money(total)}")
        return order

    def get_unique_items_sold(self):
        """Trả về Set tên tất cả các món đã từng được bán."""
        return {item for order in self.orders for item in order["items"]}

    # ------------------------------------------------------------------ #
    # Thống kê mở rộng
    # ------------------------------------------------------------------ #
    def get_total_revenue(self):
        return round(sum(order["total"] for order in self.orders), 2)

    def get_item_sales_count(self):
        """Trả về dict {tên món: số ly đã bán}."""
        counts = {}
        for order in self.orders:
            for item in order["items"]:
                counts[item] = counts.get(item, 0) + 1
        return counts
