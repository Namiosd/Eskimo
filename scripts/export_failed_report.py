"""
Generator for Failed Test Cases HTML Report (Eskimo AI Agent).
Extracts failed test cases from the latest session, today's sessions, and cumulative sessions.
Produces a self-contained, interactive, developer-ready HTML report with:
- Dedicated tabs: Latest Run (3 Fails) | Today's Runs (5 Fails) | All Historical Defects (41 Fails)
- Defect Matrix Table with quick jump & 1-click Jira ticket copy
- Comprehensive Bug Cards: User Prompt, Actual AI Response, Expected Behavior, Technical Root Cause, Steps to Reproduce
- Embedded Base64 screenshot of the failure state
- Modern Dark/Light theme, glassmorphism, responsive, print/PDF ready
"""

import os
import re
import html
import base64
from datetime import datetime
from typing import List, Dict, Any

import sys
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from scripts.html_report_generator import (
    parse_markdown_transcript,
    format_markdown_text,
    DEFAULT_MD_PATH
)
from scripts.generate_defects_report import classify_defect_type

OUTPUT_FAILED_HTML = os.path.join(_ROOT_DIR, "reports", "html", "failed_cases_report.html")
SCREENSHOT_PATH = os.path.join(_ROOT_DIR, "reports", "screenshots", "debug_failure.png")


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


def get_technical_recommendation(tag: str, reason: str, query: str) -> str:
    """Provides specific backend / engineering fix advice for each defect."""
    r_lower = reason.lower()
    tag_upper = tag.upper()

    if "ac1.6" in tag_upper or ("promo" in query.lower() and "cashback" in r_lower):
        return (
            "<strong>Khuyến nghị kỹ thuật Backend:</strong> "
            "1. Kiểm tra bộ phân giải Intent (Intent Classifier): Intent <code>CHECK_PROMO_CODE</code> đang bị nhầm lẫn hoặc kích hoạt nhầm function <code>get_user_cashback_balance()</code>.<br>"
            "2. Khi truy vấn tài khoản không có mã giảm giá đang hoạt động, cần trả về thông báo rõ: <em>'Hiện tại bạn chưa có mã giảm giá nào'</em> thay vì tự động chuyển sang đọc số dư cashback."
        )
    elif "ac2" in tag_upper or ("japan" in query.lower() and "welcome" in r_lower):
        return (
            "<strong>Khuyến nghị kỹ thuật Backend:</strong> "
            "1. <strong>Đồng bộ hàng đợi tin nhắn (Message Queue Desync):</strong> Response của câu hỏi trước (AC1.6 hỏi về promo code) bị trễ và được stream trả về cho câu hỏi AC2.<br>"
            "2. Bổ sung cơ chế Request-Response Mapping bằng <code>message_id</code> / <code>turn_id</code> giữa Client và AI Engine để loại bỏ hiện tượng trả nhầm response của prompt cũ.<br>"
            "3. Kích hoạt đúng hàm <code>query_country_plans(destination='Japan')</code> và trả về payload hiển thị danh sách gói cước kèm Plan Carousel."
        )
    elif "ac4.2" in tag_upper or ("s24" in query.lower() or "iphone 6" in query.lower()):
        return (
            "<strong>Khuyến nghị kỹ thuật Backend:</strong> "
            "1. <strong>Khôi phục ngữ cảnh kiểm tra thiết bị:</strong> Prompt AC4.1 (chuyển sang tiếng Việt) khiến AI bị 'mất tập trung' vào nhiệm vụ trả lời thông tin thiết bị.<br>"
            "2. AI cần tra cứu Database tương thích: Samsung Galaxy S24 (Hỗ trợ eSIM tùy biến thể khu vực) và iPhone 6 (Không hỗ trợ eSIM vì chỉ hỗ trợ từ iPhone XS/XR trở lên).<br>"
            "3. Điều chỉnh System Prompt: Yêu cầu AI luôn trả lời trực diện câu hỏi của người dùng trước khi đưa ra thông tin giới thiệu dịch vụ chung."
        )
    elif "timeout" in r_lower:
        return (
            "<strong>Khuyến nghị kỹ thuật Backend:</strong> "
            "1. <strong>Tối ưu thời gian phản hồi (Latency Optimization):</strong> Kiểm tra kết nối mạng giữa Appium server, Mobile App và AI Backend Gateway.<br>"
            "2. Cấu hình Timeout & Retry trên API Gateway và Streaming Socket (Server-Sent Events) để tránh treo quá 40s.<br>"
            "3. Bổ sung Fallback Message khi AI Gateway quá tải: <em>'Hệ thống đang xử lý, vui lòng chờ trong giây lát...'</em>"
        )
    elif "lệch ngữ cảnh" in r_lower:
        return (
            "<strong>Khuyến nghị kỹ thuật Backend:</strong> "
            "1. Reset Session Context khi bắt đầu phiên mới hoặc khi người dùng đổi chủ đề đột ngột.<br>"
            "2. Rà soát lại Prompt Engineering và Chain-of-Thought (CoT) để AI không tự ý nội suy thông tin của kịch bản trước đó."
        )
    return (
        "<strong>Khuyến nghị kỹ thuật:</strong> Kiểm tra lại mapping từ khóa kiểm thử trong kịch bản và xác nhận lại System Prompt của AI Agent trên môi trường UAT."
    )


