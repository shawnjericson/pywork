"""Giao diện menu tương tác trên terminal cho quán cà phê."""

import re

from coffee_shop import CoffeeShop, format_money

LINE = "=" * 35


def parse_price(text):
    """Đọc giá tiền người dùng nhập, chấp nhận nhiều kiểu viết.

    Ví dụ: '45000', '45.000', '45,000', '45k', '45.000đ', '45000 VND', '2.5k'.
    Ném ValueError nếu không đọc được.
    """
    raw = text.strip().lower().replace(" ", "")
    raw = re.sub(r"(vnđ|vnd|đ|d)$", "", raw)

    multiplier = 1
    if raw.endswith("k"):
        multiplier, raw = 1000, raw[:-1]

    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", raw):
        # Dấu . hoặc , ngăn cách hàng nghìn: 45.000 / 1,250,000
        raw = re.sub(r"[.,]", "", raw)
    else:
        raw = raw.replace(",", ".")

    if not re.fullmatch(r"\d+(\.\d+)?", raw):
        raise ValueError
    return float(raw) * multiplier


def parse_items(text, shop):
    """Tách chuỗi 'Espresso, Latte , Trà đào' thành list món, bỏ khoảng trắng thừa.

    Cho phép nhập số thứ tự món trong menu thay cho tên (VD: '1, 3').
    """
    menu_names = list(shop.menu)
    items = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if shop.find_item(part) is None and part.isdigit() and 1 <= int(part) <= len(menu_names):
            part = menu_names[int(part) - 1]
        items.append(part)
    return items


def print_header(shop):
    print()
    print(LINE)
    print(f"CHÀO MỪNG ĐẾN {shop.name.upper()}")
    print(LINE)
    print("1. Xem menu đồ uống")
    print("2. Thêm đồ uống mới vào menu")
    print("3. Đăng ký khách hàng VIP")
    print("4. Đặt hàng")
    print("5. Thống kê các món đã bán")
    print("6. Thoát chương trình")
    print(LINE)


def show_menu(shop):
    if not shop.menu:
        print("Menu hiện đang trống. Hãy thêm đồ uống ở chức năng 2.")
        return
    width = max(len(name) for name in shop.menu)
    print("--- MENU ĐỒ UỐNG ---")
    for index, (item, price) in enumerate(shop.menu.items(), start=1):
        print(f"{index:>2}. {item:<{width}}  {format_money(price):>12}")


def add_drink(shop):
    item = input("Nhập tên món: ").strip()
    if not item:
        print("Tên món không được để trống.")
        return

    try:
        price = parse_price(input("Nhập giá tiền (VD: 45000, 45.000, 45k): "))
        is_new = shop.add_to_menu(item, price)
    except (TypeError, ValueError) as error:
        message = str(error) or "Giá tiền không hợp lệ, vui lòng nhập số dương."
        print(f"Lỗi: {message}")
        return

    name = shop.find_item(item)
    action = "Đã thêm" if is_new else "Đã cập nhật giá"
    print(f"{action} '{name}': {format_money(shop.menu[name])}")


def register_vip(shop):
    phone = input("Nhập số điện thoại: ")
    try:
        is_new = shop.add_vip(phone)
    except ValueError as error:
        print(f"Lỗi: {error}")
        return
    if is_new:
        print("Đăng ký khách hàng VIP thành công!")
    else:
        print("Số điện thoại này đã là khách VIP.")


def order(shop):
    if not shop.menu:
        print("Menu đang trống, chưa thể đặt hàng.")
        return

    phone = input("Nhập số điện thoại: ")
    raw_items = input("Nhập các món (cách nhau bởi dấu phẩy, VD: Espresso, Latte): ")
    items_list = parse_items(raw_items, shop)
    if not items_list:
        print("Bạn chưa nhập món nào.")
        return

    try:
        shop.place_order(phone, items_list)
    except (TypeError, ValueError) as error:
        print(f"Lỗi: {error}")


def show_stats(shop):
    sold = shop.get_unique_items_sold()
    if not sold:
        print("Chưa có món nào được bán.")
        return

    print(f"Các món đã bán ({len(sold)} món): {sold}")
    print("--- CHI TIẾT ---")
    counts = shop.get_item_sales_count()
    for item, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0])):
        print(f"- {item}: {count} ly")
    print(f"Tổng số đơn: {len(shop.orders)}")
    print(f"Tổng doanh thu: {format_money(shop.get_total_revenue())}")


ACTIONS = {
    "1": show_menu,
    "2": add_drink,
    "3": register_vip,
    "4": order,
    "5": show_stats,
}


def main():
    shop = CoffeeShop("The Python Roastery")

    while True:
        print_header(shop)
        try:
            choice = input("Vui lòng chọn chức năng (1-6): ").strip()
            if choice == "6":
                print(f"Cảm ơn bạn đã ghé {shop.name}. Hẹn gặp lại!")
                break
            action = ACTIONS.get(choice)
            if not choice:
                print("Bạn chưa nhập lựa chọn. Vui lòng nhập số từ 1 đến 6.")
                continue
            if action is None:
                print(f"Lựa chọn '{choice}' không hợp lệ! Vui lòng nhập số từ 1 đến 6.")
                continue
            print()
            action(shop)
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C / Ctrl+D: thoát êm thay vì văng traceback.
            print(f"\nĐã thoát chương trình. Hẹn gặp lại tại {shop.name}!")
            break


if __name__ == "__main__":
    main()
