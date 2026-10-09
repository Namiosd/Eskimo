import pytest
from pages.buy_data_page import buy_data_plan
from pages.transfer_page import transfer_data


def test_buy_and_transfer_flow(logged_in_driver):
    """
    Luồng E2E: Đăng nhập thành công -> Mua gói data -> Chuyển gói data vừa mua.
    Sử dụng fixture logged_in_driver để tái sử dụng trạng thái login.
    """
    print("\n[E2E Test] Bắt đầu luồng Mua & Chuyển dữ liệu (Buy & Transfer)...")
    
    # Bước 1: Mua gói data
    print("\n--- [Bước 1] Tiến hành mua gói data ---")
    buy_data_plan(logged_in_driver)
    print("✅ [Bước 1] Mua gói data thành công!")

    # Bước 2: Chuyển gói data
    print("\n--- [Bước 2] Tiến hành chuyển gói data ---")
    result = transfer_data(logged_in_driver)
    assert result is not None, "❌ Chuyển dữ liệu thất bại!"
    print(f"✅ [Bước 2] Chuyển gói data thành công: {result}!")
    
    print("\n🎉 Toàn bộ quy trình test Buy & Transfer đã hoàn thành (PASSED)!")
