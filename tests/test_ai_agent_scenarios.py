import os
import pytest
import allure
from core.logger import logger
from core.step_tracker import Step
from pages.ai_agent_page import (
    open_in_app_chat,
    reset_chat_history,
    ask_and_record,
    init_chat_session_state,
    ChatTranscript,
    TRANSCRIPT_FILE
)
from data.ai_agent_scenarios_data import (
    AI_AGENT_SCENARIOS,
    get_scenarios_by_category
)


AI_WAIT_TIMEOUT = 120  # Tăng thời gian chờ AI phản hồi lên 120s (2 phút)


def _run_scenarios_sequence(driver, scenarios, session_title: str = "Tất cả kịch bản AI", reset: bool = False):
    """
    Executes a list of scenarios continuously in In-App Chat on a single screen without resetting.
    """
    failures = []
    total = len(scenarios)
    logger.info(f"=== Bắt đầu chạy {total} kịch bản: '{session_title}' trên 1 màn hình duy nhất (reset={reset}) ===")

    ChatTranscript.start_new_session()
    open_in_app_chat(driver)
    if reset:
        reset_chat_history(driver)

    init_chat_session_state(driver)

    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 3

    for idx, s in enumerate(scenarios, start=1):
        s_id = s["id"]
        category = s.get("category", "")
        step_title = f"{idx}/{total}. [{s_id}] {s['customer_scenario'][:50]}"
        ac_tag = f"{s_id} - {category}" if category else s_id

        logger.info(f"\n{'='*70}\n▶ [{idx}/{total}] [{s_id}] Nhóm: '{category}'\n👤 KHÁCH: \"{s['prompt']}\"\n{'='*70}")

        with allure.step(f"[{idx}/{total}] {s_id}: {s['customer_scenario']}"), Step(step_title):
            try:
                res = ask_and_record(
                    driver,
                    prompt=s["prompt"],
                    ac_tag=ac_tag,
                    timeout=AI_WAIT_TIMEOUT
                )
                consecutive_errors = 0  # Reset on successful prompt exchange
                text = res["response"].lower()
                expected_kws = [k.lower() for k in s.get("expected_keywords", [])]

                # Verify expected keywords
                matched = [k for k in expected_kws if k in text]
                if not matched:
                    err_msg = (
                        f"❌ [{s_id}]: Phản hồi của AI không chứa từ khóa kỳ vọng!\n"
                        f"   - Kịch bản: {s['customer_scenario']}\n"
                        f"   - Kỳ vọng (hành vi AI): {s['expected_behavior']}\n"
                        f"   - Từ khóa kiểm tra: {expected_kws}\n"
                        f"   - Phản hồi thực tế: {res['response']}"
                    )
                    logger.error(err_msg)
                    failures.append(err_msg)
                else:
                    logger.info(f"✅ [{s_id}] Khớp từ khóa: {matched}")

                # Check negative keywords if any
                negative_kws = [k.lower() for k in s.get("negative_keywords", [])]
                found_neg = [k for k in negative_kws if k in text]
                if found_neg:
                    err_msg = (
                        f"⚠️ [{s_id}]: Phản hồi chứa từ khóa bị cấm/không khuyến nghị: {found_neg}\n"
                        f"   - Phản hồi thực tế: {res['response']}"
                    )
                    logger.warning(err_msg)
                    failures.append(err_msg)

            except Exception as e:
                err_msg = f"❌ [{s_id}] Ngoại lệ trong quá trình gửi prompt/nhận phản hồi: {e}"
                logger.error(err_msg)
                failures.append(err_msg)
                consecutive_errors += 1
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    abort_msg = (
                        f"⛔ DỪNG TEST SỚM (Fail-Fast): Đã gặp {consecutive_errors} lỗi ngoại lệ liên tiếp! "
                        f"Có thể do mất kết nối mạng, server UAT gặp sự cố hoặc phiên đăng nhập không thể hồi phục. "
                        f"Dừng kiểm thử ngay để tránh treo tiến trình."
                    )
                    logger.critical(abort_msg)
                    failures.append(abort_msg)
                    break

    # Xuất báo cáo HTML sau khi hoàn thành
    html_report_path = ChatTranscript.export_html_report()
    logger.info(f"✅ ĐÃ XUẤT BÁO CÁO HTML TRỰC QUAN TẠI: {html_report_path}")

    if failures:
        error_summary = "\n\n".join(failures)
        pytest.fail(f"Phát hiện {len(failures)} lỗi trong {len(scenarios)} kịch bản của '{session_title}':\n{error_summary}")


