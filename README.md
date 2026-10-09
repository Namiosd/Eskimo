# Eskimo eSIM UAT - Automation Test Framework

Dự án kiểm thử tự động (Mobile Automation Testing) cho ứng dụng **Eskimo eSIM** trên nền tảng Android sử dụng **Python**, **Appium**, **Pytest**, và **Allure Report**. Framework được thiết kế theo chuẩn kiến trúc **Page Object Model (POM)**.

---

## 📁 Cấu trúc Thư mục Dự án

```text
ESKIMO/
├── config/                 # Cấu hình môi trường, thiết bị, Desired Capabilities
│   ├── __init__.py
│   └── config.py           # Class TestConfig
│
├── core/                   # Các thành phần cốt lõi và tiện ích dùng chung
│   ├── __init__.py
│   ├── driver_factory.py   # Quản lý khởi tạo Appium WebDriver & ANR dismissal
│   ├── logger.py           # Cấu hình logging thống nhất
│   └── step_tracker.py     # Theo dõi và in summary các bước kiểm thử
│
├── data/                   # Quản lý dữ liệu kiểm thử (Data-Driven Testing)
│   ├── __init__.py
│   ├── ai_agent_scenarios_data.py
│   └── voucher_code.txt
│
├── pages/                  # Page Object Model (POM) - Locators & Thao tác trên từng màn hình
│   ├── __init__.py
│   ├── base_page.py        # Các hàm thao tác chung (wait element, xử lý popup, onboarding)
│   ├── login_page.py       # Luồng xác thực đăng nhập (Mobile Number + OTP)
│   ├── profile_page.py     # Thao tác trên màn hình Profile & Account
│   ├── buy_data_page.py    # Luồng mua gói cước (Store, package selector, Stripe)
│   ├── redeem_page.py      # Luồng nhập mã Voucher & xác thực kết quả
│   ├── referral_page.py    # Luồng Refer a Friend, thống kê thưởng
│   ├── transfer_page.py    # Luồng chuyển dung lượng data
│   ├── help_page.py        # Thao tác màn hình Help Center
│   └── ai_agent_page.py    # In-App Chatbot & Eski AI Assistant
│
├── tests/                  # Kịch bản kiểm thử (Test Cases & Pytest Fixtures)
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures (driver, logged_in_driver, auto screenshot on failure)
│   ├── test_connection.py  # Sanity check kết nối Appium & Emulator
│   ├── test_login.py       # Test case đăng nhập
│   ├── test_profile.py     # Test case cập nhật thông tin cá nhân
│   ├── test_buy.py         # Test case mua gói data
│   ├── test_redeem.py      # Test case nạp mã voucher
│   ├── test_refer_friend.py# Test case giới thiệu bạn bè
│   ├── test_transfer.py    # Test case chuyển data
│   ├── test_e2e_flows.py   # Kịch bản E2E (Mua -> Chuyển data)
│   ├── test_sale_ai_agent.py
│   └── test_ai_agent_scenarios.py
│
├── reports/                # Thư mục lưu kết quả chạy test (Đã được ignore trên Git)
│   ├── html/               # Các báo cáo trực quan dạng HTML
│   ├── screenshots/        # Ảnh chụp màn hình lỗi tự động và layout DOM XML
│   └── logs/               # File nhật ký transcript hội thoại (.md)
│
├── scripts/                # Các công cụ hỗ trợ & xuất báo cáo
│   ├── start.bat           # Script kiểm tra emulator & khởi động Appium Server
│   ├── html_report_generator.py
│   └── generate_defects_report.py
│
├── legacy_wdio/            # Lưu trữ mã nguồn framework WebdriverIO cũ (nếu cần tra cứu)
├── archive_old_tests/      # Lưu trữ các file test cũ
├── pytest.ini              # Cấu hình chạy Pytest & Log level
├── requirements.txt        # Danh sách thư viện Python cần thiết
└── start.bat               # Phím tắt khởi động Appium nhanh ngoài thư mục gốc
```

---

## 🚀 Hướng dẫn Cài đặt & Sử dụng

### 1. Cài đặt môi trường Python
```bash
pip install -r requirements.txt
```

### 2. Khởi động môi trường Appium
1. Mở **Android Studio** và khởi chạy Virtual Device (mặc định: `emulator-5554`).
2. Nhấp đúp vào file `start.bat` tại thư mục gốc (hoặc chạy lệnh `appium` trong terminal).

### 3. Chạy kiểm thử

* **Quét kiểm tra danh sách test case:**
  ```bash
  python -m pytest --collect-only tests/
  ```

* **Chạy kiểm tra kết nối hệ thống:**
  ```bash
  pytest tests/test_connection.py -s
  ```

* **Chạy toàn bộ test suite:**
  ```bash
  pytest tests/ --alluredir=reports/allure-results
  ```

* **Chạy riêng một test case cụ thể (Ví dụ: Redeem Voucher):**
  ```bash
  pytest tests/test_redeem.py -s
  ```

### 4. Xuất Báo cáo Test

* **Xuất báo cáo hội thoại AI Agent:**
  ```bash
  python scripts/html_report_generator.py
  ```
  File báo cáo sẽ được lưu tại: `reports/html/ai_chat_report.html`

* **Xuất báo cáo lỗi (Defects Report):**
  ```bash
  python scripts/generate_defects_report.py
  ```
  File báo cáo lỗi sẽ được lưu tại: `reports/html/ai_chat_defects_report.html`
