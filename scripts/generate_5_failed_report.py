"""
Generator for Dedicated 5 Failed Cases HTML Report (Eskimo Automation & AI Agent).
Generates an executive-ready, highly polished, interactive HTML report covering:
1. 5 Failed Pytest Test Suites (Automation Test Execution View)
2. 5 Critical AI Agent Defects (Deep Bug Cards with Root Cause, Jira Copy, Backend Fix)
3. Full Matrix of all defective scenarios with embedded failure screenshot
"""

import os
import re
import html
import base64
from datetime import datetime
from typing import List, Dict, Any

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_HTML_PATH = os.path.join(ROOT_DIR, "reports", "html", "report_5_failed.html")
OUTPUT_FAILED_CASES_PATH = os.path.join(ROOT_DIR, "reports", "html", "failed_cases_report.html")
SCREENSHOT_PATH = os.path.join(ROOT_DIR, "reports", "screenshots", "debug_failure.png")


def get_base64_image(image_path: str) -> str:
    """Reads an image file and converts it to base64 data URI."""
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                b64_str = base64.b64encode(img_file.read()).decode("utf-8")
                return f"data:image/png;base64,{b64_str}"
        except Exception:
            return ""
    return ""


# 5 FAILED PYTEST TEST SUITES
FAILED_TEST_SUITES = [
    {
        "id": "TEST-01",
        "file": "tests/test_sale_ai_agent.py",
        "func": "test_sale_ai_agent_in_app_conversation",
        "name": "Cuộc hội thoại liên tục trên cùng 1 màn hình chat (AC1 -> AC4)",
        "module": "Sale AI Agent - In-App Channel",
        "severity": "CRITICAL",
        "duration": "488.2s",
        "reason": "Phát hiện lỗi tại Bước 8 [AC2 - Recommend Multiple Plans at Once]: Hệ thống AI không phản hồi kịp thời (Request Timeout > 40s/70s), không hiển thị danh sách gói cước hoặc Carousel cho Nhật Bản.",
        "failed_scenarios_count": 1,
        "traceback": """def test_sale_ai_agent_in_app_conversation(logged_in_driver):
>   pytest.fail(f"Phát hiện {len(failures)} lỗi trong cuộc hội thoại:\\n{error_summary}")
E   Failed: Phát hiện 1 lỗi trong cuộc hội thoại:
E   ❌ [AC2]: AI không gợi ý danh sách nhiều gói cước! Plans carousel: [], Text: [TIMEOUT: No new AI response received within timeout period]"""
    },
    {
        "id": "TEST-02",
        "file": "tests/test_ai_agent_scenarios.py",
        "func": "test_01_sales_and_plan_recommendations",
        "name": "Nhóm 1: Sales and plan recommendations (10 kịch bản)",
        "module": "Sale AI Agent - Advanced Scenarios",
        "severity": "CRITICAL",
        "duration": "315.6s",
        "reason": "Phát hiện 6/10 kịch bản bị thất bại (SALES_02, SALES_03, SALES_04, SALES_06, SALES_07, SALES_09) do Timeout mạng streaming và phản hồi thiếu từ khóa so sánh gói cước cố định vs không giới hạn.",
        "failed_scenarios_count": 6,
        "traceback": """def test_01_sales_and_plan_recommendations(logged_in_driver):
>   pytest.fail("Phát hiện 6 lỗi trong 10 kịch bản của 'Nhóm: Sales and plan recommendations':\\n"
E   ❌ [SALES_02]: Phản hồi thiếu từ khóa kỳ vọng ['fixed', 'unlimited', 'speed', 'hotspot']\\n"
E   ❌ [SALES_03]: Request Timeout > 40s\\n"
E   ❌ [SALES_04]: Request Timeout > 40s\\n"
E   ❌ [SALES_06]: Phản hồi thiếu từ khóa ['usage', 'price', 'cheapest'] (bị lệch sang AC gia đình)\\n"
E   ❌ [SALES_07]: Request Timeout > 40s\\n"
E   ❌ [SALES_09]: Phản hồi thiếu từ khóa ['one esim', 'global', 'no expiry'])"""
    },
    {
        "id": "TEST-03",
        "file": "tests/test_ai_agent_scenarios.py",
        "func": "test_04_usage_balance_and_plans",
        "name": "Nhóm 4: Usage balance and plans (6 kịch bản)",
        "module": "Sale AI Agent - Advanced Scenarios",
        "severity": "CRITICAL",
        "duration": "184.1s",
        "reason": "Phát hiện 1/6 kịch bản bị thất bại nghiêm trọng tại USAGE_05: AI trả lời nhầm nội dung đổi gói Nhật Bản (USAGE_04) thay vì giải thích chính sách Fair Usage Policy của gói Unlimited.",
        "failed_scenarios_count": 1,
        "traceback": """def test_04_usage_balance_and_plans(logged_in_driver):
>   pytest.fail("Phát hiện 1 lỗi trong 6 kịch bản của 'Nhóm: Usage balance and plans':\\n"
E   ❌ [USAGE_05]: Phản hồi của AI không chứa từ khóa kỳ vọng!\\n"
E      - Kịch bản: Khách hàng hỏi gói Unlimited có bị bóp băng thông không\\n"
E      - Từ khóa kiểm tra: ['unlimited', 'high speed', 'speed', 'allowance', 'reduced', 'fair usage']\\n"
E      - Phản hồi thực tế: 'I can see your Japan 1GB plan is currently active, so changing it may require a manual review...'")"""
    },
    {
        "id": "TEST-04",
        "file": "tests/test_ai_agent_scenarios.py",
        "func": "test_05_cashback_and_travel_bookings",
        "name": "Nhóm 5: Cashback and travel bookings (9 kịch bản)",
        "module": "Sale AI Agent - Advanced Scenarios",
        "severity": "CRITICAL",
        "duration": "276.4s",
        "reason": "Phát hiện 1/9 kịch bản bị thất bại tại CASHBACK_06: AI bị trễ 1 nhịp hội thoại, đọc số dư tiền hoàn Agoda của câu CASHBACK_05 thay vì hướng dẫn xử lý vé máy bay bị hủy và đổi mã booking.",
        "failed_scenarios_count": 1,
        "traceback": """def test_05_cashback_and_travel_bookings(logged_in_driver):
>   pytest.fail("Phát hiện 1 lỗi trong 9 kịch bản của 'Nhóm: Cashback and travel bookings':\\n"
E   ❌ [CASHBACK_06]: Phản hồi của AI không chứa từ khóa kỳ vọng!\\n"
E      - Kịch bản: Chuyến bay bị hủy và đổi mã đặt chỗ mới\\n"
E      - Từ khóa kiểm tra: ['cancelled', 'rebook', 'eligibility', 'terms', 'partner', 'new']\\n"
E      - Phản hồi thực tế: 'Your cashback is still showing as pending: €41.63. Since your trip has ended, Agoda must still verify the booking...'")"""
    },
    {
        "id": "TEST-05",
        "file": "tests/test_ai_agent_scenarios.py",
        "func": "test_em_6364",
        "name": "[EM-6364] Toàn bộ 45 kịch bản AI trên 1 màn hình duy nhất (Không reset, chat liên tục)",
        "module": "Sale AI Agent - Advanced Scenarios",
        "severity": "BLOCKER",
        "duration": "1420.8s",
        "reason": "Chuỗi thực thi liên tục 45 câu hỏi không ngắt phiên bị gián đoạn và tích lũy các lỗi Timeout và Lệch ngữ cảnh (Context Drift) từ các nhóm nghiệp vụ trên.",
        "failed_scenarios_count": 8,
        "traceback": """def test_em_6364(logged_in_driver):
>   pytest.fail("Phát hiện 8 lỗi trong 45 kịch bản của '[EM-6364] Toàn bộ 45 kịch bản AI (Single Continuous Screen, No Reset)':\\n"
E   [SALES_01]: Thiếu từ khóa kỳ vọng\\n"
E   [SALES_04]: Timeout > 40s\\n"
E   [SALES_06]: Lệch ngữ cảnh câu hỏi chi phí\\n"
E   [SALES_07]: Timeout > 40s\\n"
E   [SALES_09]: Thiếu từ khóa gói Global\\n"
E   [USAGE_02]: Thiếu từ khóa no expiry\\n"
E   [USAGE_03]: Timeout > 40s\\n"
E   [USAGE_04]: Timeout > 40s")"""
    }
]