def _run_category_scenarios(driver, category_name: str, reset: bool = False):
    """
    Executes all scenarios belonging to a specific category continuously in In-App Chat.
    Default reset=False to avoid resetting chat history.
    """
    scenarios = get_scenarios_by_category(category_name)
    _run_scenarios_sequence(
        driver,
        scenarios=scenarios,
        session_title=f"Nhóm: '{category_name}'",
        reset=reset
    )


# =============================================================================
# MASTER TEST: EM-6364 - ALL 45 SCENARIOS CONTINUOUS ON 1 SCREEN (NO RESET)
# =============================================================================
@allure.feature("Sale AI Agent - Advanced Scenarios")
@allure.story("EM-6364: All 45 Scenarios - Single Continuous Chat Screen")
@allure.title("EM-6364: Toàn bộ 45 kịch bản AI trên 1 màn hình duy nhất (Không reset, chat tuần tự từng câu)")
@allure.severity(allure.severity_level.BLOCKER)
@allure.issue("EM-6364")
@pytest.mark.ai_all
@pytest.mark.em_6364
def test_em_6364(logged_in_driver):
    """
    [EM-6364] Toàn bộ 45 kịch bản AI Agent được thực thi liên tục trên CÙNG 1 MÀN HÌNH CHAT DUY NHẤT:
    - Không đóng app hay tạo lại session giữa các câu hỏi.
    - Không reset lịch sử hội thoại (giữ nguyên luồng chat).
    - Chat tuần tự từng câu (45 câu hỏi thuộc 6 nhóm kịch bản).
    - Tự động xuất biên bản Markdown và báo cáo HTML trực quan.
    """
    _run_scenarios_sequence(
        logged_in_driver,
        scenarios=AI_AGENT_SCENARIOS,
        session_title="EM-6364: Toàn bộ 48 kịch bản AI (Single Continuous Screen, No Reset)",
        reset=False
    )



