import os
import pytest
import allure
from core.logger import logger
from core.step_tracker import Step
from pages.ai_agent_page import (
    open_in_app_chat,
    reset_chat_history,
    verify_initial_chat_ui,
    close_in_app_chat,
    ask_and_record,
    ChatTranscript,
    TRANSCRIPT_FILE,
    HTML_REPORT_FILE
)


@allure.feature("Sale AI Agent - In-App Channel")
@allure.story("EM-6364: In-App Chat Flow (AC1 -> AC4)")
@allure.title("[EM-6364] Cuộc hội thoại liên tục trên cùng 1 màn hình chat (AC1 -> AC4)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.issue("EM-6364")
@pytest.mark.em_6364
def test_sale_ai_agent_in_app_conversation(logged_in_driver):
    """
    Toàn bộ cuộc hội thoại diễn ra LIÊN TỤC trên CÙNG 1 MÀN HÌNH CHAT (App mở 1 lần duy nhất):
    - Không đóng app hay tạo lại session giữa các câu hỏi.
    - Không tự động reset lịch sử hội thoại.
    - Hỏi tuần tự các câu hỏi thuộc AC1, AC2, AC3, AC4.
    - Tự động xuất toàn bộ biên bản hội thoại ra file 'ai_chat_transcript.md' để đối chiếu.
    """
    driver = logged_in_driver
    failures = []

    # 1. Bắt đầu phiên ghi nhận transcript mới (giữ lại toàn bộ lịch sử trước) và mở chat
    logger.info("=== Bắt đầu phiên hội thoại liên tục trên cùng 1 màn hình chat (Không reset) ===")
    ChatTranscript.start_new_session()
    open_in_app_chat(driver)
    from pages.ai_agent_page import init_chat_session_state
    init_chat_session_state(driver)

    # --------------------------------------------------------------------------
    # BƯỚC 1: Xác thực UI khởi tạo của màn hình Chat
    # --------------------------------------------------------------------------
    with allure.step("1. Xác thực giao diện ban đầu của In-App Chat"), Step("1. Xác thực UI Chat"):
        try:
            ui_info = verify_initial_chat_ui(driver)
            logger.info(f"UI Info ban đầu: {ui_info}")
            if not ("user_name" in ui_info or "eski_intro" in ui_info or "chips" in ui_info):
                failures.append("❌ Bước 1: Không tìm thấy các thành phần UI khởi tạo của Chat screen!")
        except Exception as e:
            logger.warning(f"Bước 1 [UI initial warning]: {e}")

    # --------------------------------------------------------------------------
    # AC1: CHECK ACCOUNT & ORDER INFORMATION
    # --------------------------------------------------------------------------
    with allure.step("2. [AC1.1] Kiểm tra dung lượng data còn lại"), Step("2. [AC1.1] Check Data Plans"):
        try:
            prompt = "How much data do I have left, and how many plans do I currently have?"
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC1.1 - Check Data Plans Remaining")
            text = res["response"].lower()
            if not any(w in text for w in ["mb", "gb", "data", "plan", "remaining", "left", "active"]):
                failures.append(f"❌ [AC1.1]: Phản hồi không chứa dung lượng data! Nội dung: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC1.1]: {e}")

    with allure.step("3. [AC1.2] Lịch sử mua gói cước & gợi ý mua lại"), Step("3. [AC1.2] Purchase History"):
        try:
            prompt = "What plans did I buy before? Show my purchase history."
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC1.2 - Purchase History & Re-purchase Suggestion")
            text = res["response"].lower()
            if not any(w in text for w in ["purchase", "bought", "history", "order", "plan", "vietnam", "destination", "no purchase", "haven't", "past"]):
                failures.append(f"❌ [AC1.2]: Phản hồi không chứa thông tin lịch sử mua! Nội dung: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC1.2]: {e}")

    with allure.step("4. [AC1.3] Trạng thái Referral & Referral Code"), Step("4. [AC1.3] Referral Status"):
        try:
            prompt = "Check my referral status: how many friends referred, bonus data remaining, and what is my referral code?"
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC1.3 - Referral Status & Referral Code")
            text = res["response"].lower()
            if not any(w in text for w in ["referral", "code", "friend", "bonus", "500", "mb", "share", "referred"]):
                failures.append(f"❌ [AC1.3]: Phản hồi không chứa thông tin referral! Nội dung: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC1.3]: {e}")

    with allure.step("5. [AC1.4] Thông tin gói cước & thời hạn"), Step("5. [AC1.4] Data Plan Info"):
        try:
            prompt = "Can you tell me about Eskimo data plans and validity?"
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC1.4 - Data Plan Information & Validity")
            text = res["response"].lower()
            if not any(w in text for w in ["validity", "expiry", "countries", "roaming", "esim", "plan", "data", "eskimo"]):
                failures.append(f"❌ [AC1.4]: Phản hồi không chứa thông tin gói cước! Nội dung: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC1.4]: {e}")

    with allure.step("6. [AC1.5] Số dư Cashback hiện tại"), Step("6. [AC1.5] Cashback Amount"):
        try:
            prompt = "How much cashback amount do I currently have?"
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC1.5 - Current Cashback Amount")
            text = res["response"].lower()
            if not any(w in text for w in ["cashback", "$", "usd", "balance", "amount", "current", "earn", "0"]):
                failures.append(f"❌ [AC1.5]: Phản hồi không chứa thông tin cashback! Nội dung: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC1.5]: {e}")

    with allure.step("7. [AC1.6] Mã khuyến mãi hiện có"), Step("7. [AC1.6] Promo Code"):
        try:
            prompt = "Do I have any current promo code or discount available?"
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC1.6 - Current Promo Code")
            text = res["response"].lower()
            if not any(w in text for w in ["promo", "code", "discount", "voucher", "promotion", "offer", "available", "currently", "don't have", "no"]):
                failures.append(f"❌ [AC1.6]: Phản hồi không chứa thông tin mã khuyến mãi! Nội dung: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC1.6]: {e}")

    # --------------------------------------------------------------------------
    # AC2: ADVANCED PURCHASE CONSULTATION & CHECKOUT SUPPORT
    # --------------------------------------------------------------------------
    with allure.step("8. [AC2] Gợi ý nhiều gói cước cùng lúc (List / Carousel)"), Step("8. [AC2] Multi-Plan Recommendation"):
        try:
            prompt = "Recommend multiple plans at once as a list for Japan for me to choose from."
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC2 - Recommend Multiple Plans at Once")
            text = res["response"].lower()
            plans = res["plans"]
            has_multi_plans = any(term in text for term in ["1gb", "3gb", "5gb", "10gb", "options", "plans", "japan"])
            has_carousel = len(plans) >= 2
            if not (has_multi_plans or has_carousel):
                failures.append(f"❌ [AC2]: AI không gợi ý danh sách nhiều gói cước! Plans carousel: {plans}, Text: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC2]: {e}")

    # --------------------------------------------------------------------------
    # AC3: ESIM INSTALLATION SUPPORT
    # --------------------------------------------------------------------------
    with allure.step("9. [AC3.1] Hướng dẫn cài đặt eSIM trên Android"), Step("9. [AC3.1] Install Android"):
        try:
            prompt = "Provide step-by-step installation instructions for Android."
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC3.1 - Installation Instructions (Android)")
            text = res["response"].lower()
            if not any(w in text for w in ["settings", "sim", "network", "qr", "esim", "add", "install", "android", "connections"]):
                failures.append(f"❌ [AC3.1]: Phản hồi thiếu hướng dẫn cài đặt Android! Nội dung: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC3.1]: {e}")

    with allure.step("10. [AC3.2] Hướng dẫn cài đặt eSIM trên iOS / iPhone"), Step("10. [AC3.2] Install iOS"):
        try:
            prompt = "How do I install eSIM on iPhone / iOS?"
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC3.2 - Installation Instructions (iOS)")
            text = res["response"].lower()
            if not any(w in text for w in ["settings", "cellular", "mobile data", "add esim", "qr", "iphone", "ios", "install"]):
                failures.append(f"❌ [AC3.2]: Phản hồi thiếu hướng dẫn cài đặt iOS! Nội dung: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC3.2]: {e}")

    # --------------------------------------------------------------------------
    # AC4: OTHER UTILITIES
    # --------------------------------------------------------------------------
    with allure.step("11. [AC4.1] Đổi ngôn ngữ phản hồi (Tiếng Việt)"), Step("11. [AC4.1] Change Language"):
        try:
            prompt = "Hãy trả lời tôi bằng tiếng Việt nhé. Bạn có thể giới thiệu ngắn về Eskimo không?"
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC4.1 - Change Reply Language (Vietnamese)")
            text = res["response"].lower()
            vietnamese_keywords = ["chào", "eskimo", "gói", "cước", "du lịch", "dữ liệu", "kết nối", "bạn", "tôi", "cho", "xin chào"]
            if not any(w in text for w in vietnamese_keywords):
                failures.append(f"❌ [AC4.1]: AI không đổi sang phản hồi bằng tiếng Việt! Nội dung: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC4.1]: {e}")

    with allure.step("12. [AC4.2] Kiểm tra tương thích thiết bị"), Step("12. [AC4.2] Device Compatibility"):
        try:
            prompt = "Is Samsung Galaxy S24 compatible with eSIM? And what about iPhone 6?"
            res = ask_and_record(driver, prompt=prompt, ac_tag="AC4.2 - Device Compatibility Check")
            text = res["response"].lower()
            if not any(w in text for w in ["s24", "samsung", "compatible", "supports", "yes", "support", "variant"]):
                failures.append(f"❌ [AC4.2]: AI không xác nhận S24 tương thích eSIM! Nội dung: {res['response']}")
            if not any(w in text for w in ["iphone 6", "not compatible", "does not support", "no", "doesn't", "require", "need", "unsupported"]):
                failures.append(f"❌ [AC4.2]: AI không xác nhận iPhone 6 không tương thích! Nội dung: {res['response']}")
        except Exception as e:
            failures.append(f"❌ [AC4.2]: {e}")

    # --------------------------------------------------------------------------
    # KẾT THÚC: Giữ Nguyên Màn Hình Chat & Báo Cáo Transcript
    # --------------------------------------------------------------------------
    with allure.step("13. Kiểm tra file transcript & Xuất báo cáo HTML"), Step("13. Keep Chat & Summary"):
        assert os.path.exists(TRANSCRIPT_FILE), f"❌ File transcript không tồn tại tại {TRANSCRIPT_FILE}!"
        logger.info(f"✅ ĐÃ LƯU TOÀN BỘ BIÊN BẢN HỘI THOẠI TẠI: {TRANSCRIPT_FILE}")
        html_report_path = ChatTranscript.export_html_report()
        logger.info(f"✅ ĐÃ XUẤT BÁO CÁO HTML TRỰC QUAN TẠI: {html_report_path}")
        logger.info("ℹ️ Giữ nguyên màn hình Chat và toàn bộ lịch sử trò chuyện trên ứng dụng.")

    # Nếu có bước nào bị lỗi assert, báo fail tổng hợp tại đây
    if failures:
        error_summary = "\n".join(failures)
        pytest.fail(f"Phát hiện {len(failures)} lỗi trong cuộc hội thoại:\n{error_summary}")
