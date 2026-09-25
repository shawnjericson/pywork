# pywork – Hệ thống quản lý quán cà phê

Bài tập Python: quản lý menu, khách VIP, đơn hàng và thống kê cho quán **The Python Roastery**, chạy trên terminal.

## Cấu trúc

| File | Nội dung |
|------|----------|
| `coffee_shop.py` | Class `CoffeeShop` (menu: `dict`, orders: `list`, vip_customers: `set`) |
| `main.py` | Menu tương tác `while True` + `input()` |
| `tests/` | Unit test (thư viện chuẩn `unittest`) |

## Chạy chương trình

```bash
python main.py
```

Chạy test:

```bash
python -m unittest -v
```

Chỉ dùng thư viện chuẩn, không cần cài thêm gói nào (Python 3.8+).

## Các trường hợp đặc biệt đã xử lý

**Menu**
- Tên món không phân biệt hoa/thường và khoảng trắng thừa: `" latte "` và `"Latte"` là cùng một món, nên cập nhật giá chứ không tạo món trùng.
- Chuẩn hoá Unicode (NFC) để tiếng Việt gõ từ các bộ gõ/hệ điều hành khác nhau vẫn khớp.
- Giá phải là số dương hữu hạn (từ chối `0`, số âm, `NaN`, `inf`, `True`, chuỗi).
- Nhập giá linh hoạt: `45000`, `45.000`, `45,000`, `45k`, `45.000đ`, `45000 VND`.

**Khách VIP**
- Chuẩn hoá số điện thoại: `090 123 4567`, `090.123.4567`, `+84 901 234 567` là cùng một người.
- Kiểm tra định dạng số điện thoại Việt Nam (10–11 số, bắt đầu bằng `0` hoặc `+84`).
- Báo khi số đã là VIP.

**Đặt hàng**
- Tách chuỗi theo dấu phẩy, bỏ khoảng trắng và phần tử rỗng (`"Latte,, Mocha ,"`).
- Có thể gọi món bằng số thứ tự trong menu (`1, 2`).
- Món không có trong menu bị bỏ qua và được liệt kê cho người dùng biết.
- Đơn không có món hợp lệ nào thì **không** được lưu.
- Gọi trùng món được tính nhiều lần (`Latte, Latte` = 2 ly).
- Hiển thị chi tiết giảm giá 10% cho khách VIP.
- Chặn đặt hàng khi menu đang trống.

**Giao diện**
- Báo lỗi khi lựa chọn ngoài 1–6 hoặc bỏ trống.
- `Ctrl+C` / `Ctrl+D` thoát chương trình êm, không in lỗi (traceback).
- Thống kê thêm: số ly bán mỗi món, tổng số đơn và tổng doanh thu.