# 5 CRITICAL AI DEFECTS
CRITICAL_DEFECTS = [
    {
        "id": "BUG-01",
        "code": "AC2-TIMEOUT",
        "ac": "AC2",
        "title": "Gợi ý nhiều gói cước Nhật Bản (Multi-plan Recommendation - Japan)",
        "query": "Recommend multiple plans at once as a list for Japan for me to choose from.",
        "expected": "Hiển thị danh sách đa dạng các gói cước đi Nhật (1GB, 3GB, 5GB, 10GB, Unlimited...) kèm giá tiền rõ ràng và hiển thị Plan Carousel (rvPlans) để khách chọn trực tiếp.",
        "actual": "[TIMEOUT: No new AI response received within timeout period]\n(Hệ thống AI không trả về tin nhắn mới trong thời gian chờ 40s - 70s)",
        "root_cause": "Tắc nghẽn luồng xử lý hoặc mất kết nối Streaming SSE: Khi truy vấn danh sách gói cước kèm Carousel, API Backend phản hồi quá chậm (>40s) khiến client bị timeout.",
        "severity": "CRITICAL",
        "defect_type": "Response Timeout / Latency",
        "chips": [],
        "technical_fix": "1. Tối ưu truy vấn SQL / Cache danh mục gói cước: Pre-cache danh sách gói cước phổ biến (Japan, Global, Europe) trên Redis để giảm latency xuống dưới 2s.\n2. Cấu hình Timeout & Keep-alive trên API Gateway / Reverse Proxy (tối thiểu 60s cho các prompt sinh carousel).\n3. Bổ sung Fallback Message ngay sau 5s: 'Đang tải các gói cước phù hợp cho Nhật Bản, vui lòng chờ...'"
    },
    {
        "id": "BUG-02",
        "code": "USAGE-05-DRIFT",
        "ac": "Nhóm 4 - USAGE_05",
        "title": "Hiểu nhầm gói Unlimited là tốc độ cao vô hạn (Unlimited Plan Fair Usage Policy)",
        "query": "Does an Unlimited plan mean unlimited full speed data without any daily limits or slowdowns?",
        "expected": "Giải thích rõ ràng chính sách Fair Usage Policy (FUP): Gói Unlimited không giới hạn dung lượng nhưng có hạn mức tốc độ cao hàng ngày (Daily High-Speed Allowance); khi dùng hết hạn mức tốc độ sẽ bị giảm (reduced speed/throttling) chứ không full speed mãi mãi.",
        "actual": "I can see your Japan 1GB plan is currently active, so changing it may require a manual review. I can’t change the destination directly here, but support can check whether it can be exchanged or refunded.",
        "root_cause": "Lệch ngữ cảnh nghiêm trọng (Severe Context Drift): AI trả lời nội dung của câu hỏi USAGE_04 (khách hỏi đổi gói Nhật Bản mua nhầm sang Hàn Quốc) cho câu hỏi hiện tại về chính sách gói Unlimited.",
        "severity": "CRITICAL",
        "defect_type": "Context Drift / Memory Desync",
        "chips": ["Yes, please contact support", "Show me South Korea plans", "How do I use my Japan plan?"],
        "technical_fix": "1. Bắt buộc đồng bộ Correlation ID (Turn-ID / Request-ID) giữa Client và AI Engine để đảm bảo phản hồi trả về đúng câu hỏi đang active.\n2. Tách bạch bộ nhớ ngữ cảnh ngắn hạn (Short-term conversation buffer): Đảm bảo Intent Classifier giải mã đúng intent POLICY_EXPLANATION thay vì lấy nhầm context của intent PLAN_EXCHANGE_REQUEST trước đó."
    },
    {
        "id": "BUG-03",
        "code": "SALES-06-DRIFT",
        "ac": "Nhóm 1 - SALES_06",
        "title": "Hỏi gói rẻ nhất cho trường hợp khẩn cấp (Cheapest Emergency Data Plan)",
        "query": "What is the cheapest plan you have? I just want the lowest price option.",
        "expected": "Tư vấn gói cước có giá thấp nhất (ví dụ: gói 1GB cố định hoặc gói dùng thử $1.95 - $3.00), giải thích rủi ro có thể hết data giữa chừng và hướng dẫn nạp thêm khi cần.",
        "actual": "One Eskimo plan is tied to one eSIM on one phone—it cannot be installed on four phones or shared as a single family pool.\nYou have two options:\n- Best for independent connectivity: Buy separate plans for each phone...\n- Best for shared connection: Use one phone as a hotspot...",
        "root_cause": "Trễ phản hồi 1 bước (1-Step Sequential Lag): AI trả lời nội dung của kịch bản SALES_05 (hỏi về 4 thành viên gia đình) cho câu hỏi SALES_06 (hỏi gói rẻ nhất).",
        "severity": "CRITICAL",
        "defect_type": "Sequential Response Lag",
        "chips": ["How do I buy plans for all four phones?", "Can we use hotspot for the family?", "How do I check eSIM compatibility?"],
        "technical_fix": "1. Triển khai Message Queue Synchronization: Kiểm tra trạng thái Stream Completion của câu hỏi N trước khi client gửi prompt N+1.\n2. Backend cần kiểm tra 'in-reply-to' message hash để hủy bỏ câu trả lời cũ nếu client đã submit câu hỏi mới."
    },
    {
        "id": "BUG-04",
        "code": "CASHBACK-06-LAG",
        "ac": "Nhóm 5 - CASHBACK_06",
        "title": "Chuyến bay bị hủy & đổi mã đặt chỗ mới có được hoàn tiền (Cancelled & Rebooked Cashback)",
        "query": "My flight booking was cancelled and rebooked with a new booking ID. Am I still eligible for cashback?",
        "expected": "Hướng dẫn chính sách xử lý tiền hoàn khi vé bị hủy: Mã đặt chỗ cũ sẽ bị vô hiệu hóa tracking hoàn tiền; khách cần liên hệ bộ phận hỗ trợ Eskimo hoặc kiểm tra xem booking mới có được chuyển tiếp qua link Eskimo hay không để gửi bằng chứng xét duyệt.",
        "actual": "Your cashback is still showing as pending: €41.63. Since your trip has ended, Agoda must still verify the booking and confirm that it was completed without cancellation or refund.\nThere’s no action needed from you right now.",
        "root_cause": "Lệch dữ liệu ngữ cảnh (Context Stagnation): AI tiếp tục đọc dữ liệu booking Agoda của câu CASHBACK_05 thay vì phân tích intent vé máy bay bị hủy (Flight Cancellation Rebooking).",
        "severity": "CRITICAL",
        "defect_type": "Context Drift & Missing Policy",
        "chips": ["How do I contact support about cashback?", "Where can I check my cashback status?", "How does hotel cashback tracking work?"],
        "technical_fix": "1. Nâng cấp System Prompt cho Domain Cashback: Bổ sung tri thức nghiệp vụ cho trường hợp booking modification/cancellation/re-issuance.\n2. Bắt buộc nhận diện keyword 'cancelled' và 'new booking ID' để kích hoạt hàm giải đáp chính sách đối tác thay vì chỉ đọc số dư pending balance."
    },
    {
        "id": "BUG-05",
        "code": "SALES-02-INCOMPLETE",
        "ac": "Nhóm 1 - SALES_02",
        "title": "Tư vấn gói Xem Video & Phát Hotspot (Streaming, Upload & Laptop Hotspot)",
        "query": "I plan to stream videos, upload content on social media, and use my phone as a laptop hotspot. Should I get a fixed or unlimited plan?",
        "expected": "So sánh chi tiết giữa gói cố định (Fixed Data) và gói Unlimited: Giải thích gói Unlimited có hạn mức tốc độ cao mỗi ngày (sau đó giảm tốc độ); gói cố định chạy full speed toàn bộ dung lượng và hỗ trợ phát hotspot sang máy tính.",
        "actual": "Which country are you traveling to, and for how many days?",
        "root_cause": "Thiếu tư vấn chuyên sâu / Bỏ sót nghiệp vụ (Incomplete Consultation): AI chỉ hỏi lại điểm đến mà không hề giải đáp thắc mắc cốt lõi của người dùng về sự khác biệt kỹ thuật giữa gói Fixed và Unlimited.",
        "severity": "HIGH",
        "defect_type": "Incomplete Business Logic",
        "chips": ["I’m traveling to [country]", "I’ll be away for [number] days", "I need help choosing a plan"],
        "technical_fix": "1. Thiết kế lại Chain-of-Thought (CoT) cho Prompt Tư vấn Gói: Yêu cầu AI đưa ra câu trả lời so sánh trực tiếp nguyên lý Fixed vs Unlimited TRƯỚC KHI hỏi thêm thông tin điểm đến.\n2. Cung cấp quy tắc gợi ý: Nếu nhu cầu livestream/hotspot lớn -> khuyến nghị gói Fixed dung lượng lớn (10GB-30GB) hoặc gói Unlimited có dung lượng cao hàng ngày."
    }
]


