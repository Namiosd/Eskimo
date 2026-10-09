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
    ChatTranscript
)
from data.plan_discovery_scenarios_data import PLAN_DISCOVERY_SCENARIOS


AI_WAIT_TIMEOUT = 120


def _run_discovery_sequence(driver, scenarios, session_title: str = "Plan Discovery & Account Queries", reset: bool = False):
    """
    Executes Plan Discovery & Account Queries scenarios continuously in In-App Chat on a single screen.
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
                consecutive_errors = 0
                text = res["response"].lower()
                expected_kws = [k.lower() for k in s.get("expected_keywords", [])]

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
                        f"Dừng kiểm thử ngay để tránh treo tiến trình."
                    )
                    logger.critical(abort_msg)
                    failures.append(abort_msg)
                    break

    html_report_path = ChatTranscript.export_html_report()
    logger.info(f"✅ ĐÃ XUẤT BÁO CÁO HTML TRỰC QUAN TẠI: {html_report_path}")

    if failures:
        error_summary = "\n\n".join(failures)
        pytest.fail(f"Phát hiện {len(failures)} lỗi trong {len(scenarios)} kịch bản của '{session_title}':\n{error_summary}")


# =============================================================================
# MASTER TEST: ALL 33 PLAN DISCOVERY & ACCOUNT QUERIES CONTINUOUSLY
# =============================================================================
@allure.feature("Sale AI Agent - Plan Discovery & Account Queries")
@allure.story("Plan Discovery & Account Queries - Full Suite (33 Scenarios)")
@allure.title("Plan Discovery & Account Queries: Toàn bộ 33 câu hỏi tra cứu gói cước & tài khoản trên 1 màn hình")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ai_plan_discovery
def test_plan_discovery_all(logged_in_driver):
    """
    Thực thi liên tục toàn bộ 33 câu hỏi tra cứu gói cước & tài khoản (Plan Discovery & Account Queries):
    - Không đóng app hay tạo lại session giữa các câu hỏi.
    - Không reset lịch sử hội thoại.
    - Chat tuần tự từng câu hỏi trên cùng 1 màn hình chat.
    """
    _run_discovery_sequence(
        logged_in_driver,
        scenarios=PLAN_DISCOVERY_SCENARIOS,
        session_title="Plan Discovery & Account Queries (33 Scenarios, Single Screen)",
        reset=False
    )


# =============================================================================
# INDIVIDUAL TEST: RUN ANY SINGLE QUERY BY ID (DISC_01 -> DISC_33)
# =============================================================================
@allure.feature("Sale AI Agent - Plan Discovery & Account Queries")
@allure.story("Plan Discovery - Single Query")
@pytest.mark.ai_plan_discovery_single
@pytest.mark.parametrize("scenario", PLAN_DISCOVERY_SCENARIOS, ids=[s["id"] for s in PLAN_DISCOVERY_SCENARIOS])
def test_plan_discovery_single(logged_in_driver, scenario):
    """
    Chạy riêng lẻ từng câu hỏi tra cứu theo mã kịch bản (DISC_01 đến DISC_33).
    Ví dụ:
        pytest tests/test_plan_discovery.py -k DISC_01 -s
        pytest tests/test_plan_discovery.py -k DISC_02 -s
    """
    _run_discovery_sequence(
        logged_in_driver,
        scenarios=[scenario],
        session_title=f"Kịch bản đơn lẻ: {scenario['id']}",
        reset=False
    )
