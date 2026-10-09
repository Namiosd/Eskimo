import os
import pytest
from pages.redeem_page import redeem_voucher


def get_voucher_codes():
    """Đọc voucher codes từ file voucher_code.txt trong thư mục data/ (hoặc fallback ở gốc)."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    voucher_path = os.path.join(base_dir, "data", "voucher_code.txt")
    if not os.path.exists(voucher_path):
        voucher_path = os.path.join(base_dir, "voucher_code.txt")
    if not os.path.exists(voucher_path):
        return ["1-VNXNAAZCO"]  # Fallback default code nếu không tìm thấy file
    with open(voucher_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


@pytest.mark.parametrize("voucher_code", get_voucher_codes())
def test_redeem_voucher(logged_in_driver, voucher_code):
    """
    Test case nhận voucher (Redeem Voucher).
    Sử dụng Pytest Parametrize để chạy độc lập cho từng voucher code.
    """
    print(f"\n Bat dau test Redeem voi Voucher: {voucher_code}...")
    result = redeem_voucher(logged_in_driver, voucher_code)
    print(f"[Result] Redeem {voucher_code} result: {result}")
    assert result is not None, f"Redeem voucher {voucher_code} failed!"
    print(f"[Success] test_redeem_voucher ({voucher_code}) - PASSED!")
