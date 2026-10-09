from helper_login import create_driver, login
from helper_redeem import redeem_voucher
from helper_transfer import transfer_data
from helper_help import click_help
from helper_buy_data import buy_data_plan
import time

VOUCHER_CODE = "1-VNXNAAZCO"

results = []

driver = create_driver()

try:
    # ============================================================
    # BƯỚC 1: LOGIN
    # ============================================================
    print("\n[TC_LOGIN] Đang chạy...")
    try:
        login(driver)
        print("✅ TC_LOGIN — PASSED!")
        results.append(("TC_LOGIN", "PASSED"))
    except Exception as e:
        print(f"❌ TC_LOGIN — FAILED: {e}")
        results.append(("TC_LOGIN", f"FAILED: {e}"))
        raise

    # ============================================================
    # BƯỚC 2: REDEEM VOUCHER
    # ============================================================
    print("\n[TC_REDEEM] Đang chạy...")
    try:
        result = redeem_voucher(driver, VOUCHER_CODE)
        print(f"✅ TC_REDEEM — {result} PASSED!")
        results.append(("TC_REDEEM", "PASSED"))
    except Exception as e:
        print(f"❌ TC_REDEEM — FAILED: {e}")
        results.append(("TC_REDEEM", f"FAILED: {e}"))

    # ============================================================
    # BƯỚC 3: TRANSFER DATA
    # ============================================================
    print("\n[TC_TRANSFER] Đang chạy...")
    try:
        result = transfer_data(driver)
        print(f"✅ TC_TRANSFER — {result} PASSED!")
        results.append(("TC_TRANSFER", "PASSED"))
    except Exception as e:
        print(f"❌ TC_TRANSFER — FAILED: {e}")
        results.append(("TC_TRANSFER", f"FAILED: {e}"))

    # ============================================================
    # BƯỚC 4: HELP
    # ============================================================
    # print("\n[TC_HELP_001] Đang chạy...")
    # try:
    #     click_help(driver)
    #     print("✅ TC_HELP_001 — PASSED!")
    #     results.append(("TC_HELP_001", "PASSED"))
    # except Exception as e:
    #     print(f"❌ TC_HELP_001 — FAILED: {e}")
    #     results.append(("TC_HELP_001", f"FAILED: {e}"))

    # ============================================================
    # BƯỚC 4: BUY DATA
    # ============================================================
    print("\n[TC_BUY_DATA] Đang chạy...")
    try:
        buy_data_plan(driver)
        print("✅ TC_BUY_DATA — PASSED!")
        results.append(("TC_BUY_DATA", "PASSED"))
    except Exception as e:
        print(f"❌ TC_BUY_DATA — FAILED: {e}")
        results.append(("TC_BUY_DATA", f"FAILED: {e}"))

except Exception as e:
    print(f"\n❌ Dừng do lỗi nghiêm trọng: {e}")

finally:
    print("\n" + "=" * 60)
    print("KẾT QUẢ TOÀN BỘ TEST")
    print("=" * 60)
    passed = 0
    for name, status in results:
        icon = "✅" if "PASSED" in status else "❌"
        print(f"  {icon} {name}: {status}")
        if "PASSED" in status:
            passed += 1
    print(f"\nTổng: {passed}/{len(results)} PASSED")
    print("=" * 60)

    time.sleep(3)
    driver.quit()
    print("\n✅ Đã đóng session")
