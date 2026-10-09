import pytest
from pages.transfer_page import transfer_data


def test_transfer_data(logged_in_driver):
    """
    Test case chuyển dung lượng data (Transfer Data).
    Sử dụng fixture logged_in_driver để tự động login.
    """
    print("\n[Test] Bắt đầu test chuyển dữ liệu (Transfer Data)...")
    result = transfer_data(logged_in_driver)
    print(f"🎉 Kết quả chuyển dữ liệu: {result}")
    assert result is not None, "❌ Chuyển dữ liệu thất bại!"
    print("✅ test_transfer_data — PASSED!")
