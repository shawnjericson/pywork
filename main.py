from coffee_shop import CoffeeShop

shop = CoffeeShop("The Python Roastery")

while True:
    print("===================================")
    print(f"CHÀO MỪNG ĐẾN {shop.name.upper()}")
    print("===================================")
    print("1. Xem menu đồ uống")
    print("2. Thêm đồ uống mới vào menu")
    print("3. Đăng ký khách hàng VIP")
    print("4. Đặt hàng")
    print("5. Thống kê các món đã bán")
    print("6. Thoát chương trình")
    print("===================================")
    choice = input("Vui lòng chọn chức năng (1-6): ").strip()

    if choice == "1":
        if not shop.menu:
            print("Menu hiện đang trống.")
        else:
            print("--- MENU ĐỒ UỐNG ---")
            for item, price in shop.menu.items():
                print(f"- {item}: {price:,.0f} VNĐ")

    elif choice == "2":
        item = input("Nhập tên món: ").strip()
        if not item:
            print("Tên món không được để trống.")
            continue
        try:
            price = float(input("Nhập giá tiền: "))
        except ValueError:
            print("Giá tiền không hợp lệ.")
            continue
        shop.add_to_menu(item, price)
        print(f"Đã thêm/cập nhật '{item}' với giá {price:,.0f} VNĐ.")

    elif choice == "3":
        phone = input("Nhập số điện thoại: ").strip()
        shop.add_vip(phone)
        print(f"Đã đăng ký VIP cho số {phone}.")

    elif choice == "4":
        phone = input("Nhập số điện thoại: ").strip()
        raw_items = input("Nhập các món muốn đặt (cách nhau bởi dấu phẩy): ")
        items_list = [item.strip() for item in raw_items.split(",") if item.strip()]
        shop.place_order(phone, items_list)

    elif choice == "5":
        sold = shop.get_unique_items_sold()
        if not sold:
            print("Chưa có món nào được bán.")
        else:
            print(f"Các món đã bán: {sold}")

    elif choice == "6":
        print("Cảm ơn bạn đã ghé The Python Roastery. Hẹn gặp lại!")
        break

    else:
        print("Lựa chọn không hợp lệ! Vui lòng nhập số từ 1 đến 6.")
