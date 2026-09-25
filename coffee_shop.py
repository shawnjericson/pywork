import datetime


class CoffeeShop:
    def __init__(self, name, menu=None, orders=None, vip_customers=None):
        self.name = name
        self.menu = menu if menu is not None else {}
        self.orders = orders if orders is not None else []
        self.vip_customers = vip_customers if vip_customers is not None else set()

    def add_to_menu(self, item, price):
        """Thêm món mới hoặc cập nhật giá nếu món đã tồn tại."""
        self.menu[item] = price

    def add_vip(self, phone_number):
        """Thêm số điện thoại vào danh sách khách VIP."""
        self.vip_customers.add(phone_number)

    def place_order(self, phone_number, items_list):
        """Tạo đơn hàng, chỉ tính tiền các món có trong menu, giảm 10% cho VIP."""
        valid_items = [item for item in items_list if item in self.menu]
        total = sum(self.menu[item] for item in valid_items)

        if phone_number in self.vip_customers:
            total *= 0.9

        order = {
            "phone": phone_number,
            "items": valid_items,
            "total": total,
            "time": datetime.datetime.now(),
        }
        self.orders.append(order)

        print(f"Đặt hàng thành công! Tổng tiền: {total:,.0f} VNĐ")
        return order

    def get_unique_items_sold(self):
        """Trả về Set tên tất cả các món đã từng được bán."""
        sold = set()
        for order in self.orders:
            sold.update(order["items"])
        return sold