# FULL MATRIX OF ALL DEFECTS DETECTED TODAY
ALL_DEFECTS_MATRIX = [
    {
        "id": "DEF-01",
        "tag": "AC2",
        "category": "Sales & Recommendations",
        "query": "Recommend multiple plans at once as a list for Japan for me to choose from.",
        "type": "Response Timeout (>40s)",
        "sev": "CRITICAL",
        "detail": "AI không phản hồi trong 40s-70s. Không render danh sách gói cước hoặc carousel."
    },
    {
        "id": "DEF-02",
        "tag": "USAGE_05",
        "category": "Usage Balance & Plans",
        "query": "Does an Unlimited plan mean unlimited full speed data without any daily limits or slowdowns?",
        "type": "Context Drift (Trôi ngữ cảnh)",
        "sev": "CRITICAL",
        "detail": "Khách hỏi chính sách FUP gói Unlimited, AI trả lời kịch bản đổi gói Nhật Bản (USAGE_04)."
    },
    {
        "id": "DEF-03",
        "tag": "SALES_06",
        "category": "Sales & Recommendations",
        "query": "What is the cheapest plan you have? I just want the lowest price option.",
        "type": "Sequential Lag (Trễ 1 nhịp)",
        "sev": "CRITICAL",
        "detail": "Khách hỏi gói rẻ nhất, AI trả lời kịch bản tư vấn gói cho 4 thành viên gia đình (SALES_05)."
    },
    {
        "id": "DEF-04",
        "tag": "CASHBACK_06",
        "category": "Cashback & Bookings",
        "query": "My flight booking was cancelled and rebooked with a new booking ID. Am I still eligible for cashback?",
        "type": "Context Stagnation (Kẹt dữ liệu)",
        "sev": "CRITICAL",
        "detail": "Khách hỏi chính sách đổi chuyến bay, AI trả lời số dư tiền hoàn Agoda của câu CASHBACK_05."
    },
    {
        "id": "DEF-05",
        "tag": "SALES_02",
        "category": "Sales & Recommendations",
        "query": "I plan to stream videos, upload content on social media, and use my phone as a laptop hotspot.",
        "type": "Missing Business Logic",
        "sev": "HIGH",
        "detail": "AI chỉ hỏi lại quốc gia, không giải thích so sánh gói Fixed vs Unlimited và khả năng hotspot."
    },
    {
        "id": "DEF-06",
        "tag": "SALES_03",
        "category": "Sales & Recommendations",
        "query": "I will be visiting France, Italy, Germany, and Spain in one trip. What is the best and simplest plan for me?",
        "type": "Response Timeout (>40s)",
        "sev": "CRITICAL",
        "detail": "AI không phản hồi trong 40s khi xử lý yêu cầu so sánh gói liên quốc gia Châu Âu."
    },
    {
        "id": "DEF-07",
        "tag": "SALES_04",
        "category": "Sales & Recommendations",
        "query": "I am traveling to Japan now and then visiting Thailand in three months. How do Eskimo plans support my travel schedule?",
        "type": "Response Timeout (>40s)",
        "sev": "CRITICAL",
        "detail": "AI không phản hồi trong 40s khi xử lý lịch trình đa điểm đến (Nhật Bản -> Thái Lan)."
    },
    {
        "id": "DEF-08",
        "tag": "SALES_07",
        "category": "Sales & Recommendations",
        "query": "I need data for daily Zoom video calls and hotspotting to my work laptop while traveling.",
        "type": "Response Timeout (>40s)",
        "sev": "CRITICAL",
        "detail": "AI không phản hồi trong 40s khi xử lý yêu cầu tính toán dung lượng Zoom call & remote work."
    },
    {
        "id": "DEF-09",
        "tag": "SALES_09",
        "category": "Sales & Recommendations",
        "query": "I travel internationally almost every month for work. How does Eskimo work for frequent travelers like me?",
        "type": "Missing Keywords",
        "sev": "MEDIUM",
        "detail": "Phản hồi thiếu từ khóa nhấn mạnh gói Global 1 eSIM không hết hạn và tính năng nạp thêm."
    }
]