# =============================================================================
# 1. SALES AND PLAN RECOMMENDATIONS (12 Scenarios)
# =============================================================================
@allure.feature("Sale AI Agent - Advanced Scenarios")
@allure.story("EM-6364: 1. Sales and plan recommendations")
@allure.title("[EM-6364] Nhóm 1: Sales and plan recommendations (12 kịch bản)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.issue("EM-6364")
@pytest.mark.ai_sales
@pytest.mark.em_6364
def test_01_sales_and_plan_recommendations(logged_in_driver):
    """
    [EM-6364] Kiểm thử 12 kịch bản tư vấn bán hàng và gợi ý gói cước:
    - Nhu cầu bản đồ/nhắn tin/tìm quán ăn (SALES_01)
    - Nhu cầu xem video/upload/hotspot (SALES_02)
    - Đi nhiều nước châu Âu (SALES_03)
    - Đi Nhật hiện tại và Thái Lan sau 3 tháng (SALES_04)
    - Gia đình 4 người (SALES_05)
    - Hỏi gói rẻ nhất (SALES_06)
    - Video call & hotspot (SALES_07)
    - Hỏi dùng trên tàu biển (SALES_08)
    - Du lịch hàng tháng (SALES_09)
    - Vì sao nên chọn Eskimo (SALES_10)
    - Cách đổi/nhập gift code (SALES_11)
    - Dùng Google & WhatsApp tại Trung Quốc (SALES_12)
    """
    _run_category_scenarios(logged_in_driver, "Sales and plan recommendations")


# =============================================================================
# 2. COMPATIBILITY AND INSTALLATION (6 Scenarios)
# =============================================================================
@allure.feature("Sale AI Agent - Advanced Scenarios")
@allure.story("EM-6364: 2. Compatibility and installation")
@allure.title("[EM-6364] Nhóm 2: Compatibility and installation (6 kịch bản)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.issue("EM-6364")
@pytest.mark.ai_compat
@pytest.mark.em_6364
def test_02_compatibility_and_installation(logged_in_driver):
    """
    [EM-6364] Kiểm thử 6 kịch bản tương thích và cài đặt eSIM:
    - Kiểm tra máy hỗ trợ eSIM trước khi mua (COMPAT_01)
    - Điện thoại bị khóa mạng nhà mạng (COMPAT_02)
    - Lo lắng cài xong bị tính hạn dùng ngay (COMPAT_03)
    - Tìm mã QR code (COMPAT_04)
    - Lỡ tay xóa eSIM khỏi máy (COMPAT_05)
    - Đổi sang máy mới muốn chuyển eSIM (COMPAT_06)
    """
    _run_category_scenarios(logged_in_driver, "Compatibility and installation")


# =============================================================================
# 3. CONNECTION ISSUES DURING TRAVEL (7 Scenarios)
# =============================================================================
@allure.feature("Sale AI Agent - Advanced Scenarios")
@allure.story("EM-6364: 3. Connection issues during travel")
@allure.title("[EM-6364] Nhóm 3: Connection issues during travel (7 kịch bản)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.issue("EM-6364")
@pytest.mark.ai_connection
@pytest.mark.em_6364
def test_03_connection_issues_during_travel(logged_in_driver):
    """
    [EM-6364] Kiểm thử 7 kịch bản sự cố kết nối khi đang du lịch:
    - Đã hạ cánh Tokyo nhưng không có data (CONN_01)
    - Có vạch sóng nhưng không tải được trang (CONN_02)
    - Kỳ vọng 5G nhưng chỉ nhận 4G/chậm (CONN_03)
    - Mất mạng ở tầng hầm/ngoại ô (CONN_04)
    - SIM chính bị trừ tiền roaming ngoài ý muốn (CONN_05)
    - Điện thoại có mạng nhưng không phát được hotspot sang laptop (CONN_06)
    - Khách bị lạc đường, hoảng loạn cần mạng gấp (CONN_07)
    """
    _run_category_scenarios(logged_in_driver, "Connection issues during travel")


# =============================================================================
# 4. USAGE BALANCE AND PLANS (6 Scenarios)
# =============================================================================
@allure.feature("Sale AI Agent - Advanced Scenarios")
@allure.story("EM-6364: 4. Usage balance and plans")
@allure.title("[EM-6364] Nhóm 4: Usage balance and plans (7 kịch bản)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.issue("EM-6364")
@pytest.mark.ai_usage
@pytest.mark.em_6364
def test_04_usage_balance_and_plans(logged_in_driver):
    """
    [EM-6364] Kiểm thử 7 kịch bản về dung lượng data và gói cước:
    - Thắc mắc data hao quá nhanh (USAGE_01)
    - Data gói cố định còn thừa sau chuyến đi (USAGE_02)
    - Muốn chuyển/chia sẻ data thừa cho bạn bè (USAGE_03)
    - Mua nhầm gói quốc gia khác (USAGE_04)
    - Tưởng gói Unlimited là tốc độ cao mãi mãi (USAGE_05)
    - Gói cước kích hoạt sớm hơn dự kiến (USAGE_06)
    - Thứ tự ưu tiên trừ data Singapore và World data (USAGE_07)
    """
    _run_category_scenarios(logged_in_driver, "Usage balance and plans")


# =============================================================================
# 5. CASHBACK AND TRAVEL BOOKINGS (9 Scenarios)
# =============================================================================
@allure.feature("Sale AI Agent - Advanced Scenarios")
@allure.story("EM-6364: 5. Cashback and travel bookings")
@allure.title("[EM-6364] Nhóm 5: Cashback and travel bookings (9 kịch bản)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.issue("EM-6364")
@pytest.mark.ai_cashback
@pytest.mark.em_6364
def test_05_cashback_and_travel_bookings(logged_in_driver):
    """
    [EM-6364] Kiểm thử 9 kịch bản hoàn tiền và đặt phòng du lịch:
    - Chưa hiểu cách tích cashback qua đối tác (CASHBACK_01)
    - Đặt trực tiếp trên Klook không qua Eskimo (CASHBACK_02)
    - Đặt hôm qua nhưng chưa thấy cập nhật trạng thái (CASHBACK_03)
    - Đặt 2 đơn liên tiếp trong 1 lần click (CASHBACK_04)
    - Chuyến đi đã xong nhưng chưa nhận được tiền hoàn (CASHBACK_05)
    - Đơn đặt phòng bị hủy/đổi mã đặt phòng mới (CASHBACK_06)
    - Tiền hoàn ít hơn số tiền tự tính (CASHBACK_07)
    - Dùng tiền cashback để mua gói data (CASHBACK_08)
    - Rút tiền cashback về tài khoản ngân hàng (CASHBACK_09)
    """
    _run_category_scenarios(logged_in_driver, "Cashback and travel bookings")


# =============================================================================
# 6. COMPLAINTS AND DIFFICULT CONVERSATIONS (7 Scenarios)
# =============================================================================
@allure.feature("Sale AI Agent - Advanced Scenarios")
@allure.story("EM-6364: 6. Complaints and difficult conversations")
@allure.title("[EM-6364] Nhóm 6: Complaints and difficult conversations (7 kịch bản)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.issue("EM-6364")
@pytest.mark.ai_complaints
@pytest.mark.em_6364
def test_06_complaints_and_difficult_conversations(logged_in_driver):
    """
    [EM-6364] Kiểm thử 7 kịch bản khiếu nại và tình huống nhạy cảm:
    - Đã dùng 1 phần data nhưng đòi hoàn tiền 100% (COMPLAINT_01)
    - Mất mạng ngay trước cuộc họp quan trọng (COMPLAINT_02)
    - Đòi cam kết phủ sóng 100% mọi nơi (COMPLAINT_03)
    - Đòi mua giá khuyến mãi cũ đã hết hạn (COMPLAINT_04)
    - KOC/Creator xin data miễn phí (COMPLAINT_05)
    - Báo có giao dịch/chuyển data lạ trên tài khoản (COMPLAINT_06)
    - Khách không hiểu từ ngữ kỹ thuật (COMPLAINT_07)
    """
    _run_category_scenarios(logged_in_driver, "Complaints and difficult conversations")


# =============================================================================
# 7. INDIVIDUAL SCENARIO TEST RUNNER (Run any single scenario by ID)
# =============================================================================
@allure.feature("Sale AI Agent - Individual Scenario")
@allure.story("EM-6364: Run Single Scenario")
@pytest.mark.ai_individual
@pytest.mark.parametrize("scenario", AI_AGENT_SCENARIOS, ids=[s["id"] for s in AI_AGENT_SCENARIOS])
def test_individual_ai_scenario(logged_in_driver, scenario):
    """
    [EM-6364] Chạy riêng lẻ từng kịch bản AI Agent theo mã kịch bản (Scenario ID).
    Ví dụ lệnh chạy:
        pytest tests/test_ai_agent_scenarios.py -k SALES_01 -s
        pytest tests/test_ai_agent_scenarios.py -k COMPAT_01 -s
    """
    _run_scenarios_sequence(
        logged_in_driver,
        scenarios=[scenario],
        session_title=f"Kịch bản đơn lẻ: {scenario['id']}",
        reset=False
    )