def build_failed_report_html() -> str:
    """Builds the specialized Failed Cases HTML Report."""
    sessions = parse_markdown_transcript(DEFAULT_MD_PATH)
    if not sessions:
        return ""

    today_str = datetime.now().strftime("%Y-%m-%d")

    # Group sessions
    today_sessions = [s for s in sessions if today_str in s.get("session_full_time", "")]
    if not today_sessions:
        today_sessions = [sessions[-1]]

    # 1. Latest run batch sessions (all sessions belonging to the most recent test run batch)
    latest_run_sessions = []
    if today_sessions:
        last_dt = datetime.strptime(today_sessions[-1]["session_full_time"], "%Y-%m-%d %H:%M:%S")
        for s in reversed(today_sessions):
            try:
                s_dt = datetime.strptime(s["session_full_time"], "%Y-%m-%d %H:%M:%S")
                # Group sessions run within 2 hours into the latest batch
                if (last_dt - s_dt).total_seconds() <= 7200:
                    latest_run_sessions.append(s)
                else:
                    break
            except Exception:
                pass
        latest_run_sessions.reverse()
    if not latest_run_sessions:
        latest_run_sessions = [today_sessions[-1]]

    start_time_str = latest_run_sessions[0]["session_full_time"].split(" ")[1][:5]
    end_time_str = latest_run_sessions[-1]["session_full_time"].split(" ")[1][:5]
    latest_run_time_range = f"{start_time_str} - {end_time_str}"
    today_date_display = datetime.now().strftime("%d/%m")

    # Collect errors
    # 1. Latest run batch errors (deduplicated by ac_tag + query)
    latest_errors = []
    seen_latest = set()
    latest_total_turns = sum(len(s.get("entries", [])) for s in latest_run_sessions)
    for s in latest_run_sessions:
        s_title = s.get("session_name", "")
        for e in s.get("entries", []):
            if e.get("is_error"):
                key = (e.get("ac_tag"), e.get("query"))
                if key not in seen_latest:
                    seen_latest.add(key)
                    latest_errors.append({"session": s_title, "entry": e})

    # 2. Today's errors (deduplicated by ac_tag + query)
    today_errors = []
    seen_today = set()
    for s in reversed(today_sessions):
        s_title = s.get("session_name", "")
        for e in s.get("entries", []):
            if e.get("is_error"):
                key = (e.get("ac_tag"), e.get("query"))
                if key not in seen_today:
                    seen_today.add(key)
                    today_errors.append({"session": s_title, "entry": e})

    # 3. All historical errors
    all_errors = []
    seen_all = set()
    for s in reversed(sessions):
        s_title = s.get("session_name", "")
        for e in s.get("entries", []):
            if e.get("is_error"):
                key = (e.get("ac_tag"), e.get("query"))
                if key not in seen_all:
                    seen_all.add(key)
                    all_errors.append({"session": s_title, "entry": e})

    # Screenshot base64
    screenshot_b64 = get_base64_image(SCREENSHOT_PATH)

    # Classifications for latest errors
    latest_classified = []
    for idx, item in enumerate(latest_errors, 1):
        e = item["entry"]
        cls = classify_defect_type(e.get("reason", ""))
        latest_classified.append({
            "idx": idx,
            "id": f"FAIL-{idx:02d}",
            "entry": e,
            "classification": cls,
            "session": item["session"]
        })

    # Classifications for today errors
    today_classified = []
    for idx, item in enumerate(today_errors, 1):
        e = item["entry"]
        cls = classify_defect_type(e.get("reason", ""))
        today_classified.append({
            "idx": idx,
            "id": f"TDY-{idx:02d}",
            "entry": e,
            "classification": cls,
            "session": item["session"]
        })

    # Classifications for all errors
    all_classified = []
    for idx, item in enumerate(all_errors, 1):
        e = item["entry"]
        cls = classify_defect_type(e.get("reason", ""))
        all_classified.append({
            "idx": idx,
            "id": f"ALL-{idx:02d}",
            "entry": e,
            "classification": cls,
            "session": item["session"]
        })

    def render_rows(items: List[Dict[str, Any]], scope_prefix: str) -> str:
        rows = []
        for it in items:
            e = it["entry"]
            cls = it["classification"]
            dom_id = f"card-{scope_prefix}-{it['idx']}"
            ac_tag = html.escape(e.get("ac_tag", ""))
            query = html.escape(e.get("query", ""))
            reason = html.escape(e.get("reason", ""))
            short_reason = reason[:85] + ("..." if len(reason) > 85 else "")
            
            # Domain detection
            domain = "Quy trình AC"
            tl = ac_tag.lower()
            if "sales" in tl: domain = "Sales & Plans"
            elif "compat" in tl: domain = "Compatibility"
            elif "conn" in tl: domain = "Connection"
            elif "usage" in tl: domain = "Usage & Plans"
            elif "cashback" in tl: domain = "Cashback"
            elif "complaint" in tl: domain = "Complaints"

            rows.append(f"""
            <tr class="bug-row" onclick="jumpToCard('{dom_id}')">
                <td class="col-id"><strong>{it['id']}</strong></td>
                <td class="col-sev"><span class="badge-sev {cls['severity_class']}">{cls['severity']}</span></td>
                <td class="col-domain"><span class="badge-domain">{domain}</span></td>
                <td class="col-tag"><code>{ac_tag.split(' - ')[0]}</code></td>
                <td class="col-q"><strong>{query}</strong></td>
                <td class="col-type"><span class="type-pill">{cls['icon']} {cls['type']}</span></td>
                <td class="col-reason"><span class="reason-snippet">{short_reason}</span></td>
                <td class="col-action"><button class="btn-sm-jump" onclick="event.stopPropagation(); jumpToCard('{dom_id}')">🔍 Chi tiết</button></td>
            </tr>
            """)
        return "".join(rows)

    def render_cards(items: List[Dict[str, Any]], scope_prefix: str) -> str:
        cards = []
        for it in items:
            e = it["entry"]
            cls = it["classification"]
            dom_id = f"card-{scope_prefix}-{it['idx']}"
            defect_id = it["id"]
            ac_tag = html.escape(e.get("ac_tag", ""))
            query = html.escape(e.get("query", ""))
            raw_resp = e.get("response", "")
            resp_formatted = format_markdown_text(raw_resp)
            reason = html.escape(e.get("reason", ""))
            expected = html.escape(e.get("expected", ""))
            timestamp = html.escape(e.get("time", ""))
            session_name = html.escape(it["session"])
            tech_fix = get_technical_recommendation(ac_tag, e.get("reason", ""), e.get("query", ""))

            # Domain detection
            domain = "Quy trình AC"
            tl = ac_tag.lower()
            if "sales" in tl: domain = "Sales & Plans"
            elif "compat" in tl: domain = "Compatibility"
            elif "conn" in tl: domain = "Connection"
            elif "usage" in tl: domain = "Usage & Plans"
            elif "cashback" in tl: domain = "Cashback"
            elif "complaint" in tl: domain = "Complaints"

            jira_text = (
                f"*Issue:* [{defect_id}] {ac_tag}\\n"
                f"*Severity:* {cls['severity']}\\n"
                f"*Defect Type:* {cls['type']}\\n"
                f"*User Query:* {e.get('query')}\\n"
                f"*Actual AI Response:* {raw_resp[:350]}...\\n"
                f"*Expected Behavior:* {e.get('expected')}\\n"
                f"*Root Cause:* {e.get('reason')}\\n"
                f"*Steps to Reproduce:*\\n1. Open Eskimo App -> Ask Eski Chat\\n2. Ask: {e.get('query')}\\n3. Observe AI response"
            )
            jira_attr = html.escape(jira_text)

            chips_html = ""
            chips = e.get("chips", [])
            if chips:
                chips_badges = "".join([f'<span class="chip-badge">{html.escape(c)}</span>' for c in chips])
                chips_html = f"""
                <div class="chips-container">
                    <span class="chips-label">💡 Gợi ý (Chips) AI sinh ra:</span>
                    <div class="chips-list">{chips_badges}</div>
                </div>
                """

            cards.append(f"""
            <div id="{dom_id}" class="defect-card" data-domain="{domain.lower()}" data-type="{cls['type_code']}">
                <div class="card-header">
                    <div class="header-left">
                        <span class="bug-code">{defect_id}</span>
                        <span class="badge-sev {cls['severity_class']}">{cls['severity']}</span>
                        <span class="card-ac-tag">{ac_tag}</span>
                    </div>
                    <div class="header-right">
                        <span class="defect-cat-pill">{cls['icon']} {cls['type']}</span>
                        <button class="btn-copy-ticket" onclick="copyBugTicket(this, '{jira_attr}')">📋 Copy Jira Bug</button>
                    </div>
                </div>

                <div class="card-body">
                    <!-- Prompt Box -->
                    <div class="section-box prompt-box">
                        <div class="box-title"><span class="icon">👤</span> 1. USER PROMPT (CÂU HỎI TỪ NGƯỜI DÙNG)</div>
                        <div class="box-content prompt-text">"{query}"</div>
                    </div>

                    <!-- Response Box -->
                    <div class="section-box response-box">
                        <div class="box-title"><span class="icon">🤖</span> 2. ACTUAL AI RESPONSE (PHẢN HỒI THỰC TẾ BỊ SAI LỆCH)</div>
                        <div class="box-content response-text">{resp_formatted}</div>
                        {chips_html}
                    </div>

                    <!-- Defect Analysis Box -->
                    <div class="section-box defect-analysis-box">
                        <div class="box-title"><span class="icon">🚨</span> 3. PHÂN TÍCH LỖI & NGUYÊN NHÂN (ROOT CAUSE ANALYSIS)</div>
                        <div class="analysis-grid">
                            <div class="analysis-item">
                                <span class="item-label">🔴 Nguyên nhân lỗi:</span>
                                <span class="item-val highlight-red">{reason}</span>
                            </div>
                            <div class="analysis-item">
                                <span class="item-label">🎯 Hành vi kỳ vọng:</span>
                                <span class="item-val highlight-green">{expected}</span>
                            </div>
                            <div class="analysis-item">
                                <span class="item-label">🕒 Phiên ghi nhận:</span>
                                <span class="item-val text-muted">{timestamp} ({session_name})</span>
                            </div>
                        </div>
                    </div>

                    <!-- Technical Fix Recommendation -->
                    <div class="section-box tech-box">
                        <div class="box-title"><span class="icon">💻</span> 4. KHUYẾN NGHỊ KỸ THUẬT CHO DEVELOPERS</div>
                        <div class="tech-content">{tech_fix}</div>
                    </div>

                    <!-- Reproduction Steps -->
                    <div class="section-box repro-box">
                        <div class="box-title"><span class="icon">🛠️</span> 5. CÁC BƯỚC TÁI HIỆN (STEPS TO REPRODUCE)</div>
                        <ol class="repro-list">
                            <li>Khởi chạy ứng dụng <strong>Eskimo eSIM (UAT)</strong> và đăng nhập tài khoản kiểm thử.</li>
                            <li>Tại màn hình chính, nhấn vào biểu tượng <strong>In-App Chat ("Ask Eski!")</strong> để mở giao diện hội thoại.</li>
                            <li>Gửi câu hỏi chính xác: <code>{query}</code></li>
                            <li>Quan sát nội dung phản hồi thực tế của AI và đối chiếu với hành vi kỳ vọng nêu trên.</li>
                        </ol>
                    </div>
                </div>
            </div>
            """)
        return "".join(cards)

    latest_rows = render_rows(latest_classified, "latest")
    today_rows = render_rows(today_classified, "today")
    all_rows = render_rows(all_classified, "all")

    latest_cards = render_cards(latest_classified, "latest")
    today_cards = render_cards(today_classified, "today")
    all_cards = render_cards(all_classified, "all")

    latest_count = len(latest_classified)
    today_count = len(today_classified)
    all_count = len(all_classified)

    latest_passed = max(0, latest_total_turns - latest_count)
    fail_rate = round((latest_count / latest_total_turns * 100), 1) if latest_total_turns else 0

    screenshot_section = ""
    if screenshot_b64:
        screenshot_section = f"""
        <section class="screenshot-section">
            <div class="section-header">
                <div>
                    <h2 class="section-title">📸 Ảnh Chụp Màn Hình Lỗi Thực Tế (Failure Screenshot)</h2>
                    <p class="section-desc">Giao diện ứng dụng tại thời điểm ghi nhận lỗi kết thúc phiên kiểm thử.</p>
                </div>
            </div>
            <div class="screenshot-card">
                <img src="{screenshot_b64}" alt="App Failure Screenshot" class="app-screenshot">
            </div>
        </section>
        """

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html lang="vi" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eskimo AI Chatbot — Báo Cáo Các Test Case Thất Bại (Failed Report)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #0a0e17;
            --bg-surface: #111827;
            --bg-card: #1c2433;
            --bg-card-hover: #242f42;
            --border-color: rgba(255, 255, 255, 0.09);
            --border-focus: #ef4444;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --text-sub: #6b7280;
            --primary: #3b82f6;
            --danger-red: #ef4444;
            --danger-dark: #991b1b;
            --danger-bg: rgba(239, 68, 68, 0.12);
            --danger-border: rgba(239, 68, 68, 0.35);
            --success-green: #10b981;
            --success-bg: rgba(16, 185, 129, 0.12);
            --accent-amber: #f59e0b;
            --accent-purple: #8b5cf6;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        }}

        [data-theme="light"] {{
            --bg-base: #f3f4f6;
            --bg-surface: #ffffff;
            --bg-card: #f9fafb;
            --bg-card-hover: #f3f4f6;
            --border-color: #e5e7eb;
            --border-focus: #dc2626;
            --text-main: #111827;
            --text-muted: #4b5563;
            --text-sub: #9ca3af;
            --primary: #2563eb;
            --danger-red: #dc2626;
            --danger-dark: #b91c1c;
            --danger-bg: #fef2f2;
            --danger-border: #fca5a5;
            --success-green: #059669;
            --success-bg: #ecfdf5;
            --accent-amber: #d97706;
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
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(17, 24, 39, 0.95) 100%);
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
            margin-bottom: 20px;
        }}

        .badge-app {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--danger-bg);
            color: var(--danger-red);
            font-size: 0.8rem;
            font-weight: 700;
            padding: 5px 12px;
            border-radius: 20px;
            border: 1px solid var(--danger-border);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .report-title {{
            font-size: 2rem;
            font-weight: 800;
            margin-top: 8px;
            letter-spacing: -0.02em;
            background: linear-gradient(90deg, #f87171, #fca5a5, #ffffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .report-subtitle {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-top: 4px;
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
            border-color: var(--text-muted);
        }}

        /* Metrics */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            border-top: 1px solid var(--border-color);
            padding-top: 22px;
        }}

        .metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .metric-card.card-fail {{
            background: var(--danger-bg);
            border-color: var(--danger-border);
        }}

        .metric-icon {{
            font-size: 2rem;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.05);
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
        .metric-val.text-blue {{ color: var(--primary); }}

        .metric-lbl {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 700;
        }}

        /* Scope Tab Switcher */
        .scope-nav {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .scope-btn {{
            padding: 12px 20px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            color: var(--text-muted);
            font-size: 0.95rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .scope-btn.active {{
            background: var(--danger-bg);
            border-color: var(--danger-border);
            color: var(--danger-red);
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);
        }}

        .scope-btn .count-badge {{
            background: rgba(255, 255, 255, 0.1);
            color: inherit;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }}

        .scope-btn.active .count-badge {{
            background: var(--danger-red);
            color: #ffffff;
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
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .section-title {{
            font-size: 1.25rem;
            font-weight: 700;
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

        .bug-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
            text-align: left;
        }}

        .bug-table th {{
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

        .bug-table td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
        }}

        .bug-row {{
            cursor: pointer;
            transition: background 0.15s ease;
        }}

        .bug-row:hover {{
            background: var(--bg-card-hover);
        }}

        .badge-sev {{
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .sev-critical {{
            background: var(--danger-dark);
            color: #ffffff;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
        }}

        .sev-high {{
            background: rgba(245, 158, 11, 0.25);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }}

        .badge-domain {{
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            white-space: nowrap;
        }}

        .type-pill {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: rgba(255, 255, 255, 0.06);
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.78rem;
            white-space: nowrap;
        }}

        .reason-snippet {{
            color: #f87171;
            font-weight: 500;
            font-size: 0.82rem;
        }}

        .btn-sm-jump {{
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

        .btn-sm-jump:hover {{
            opacity: 0.85;
        }}

        /* Defect Cards */
        .cards-container {{
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 28px;
        }}

        .defect-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-left: 6px solid var(--danger-red);
            border-radius: 16px;
            padding: 24px;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }}

        .defect-card:hover {{
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
            gap: 10px;
            flex-wrap: wrap;
        }}

        .bug-code {{
            font-size: 1.1rem;
            font-weight: 800;
            color: var(--text-main);
            font-family: var(--font-mono);
        }}

        .card-ac-tag {{
            font-size: 0.95rem;
            font-weight: 700;
            color: #93c5fd;
        }}

        .defect-cat-pill {{
            background: var(--danger-bg);
            color: var(--danger-red);
            border: 1px solid var(--danger-border);
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 700;
        }}

        .btn-copy-ticket {{
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

        .btn-copy-ticket:hover {{
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }}

        /* Section Boxes in Card */
        .section-box {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 14px;
        }}

        .box-title {{
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .prompt-text {{
            font-size: 1.05rem;
            font-weight: 600;
            color: #60a5fa;
            font-family: var(--font-sans);
        }}

        .response-box {{
            border-left: 3px solid #f87171;
            background: rgba(239, 68, 68, 0.04);
        }}

        .response-text {{
            font-size: 0.95rem;
            color: #fca5a5;
            white-space: pre-wrap;
            line-height: 1.6;
        }}

        .chips-container {{
            margin-top: 14px;
            padding-top: 12px;
            border-top: 1px dashed var(--border-color);
        }}

        .chips-label {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            display: block;
            margin-bottom: 6px;
        }}

        .chips-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .chip-badge {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 4px 10px;
            border-radius: 14px;
            font-size: 0.78rem;
        }}

        /* Analysis Grid */
        .analysis-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
        }}

        .analysis-item {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .item-label {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--text-muted);
        }}

        .item-val {{
            font-size: 0.92rem;
            font-weight: 600;
        }}

        .highlight-red {{
            color: #f87171;
            background: rgba(239, 68, 68, 0.1);
            padding: 6px 12px;
            border-radius: 6px;
            border-left: 3px solid #ef4444;
        }}

        .highlight-green {{
            color: #34d399;
            background: rgba(16, 185, 129, 0.1);
            padding: 6px 12px;
            border-radius: 6px;
            border-left: 3px solid #10b981;
        }}

        /* Tech Box */
        .tech-box {{
            background: rgba(59, 130, 246, 0.06);
            border-color: rgba(59, 130, 246, 0.25);
            border-left: 3px solid var(--primary);
        }}

        .tech-content {{
            font-size: 0.9rem;
            color: var(--text-main);
            line-height: 1.6;
        }}

        .tech-content code {{
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: var(--font-mono);
            color: #93c5fd;
            font-size: 0.85rem;
        }}

        /* Repro list */
        .repro-list {{
            padding-left: 20px;
            font-size: 0.88rem;
            color: var(--text-muted);
        }}

        .repro-list li {{
            margin-bottom: 6px;
        }}

        .repro-list code {{
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: var(--font-mono);
            color: #fbbf24;
            font-size: 0.85rem;
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
            padding: 20px;
            border-radius: 14px;
            border: 1px solid var(--border-color);
        }}

        .app-screenshot {{
            max-width: 360px;
            width: 100%;
            height: auto;
            border-radius: 14px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
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

        .flash-highlight {{
            animation: highlightPulse 2s ease;
        }}

        @keyframes highlightPulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }}
            50% {{ box-shadow: 0 0 25px 8px rgba(239, 68, 68, 0.5); }}
            100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
        }}

        @media (max-width: 768px) {{
            .report-title {{ font-size: 1.5rem; }}
            .header-top {{ flex-direction: column; }}
            .metrics-grid {{ grid-template-columns: 1fr 1fr; }}
            .card-header {{ flex-direction: column; align-items: flex-start; }}
        }}

        @media print {{
            body {{ background: #fff; color: #000; padding: 0; }}
            .header-actions, .scope-nav, .btn-sm-jump, .btn-copy-ticket {{ display: none; }}
            .report-header, .matrix-section, .defect-card {{ border: 1px solid #ccc; box-shadow: none; break-inside: avoid; }}
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
                    <h1 class="report-title">Báo Cáo Các Test Case Thất Bại (Failed Cases)</h1>
                    <p class="report-subtitle">Tập hợp chuyên sâu các kịch bản kiểm thử AI Agent gặp sự cố phản hồi lệch ngữ cảnh / timeout để chuyển giao Developer xử lý.</p>
                </div>
                <div class="header-actions">
                    <button class="btn-action" onclick="toggleTheme()">🌓 Đổi Giao Diện</button>
                    <button class="btn-action" onclick="window.print()">🖨️ Xuất PDF / In</button>
                </div>
            </div>

            <!-- Executive Metrics of Latest Run -->
            <div class="metrics-grid">
                <div class="metric-card card-fail">
                    <div class="metric-icon">❌</div>
                    <div>
                        <div class="metric-val text-red">{latest_count} / {latest_total_turns}</div>
                        <div class="metric-lbl">Lỗi Phiên Mới Nhất ({fail_rate}%)</div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon">✅</div>
                    <div>
                        <div class="metric-val text-green">{latest_passed} / {latest_total_turns}</div>
                        <div class="metric-lbl">Đạt Phiên Mới Nhất</div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon">📅</div>
                    <div>
                        <div class="metric-val text-amber">{today_count}</div>
                        <div class="metric-lbl">Tổng Lỗi Hôm Nay ({today_str})</div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon">🌐</div>
                    <div>
                        <div class="metric-val text-blue">{all_count}</div>
                        <div class="metric-lbl">Toàn Bộ Lỗi Tích Lũy</div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Scope Navigation Tabs -->
        <nav class="scope-nav">
            <button id="btn-scope-latest" class="scope-btn active" onclick="switchScope('latest')">
                🔥 Đợt Chạy Vừa Qua ({latest_run_time_range}) <span class="count-badge">{latest_count} Lỗi</span>
            </button>
            <button id="btn-scope-today" class="scope-btn" onclick="switchScope('today')">
                📅 Tất Cả Các Lỗi Hôm Nay ({today_date_display}) <span class="count-badge">{today_count} Lỗi</span>
            </button>
            <button id="btn-scope-all" class="scope-btn" onclick="switchScope('all')">
                🌐 Toàn Bộ Lỗi Tích Lũy <span class="count-badge">{all_count} Lỗi</span>
            </button>
        </nav>

        <!-- SCOPE: LATEST -->
        <div id="scope-content-latest" class="scope-content">
            <section class="matrix-section">
                <div class="section-header">
                    <div>
                        <h2 class="section-title">📊 Bảng Tổng Hợp Lỗi — Đợt Chạy Vừa Qua ({latest_run_time_range})</h2>
                        <p class="section-desc">Gồm {latest_count} kịch bản thất bại trên tổng số {latest_total_turns} câu hỏi kiểm thử được thực thi.</p>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="bug-table">
                        <thead>
                            <tr>
                                <th>Mã Bug</th>
                                <th>Mức Độ</th>
                                <th>Nhóm Nghiệp Vụ</th>
                                <th>AC Tag</th>
                                <th>User Prompt (Câu hỏi)</th>
                                <th>Loại Lỗi</th>
                                <th>Lý Do Chi Tiết</th>
                                <th>Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {latest_rows}
                        </tbody>
                    </table>
                </div>
            </section>

            <div class="cards-container">
                {latest_cards}
            </div>
        </div>

        <!-- SCOPE: TODAY -->
        <div id="scope-content-today" class="scope-content" style="display: none;">
            <section class="matrix-section">
                <div class="section-header">
                    <div>
                        <h2 class="section-title">📊 Bảng Tổng Hợp Lỗi — Tất Cả Các Phiên Hôm Nay ({today_str})</h2>
                        <p class="section-desc">Bao gồm các kịch bản bị Timeout buổi sáng và các lỗi lệch ngữ cảnh buổi chiều.</p>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="bug-table">
                        <thead>
                            <tr>
                                <th>Mã Bug</th>
                                <th>Mức Độ</th>
                                <th>Nhóm Nghiệp Vụ</th>
                                <th>AC Tag</th>
                                <th>User Prompt (Câu hỏi)</th>
                                <th>Loại Lỗi</th>
                                <th>Lý Do Chi Tiết</th>
                                <th>Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {today_rows}
                        </tbody>
                    </table>
                </div>
            </section>

            <div class="cards-container">
                {today_cards}
            </div>
        </div>

        <!-- SCOPE: ALL -->
        <div id="scope-content-all" class="scope-content" style="display: none;">
            <section class="matrix-section">
                <div class="section-header">
                    <div>
                        <h2 class="section-title">📊 Toàn Bộ Lỗi Đã Ghi Nhận Trong Lịch Sử Kiểm Thử ({all_count} Defects)</h2>
                        <p class="section-desc">Lịch sử tích lũy qua tất cả các phiên kiểm thử In-App Chatbot.</p>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="bug-table">
                        <thead>
                            <tr>
                                <th>Mã Bug</th>
                                <th>Mức Độ</th>
                                <th>Nhóm Nghiệp Vụ</th>
                                <th>AC Tag</th>
                                <th>User Prompt (Câu hỏi)</th>
                                <th>Loại Lỗi</th>
                                <th>Lý Do Chi Tiết</th>
                                <th>Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {all_rows}
                        </tbody>
                    </table>
                </div>
            </section>

            <div class="cards-container">
                {all_cards}
            </div>
        </div>

        <!-- Screenshot Section -->
        {screenshot_section}

    </div>

    <!-- Toast Notification -->
    <div id="toast" class="toast">Đã copy nội dung Jira Bug Ticket!</div>

    <script>
        function switchScope(scope) {{
            // buttons
            document.querySelectorAll('.scope-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-scope-' + scope).classList.add('active');

            // contents
            document.querySelectorAll('.scope-content').forEach(c => c.style.display = 'none');
            document.getElementById('scope-content-' + scope).style.display = 'block';
        }}

        function toggleTheme() {{
            const html = document.documentElement;
            const current = html.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
        }}

        function jumpToCard(cardId) {{
            const target = document.getElementById(cardId);
            if (target) {{
                target.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                target.classList.add('flash-highlight');
                setTimeout(() => target.classList.remove('flash-highlight'), 2000);
            }}
        }}

        function copyBugTicket(btn, text) {{
            const cleanText = text.replace(/\\\\n/g, '\\n');
            navigator.clipboard.writeText(cleanText).then(() => {{
                showToast("Đã copy định dạng Jira Bug Ticket!");
            }}).catch(() => {{
                showToast("Không thể sao chép");
            }});
        }}

        function showToast(msg) {{
            const t = document.getElementById('toast');
            t.innerText = msg;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 2500);
        }}
    </script>
</body>
</html>
"""
    return html_content


def export_failed_report(output_path: str = OUTPUT_FAILED_HTML) -> str:
    """Exports the failed cases HTML report."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    html_content = build_failed_report_html()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    out = export_failed_report()
    print(f"Failed cases HTML report successfully exported to: {out}")