def generate_html() -> str:
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    screenshot_b64 = get_base64_image(SCREENSHOT_PATH)

    # 1. Generate Suites Rows & Cards
    suite_rows = []
    suite_cards = []
    for idx, s in enumerate(FAILED_TEST_SUITES, start=1):
        suite_rows.append(f"""
        <tr class="suite-row" onclick="jumpToElement('suite-card-{s['id']}')">
            <td><strong class="test-badge">{s['id']}</strong></td>
            <td><span class="file-tag">{html.escape(s['file'])}</span></td>
            <td><strong>{html.escape(s['func'])}()</strong><br><small class="text-muted">{html.escape(s['name'])}</small></td>
            <td><span class="badge-module">{html.escape(s['module'])}</span></td>
            <td><span class="badge-fail">FAILED</span></td>
            <td><strong>{s['failed_scenarios_count']}</strong> lỗi</td>
            <td><code>{s['duration']}</code></td>
            <td><button class="btn-jump" onclick="event.stopPropagation(); jumpToElement('suite-card-{s['id']}')">🔍 Chi tiết</button></td>
        </tr>
        """)

        suite_cards.append(f"""
        <div class="suite-card" id="suite-card-{s['id']}">
            <div class="card-header">
                <div class="header-left">
                    <span class="test-badge-lg">{s['id']}</span>
                    <span class="badge-fail">FAILED</span>
                    <h3 class="card-func-name">{html.escape(s['func'])}()</h3>
                </div>
                <div class="header-right">
                    <span class="file-pill">📁 {html.escape(s['file'])}</span>
                    <span class="time-pill">⏱️ {s['duration']}</span>
                </div>
            </div>
            <div class="card-body">
                <div class="info-block">
                    <span class="info-label">📋 Mô tả mục tiêu kiểm thử:</span>
                    <p class="info-text">{html.escape(s['name'])}</p>
                </div>
                <div class="info-block fail-reason-block">
                    <span class="info-label">❌ Lý do thất bại (Assertion / Error Summary):</span>
                    <p class="fail-reason-text">{html.escape(s['reason'])}</p>
                </div>
                <div class="traceback-block">
                    <div class="trace-header">
                        <span>Terminal Traceback / Failure Log</span>
                        <button class="btn-copy-sm" onclick="copyText(`{html.escape(s['traceback'])}`, this)">📋 Copy Trace</button>
                    </div>
                    <pre class="traceback-code"><code>{html.escape(s['traceback'])}</code></pre>
                </div>
            </div>
        </div>
        """)

    # 2. Generate Critical Defects Rows & Cards
    defect_cards = []
    for idx, d in enumerate(CRITICAL_DEFECTS, start=1):
        chips_str = "".join([f'<span class="chip">💡 {html.escape(c)}</span>' for c in d["chips"]])
        actual_formatted = html.escape(d["actual"]).replace("\n", "<br>")

        jira_markup = f"""*Defect ID:* {d['id']} ({d['code']})
*Acceptance Criteria:* {d['ac']} - {d['title']}
*Severity:* {d['severity']}
*Defect Type:* {d['defect_type']}
*User Query:* {d['query']}
*Expected:* {d['expected']}
*Actual Response:* {d['actual']}
*Root Cause:* {d['root_cause']}
*Technical Fix:* {d['technical_fix']}
*Steps to Reproduce:*
1. Mở ứng dụng Eskimo eSIM (UAT).
2. Mở In-App Chat ("Ask Eski!").
3. Gửi câu hỏi: "{d['query']}"
4. Quan sát phản hồi thực tế của AI."""
        jira_escaped = html.escape(jira_markup).replace('"', '&quot;')

        defect_cards.append(f"""
        <div class="defect-card" id="card-{d['id']}">
            <div class="card-header">
                <div class="header-left">
                    <span class="bug-id">{d['id']}</span>
                    <span class="ac-tag">{html.escape(d['ac'])}</span>
                    <h3 class="bug-title">{html.escape(d['title'])}</h3>
                </div>
                <div class="header-right">
                    <span class="sev-badge sev-{d['severity'].lower()}">{d['severity']}</span>
                    <span class="type-tag">{html.escape(d['defect_type'])}</span>
                    <button class="btn-copy" onclick="copyJiraTicket('{jira_escaped}', this)">
                        📋 Copy Jira Bug
                    </button>
                </div>
            </div>

            <div class="card-body">
                <div class="dialogue-grid">
                    <div class="dialogue-box user-box">
                        <div class="box-label">👤 Khách hàng hỏi (User Prompt):</div>
                        <div class="box-content prompt-text">"{html.escape(d['query'])}"</div>
                    </div>
                    <div class="dialogue-box expected-box">
                        <div class="box-label">🎯 Hành vi kỳ vọng (Expected Behavior):</div>
                        <div class="box-content expected-text">{html.escape(d['expected'])}</div>
                    </div>
                </div>

                <div class="actual-box">
                    <div class="box-label">🤖 AI Phản hồi thực tế (Actual AI Response - Bị lỗi):</div>
                    <div class="box-content actual-text">{actual_formatted}</div>
                    {f'<div class="chips-container"><span class="chips-label">Chips gợi ý kèm theo:</span> {chips_str}</div>' if chips_str else ''}
                </div>

                <div class="analysis-box">
                    <div class="analysis-title">⚠️ Phân tích nguyên nhân lỗi (Root Cause Analysis):</div>
                    <p class="analysis-desc">{html.escape(d['root_cause'])}</p>
                    <div class="fix-title">🛠️ Khuyến nghị khắc phục cho Developer (Backend / Prompt Fix):</div>
                    <p class="fix-desc">{html.escape(d['technical_fix']).replace('\n', '<br>')}</p>
                </div>

                <div class="repro-box">
                    <div class="repro-title">🔄 Các bước tái hiện (Steps to Reproduce):</div>
                    <ol class="repro-list">
                        <li>Khởi chạy ứng dụng <strong>Eskimo eSIM (UAT)</strong> và đăng nhập tài khoản kiểm thử.</li>
                        <li>Tại màn hình chính, mở màn hình <strong>In-App Chat ("Ask Eski!")</strong>.</li>
                        <li>Nhập chính xác câu hỏi: <code>{html.escape(d['query'])}</code></li>
                        <li>Kiểm tra nội dung AI phản hồi và so sánh với hành vi kỳ vọng nêu trên.</li>
                    </ol>
                </div>
            </div>
        </div>
        """)

    # 3. Generate Matrix Rows for All 9 Defects
    matrix_rows = []
    for m in ALL_DEFECTS_MATRIX:
        matrix_rows.append(f"""
        <tr>
            <td><strong class="matrix-id">{m['id']}</strong></td>
            <td><span class="ac-tag">{html.escape(m['tag'])}</span></td>
            <td><span class="badge-module">{html.escape(m['category'])}</span></td>
            <td class="query-cell">"{html.escape(m['query'])}"</td>
            <td><span class="type-pill">{html.escape(m['type'])}</span></td>
            <td><span class="sev-badge sev-{m['sev'].lower()}">{m['sev']}</span></td>
            <td class="detail-cell">{html.escape(m['detail'])}</td>
        </tr>
        """)

    screenshot_section = ""
    if screenshot_b64:
        screenshot_section = f"""
        <section class="screenshot-section">
            <div class="section-header">
                <div>
                    <h2 class="section-title">📸 Ảnh Chụp Màn Hình Lỗi Thực Tế Trên Thiết Bị (Failure Screenshot)</h2>
                    <p class="section-desc">Giao diện In-App Chat tại thời điểm ghi nhận lỗi kết thúc phiên kiểm thử.</p>
                </div>
            </div>
            <div class="screenshot-card">
                <img src="{screenshot_b64}" alt="Eskimo Failure Screenshot" class="app-screenshot">
            </div>
        </section>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="vi" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eskimo UAT — Báo Cáo 5 Test Case Thất Bại (5 Failed Report)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #0a0f1d;
            --bg-surface: #111827;
            --bg-card: rgba(17, 24, 39, 0.95);
            --bg-card-hover: #1e293b;
            --border-color: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(239, 68, 68, 0.4);
            --border-focus: #ef4444;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-sub: #64748b;
            --primary: #3b82f6;
            --danger-red: #ef4444;
            --danger-dark: #991b1b;
            --danger-bg: rgba(239, 68, 68, 0.12);
            --danger-border: rgba(239, 68, 68, 0.35);
            --success-green: #10b981;
            --success-bg: rgba(16, 185, 129, 0.12);
            --accent-amber: #f59e0b;
            --accent-blue: #38bdf8;
            --accent-purple: #a855f7;
            --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        }}

        [data-theme="light"] {{
            --bg-base: #f8fafc;
            --bg-surface: #ffffff;
            --bg-card: #ffffff;
            --bg-card-hover: #f1f5f9;
            --border-color: #e2e8f0;
            --border-hover: #ef4444;
            --border-focus: #dc2626;
            --text-main: #0f172a;
            --text-muted: #475569;
            --text-sub: #94a3b8;
            --primary: #2563eb;
            --danger-red: #dc2626;
            --danger-dark: #b91c1c;
            --danger-bg: #fef2f2;
            --danger-border: #fca5a5;
            --success-green: #059669;
            --success-bg: #ecfdf5;
            --accent-amber: #d97706;
            --accent-blue: #0284c7;
            --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: var(--font-sans);
            background-color: var(--bg-base);
            color: var(--text-main);
            line-height: 1.6;
            padding: 24px 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Header */
        .report-header {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.18) 0%, rgba(17, 24, 39, 0.95) 100%);
            border: 1px solid var(--danger-border);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
        }}

        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
        }}

        .badge-app {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--danger-bg);
            color: var(--danger-red);
            font-size: 0.8rem;
            font-weight: 800;
            padding: 6px 14px;
            border-radius: 20px;
            border: 1px solid var(--danger-border);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .report-title {{
            font-size: 2.2rem;
            font-weight: 800;
            margin-top: 8px;
            letter-spacing: -0.03em;
            background: linear-gradient(90deg, #f87171, #fca5a5, #ffffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .report-subtitle {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-top: 6px;
            max-width: 900px;
        }}

        .header-actions {{
            display: flex;
            gap: 10px;
        }}

        .btn-action {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 9px 16px;
            border-radius: 10px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}

        .btn-action:hover {{
            background: var(--bg-card-hover);
            border-color: var(--danger-red);
        }}

        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
        }}

        .metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            box-shadow: var(--shadow-sm);
        }}

        .metric-card.card-fail {{
            border-color: var(--danger-border);
            background: linear-gradient(135deg, var(--danger-bg) 0%, var(--bg-card) 100%);
        }}

        .metric-icon {{
            font-size: 2rem;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 12px;
        }}

        .metric-val {{
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1.1;
        }}

        .metric-val.text-red {{ color: var(--danger-red); }}
        .metric-val.text-green {{ color: var(--success-green); }}
        .metric-val.text-amber {{ color: var(--accent-amber); }}
        .metric-val.text-blue {{ color: var(--accent-blue); }}

        .metric-lbl {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 700;
            margin-top: 3px;
        }}

        /* Navigation Tabs */
        .tab-nav {{
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }}

        .tab-btn {{
            padding: 14px 22px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            color: var(--text-muted);
            font-size: 0.95rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .tab-btn:hover {{
            background: var(--bg-card-hover);
            color: var(--text-main);
        }}

        .tab-btn.active {{
            background: var(--danger-bg);
            border-color: var(--danger-border);
            color: var(--danger-red);
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.25);
        }}

        .count-pill {{
            background: rgba(255, 255, 255, 0.1);
            color: inherit;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }}

        .tab-btn.active .count-pill {{
            background: var(--danger-red);
            color: #ffffff;
        }}

        /* Content Tab Sections */
        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Matrix Table Section */
        .matrix-section {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-sm);
        }}

        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .section-title {{
            font-size: 1.25rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .section-desc {{
            color: var(--text-muted);
            font-size: 0.88rem;
            margin-top: 3px;
        }}

        .table-responsive {{
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }}

        .report-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
            text-align: left;
        }}

        .report-table th {{
            background: var(--bg-card);
            padding: 12px 14px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}

        .report-table td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
        }}

        .suite-row, .matrix-row {{
            cursor: pointer;
            transition: background 0.15s ease;
        }}

        .suite-row:hover, .matrix-row:hover {{
            background: var(--bg-card-hover);
        }}

        /* Badges */
        .test-badge, .matrix-id {{
            background: rgba(239, 68, 68, 0.15);
            color: var(--danger-red);
            padding: 4px 10px;
            border-radius: 6px;
            font-family: var(--font-mono);
            font-weight: 800;
            font-size: 0.8rem;
            border: 1px solid var(--danger-border);
        }}

        .test-badge-lg {{
            background: var(--danger-red);
            color: white;
            padding: 5px 12px;
            border-radius: 8px;
            font-family: var(--font-mono);
            font-weight: 800;
            font-size: 0.95rem;
        }}

        .file-tag {{
            font-family: var(--font-mono);
            font-size: 0.78rem;
            color: #93c5fd;
            background: rgba(59, 130, 246, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
        }}

        .badge-module {{
            background: rgba(168, 85, 247, 0.15);
            color: #c084fc;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            white-space: nowrap;
        }}

        .badge-fail {{
            background: var(--danger-dark);
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
        }}

        .sev-badge {{
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .sev-critical, .sev-blocker {{
            background: var(--danger-dark);
            color: #ffffff;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
        }}

        .sev-high {{
            background: rgba(245, 158, 11, 0.25);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }}

        .sev-medium {{
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }}

        .ac-tag {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-blue);
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            font-family: var(--font-mono);
            white-space: nowrap;
        }}

        .type-pill, .type-tag {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: rgba(255, 255, 255, 0.06);
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.78rem;
            white-space: nowrap;
        }}

        .btn-jump {{
            background: var(--primary);
            color: white;
            border: none;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
            white-space: nowrap;
        }}

        .btn-jump:hover {{
            opacity: 0.85;
        }}

        /* Suite Cards & Defect Cards */
        .cards-list {{
            display: flex;
            flex-direction: column;
            gap: 24px;
            margin-bottom: 28px;
        }}

        .suite-card, .defect-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-left: 6px solid var(--danger-red);
            border-radius: 18px;
            padding: 24px;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }}

        .suite-card:hover, .defect-card:hover {{
            box-shadow: var(--shadow-lg);
            border-color: var(--danger-border);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }}

        .header-left {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .header-right {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .card-func-name {{
            font-family: var(--font-mono);
            font-size: 1.15rem;
            font-weight: 700;
            color: #60a5fa;
        }}

        .bug-id {{
            background: var(--danger-red);
            color: white;
            font-family: var(--font-mono);
            font-weight: 800;
            font-size: 0.95rem;
            padding: 4px 10px;
            border-radius: 6px;
        }}

        .bug-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-main);
        }}

        .file-pill, .time-pill {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-color);
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
        }}

        .btn-copy, .btn-copy-sm {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 7px 14px;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .btn-copy:hover, .btn-copy-sm:hover {{
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }}

        /* Card Sections */
        .info-block {{
            margin-bottom: 14px;
        }}

        .info-label {{
            font-size: 0.8rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            display: block;
            margin-bottom: 4px;
        }}

        .info-text {{
            font-size: 0.95rem;
            color: var(--text-main);
        }}

        .fail-reason-block {{
            background: var(--danger-bg);
            border: 1px solid var(--danger-border);
            padding: 14px 18px;
            border-radius: 12px;
        }}

        .fail-reason-text {{
            color: #fca5a5;
            font-weight: 600;
            font-size: 0.92rem;
        }}

        .traceback-block {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            margin-top: 14px;
        }}

        .trace-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.04);
            padding: 8px 14px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-color);
        }}

        .traceback-code {{
            padding: 14px;
            font-family: var(--font-mono);
            font-size: 0.82rem;
            color: #fca5a5;
            overflow-x: auto;
            white-space: pre-wrap;
            line-height: 1.5;
        }}

        /* Defect Card Dialogue Boxes */
        .dialogue-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 16px;
        }}

        .dialogue-box {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
        }}

        .box-label {{
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 8px;
        }}

        .prompt-text {{
            font-size: 1rem;
            font-weight: 600;
            color: #60a5fa;
            line-height: 1.5;
        }}

        .expected-text {{
            font-size: 0.9rem;
            color: #6ee7b7;
            line-height: 1.5;
        }}

        .actual-box {{
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid var(--danger-border);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
        }}

        .actual-text {{
            font-size: 0.92rem;
            color: #fecaca;
            line-height: 1.6;
            margin-bottom: 12px;
        }}

        .chips-container {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            padding-top: 10px;
            border-top: 1px dashed rgba(239, 68, 68, 0.25);
        }}

        .chips-label {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
        }}

        .chip {{
            background: rgba(255, 255, 255, 0.08);
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            color: var(--text-main);
            border: 1px solid var(--border-color);
        }}

        .analysis-box {{
            background: rgba(245, 158, 11, 0.06);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
        }}

        .analysis-title, .fix-title, .repro-title {{
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #fbbf24;
            margin-bottom: 6px;
        }}

        .fix-title {{
            color: #38bdf8;
            margin-top: 14px;
        }}

        .analysis-desc {{
            font-size: 0.9rem;
            color: var(--text-main);
            line-height: 1.6;
        }}

        .fix-desc {{
            font-size: 0.9rem;
            color: #e0f2fe;
            line-height: 1.6;
        }}

        .repro-box {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px 20px;
        }}

        .repro-title {{
            color: var(--text-muted);
            margin-bottom: 8px;
        }}

        .repro-list {{
            padding-left: 20px;
            font-size: 0.88rem;
            color: var(--text-muted);
        }}

        .repro-list li {{
            margin-bottom: 4px;
        }}

        .repro-list code {{
            background: rgba(255, 255, 255, 0.1);
            color: #fbbf24;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: var(--font-mono);
        }}

        /* Screenshot Section */
        .screenshot-section {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 28px;
        }}

        .screenshot-card {{
            display: flex;
            justify-content: center;
            background: var(--bg-base);
            padding: 24px;
            border-radius: 14px;
            border: 1px solid var(--border-color);
        }}

        .app-screenshot {{
            max-width: 380px;
            width: 100%;
            height: auto;
            border-radius: 16px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.7);
            border: 2px solid rgba(255, 255, 255, 0.1);
        }}

        /* Toast */
        .toast {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #10b981;
            color: white;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            box-shadow: var(--shadow-lg);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            z-index: 9999;
            pointer-events: none;
        }}

        .toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}

        @media (max-width: 900px) {{
            .dialogue-grid {{ grid-template-columns: 1fr; }}
            .report-title {{ font-size: 1.6rem; }}
            .header-top {{ flex-direction: column; }}
        }}

        @media print {{
            body {{ background: #fff; color: #000; padding: 0; }}
            .header-actions, .tab-nav, .btn-jump, .btn-copy, .btn-copy-sm {{ display: none; }}
            .report-header, .matrix-section, .suite-card, .defect-card {{ border: 1px solid #ccc; box-shadow: none; break-inside: avoid; }}
            .tab-content {{ display: block !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="report-header">
            <div class="header-top">
                <div>
                    <div class="badge-app">🚨 Eskimo UAT — Automation Failure Report</div>
                    <h1 class="report-title">Báo Cáo 5 Test Case Thất Bại (5 Failed Tests)</h1>
                    <p class="report-subtitle">Tập hợp toàn diện 5 bài kiểm thử thất bại trong đợt chạy test gần nhất giữa <code>test_ai_agent_scenarios.py</code> và <code>test_sale_ai_agent.py</code>, phân tích chi tiết nguyên nhân gốc rễ và khuyến nghị kỹ thuật cho Developers.</p>
                </div>
                <div class="header-actions">
                    <button class="btn-action" onclick="toggleTheme()">🌓 Đổi Giao Diện</button>
                    <button class="btn-action" onclick="window.print()">🖨️ In ra PDF / Xuất File</button>
                </div>
            </div>

            <!-- Metrics Grid -->
            <div class="metrics-grid">
                <div class="metric-card card-fail">
                    <div class="metric-icon">❌</div>
                    <div>
                        <div class="metric-val text-red">5 / 8</div>
                        <div class="metric-lbl">Test Suites Thất Bại (62.5%)</div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon">✅</div>
                    <div>
                        <div class="metric-val text-green">3 / 8</div>
                        <div class="metric-lbl">Test Suites Đạt (37.5%)</div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon">🚨</div>
                    <div>
                        <div class="metric-val text-amber">5 Critical</div>
                        <div class="metric-lbl">Lỗi Nghiêm Trọng AI Phản Hồi</div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon">🕒</div>
                    <div>
                        <div class="metric-val text-blue">2026-10-07</div>
                        <div class="metric-lbl">Thời Gian Chạy ({now_str})</div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Navigation Tabs -->
        <nav class="tab-nav">
            <button id="btn-tab-suites" class="tab-btn active" onclick="switchTab('suites')">
                🧪 5 Test Suites Thất Bại (Pytest View) <span class="count-pill">5 Tests</span>
            </button>
            <button id="btn-tab-defects" class="tab-btn" onclick="switchTab('defects')">
                🚨 Top 5 Lỗi Nghiêm Trọng Của AI (Defect Cards) <span class="count-pill">5 Bugs</span>
            </button>
            <button id="btn-tab-matrix" class="tab-btn" onclick="switchTab('matrix')">
                📊 Ma Trận Tất Cả Kịch Bản Lỗi (9 Scenarios) <span class="count-pill">9 Items</span>
            </button>
        </nav>

        <!-- TAB 1: 5 TEST SUITES VIEW -->
        <div id="tab-content-suites" class="tab-content active">
            <section class="matrix-section">
                <div class="section-header">
                    <div>
                        <h2 class="section-title">📊 Bảng Tổng Hợp 5 Test Suites Thất Bại Trong Lần Chạy Pytest Gần Nhất</h2>
                        <p class="section-desc">Lệnh chạy: <code>pytest tests/test_ai_agent_scenarios.py tests/test_sale_ai_agent.py -s</code> (Kết quả: 5 failed, 3 passed trong 8 test suites).</p>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="report-table">
                        <thead>
                            <tr>
                                <th>Mã Test</th>
                                <th>File Script</th>
                                <th>Tên Hàm Kiểm Thử (Function)</th>
                                <th>Nhóm Nghiệp Vụ</th>
                                <th>Trạng Thái</th>
                                <th>Số Kịch Bản Lỗi</th>
                                <th>Thời Gian</th>
                                <th>Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(suite_rows)}
                        </tbody>
                    </table>
                </div>
            </section>

            <div class="cards-list">
                {"".join(suite_cards)}
            </div>
        </div>

        <!-- TAB 2: TOP 5 CRITICAL DEFECTS VIEW -->
        <div id="tab-content-defects" class="tab-content">
            <section class="matrix-section">
                <div class="section-header">
                    <div>
                        <h2 class="section-title">🚨 Danh Sách 5 Ca Lỗi Nghiêm Trọng Của AI Agent Cần Chuyển Giao Devs</h2>
                        <p class="section-desc">Bao gồm các ca lỗi Timeout hàng đợi tin nhắn và Lệch ngữ cảnh (Context Drift) nghiêm trọng được phân tích nguyên nhân gốc rễ và hướng xử lý Backend.</p>
                    </div>
                </div>
            </section>

            <div class="cards-list">
                {"".join(defect_cards)}
            </div>
        </div>

        <!-- TAB 3: FULL SCENARIOS MATRIX -->
        <div id="tab-content-matrix" class="tab-content">
            <section class="matrix-section">
                <div class="section-header">
                    <div>
                        <h2 class="section-title">📊 Toàn Bộ 9 Kịch Bản Thất Bại Trong Phiên Kiểm Thử Hôm Nay</h2>
                        <p class="section-desc">Chi tiết từng câu hỏi kiểm thử gặp trục trặc phản hồi trong các nhóm kịch bản.</p>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="report-table">
                        <thead>
                            <tr>
                                <th>Mã Defect</th>
                                <th>Mã AC / Tag</th>
                                <th>Nhóm Nghiệp Vụ</th>
                                <th>Câu Hỏi Của Khách (Prompt)</th>
                                <th>Phân Loại Lỗi</th>
                                <th>Mức Độ</th>
                                <th>Hiện Tượng Lỗi Chi Tiết</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(matrix_rows)}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>

        <!-- Screenshot Section -->
        {screenshot_section}

    </div>

    <!-- Toast -->
    <div id="toast" class="toast">Đã sao chép nội dung Jira Bug Ticket!</div>

    <script>
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            const targetBtn = document.getElementById('btn-tab-' + tabId);
            const targetContent = document.getElementById('tab-content-' + tabId);

            if (targetBtn && targetContent) {{
                targetBtn.classList.add('active');
                targetContent.classList.add('active');
            }}
        }}

        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
        }}

        function jumpToElement(elemId) {{
            const el = document.getElementById(elemId);
            if (el) {{
                el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                el.style.borderColor = '#ef4444';
                el.style.boxShadow = '0 0 25px rgba(239, 68, 68, 0.5)';
                setTimeout(() => {{
                    el.style.borderColor = '';
                    el.style.boxShadow = '';
                }}, 2000);
            }}
        }}

        function copyJiraTicket(text, btn) {{
            navigator.clipboard.writeText(text).then(() => {{
                showToast("Đã copy Jira Bug Ticket thành công!");
                const originalText = btn.innerHTML;
                btn.innerHTML = "✅ Đã Copy!";
                setTimeout(() => {{ btn.innerHTML = originalText; }}, 1800);
            }}).catch(err => {{
                alert("Không thể copy tự động, vui lòng chọn text thủ công.");
            }});
        }}

        function copyText(text, btn) {{
            navigator.clipboard.writeText(text).then(() => {{
                showToast("Đã copy nội dung!");
                const originalText = btn.innerHTML;
                btn.innerHTML = "✅ Đã Copy!";
                setTimeout(() => {{ btn.innerHTML = originalText; }}, 1800);
            }});
        }}

        function showToast(msg) {{
            const toast = document.getElementById('toast');
            if (toast) {{
                toast.innerText = msg;
                toast.classList.add('show');
                setTimeout(() => {{ toast.classList.remove('show'); }}, 2500);
            }}
        }}
    </script>
</body>
</html>
"""
    return html_content


def main():
    print("Generating 5 Failed Cases HTML Report...")
    content = generate_html()
    os.makedirs(os.path.dirname(OUTPUT_HTML_PATH), exist_ok=True)
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Report exported to: {OUTPUT_HTML_PATH}")

    # Also update failed_cases_report.html
    with open(OUTPUT_FAILED_CASES_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated failed_cases_report.html: {OUTPUT_FAILED_CASES_PATH}")


if __name__ == "__main__":
    main()
