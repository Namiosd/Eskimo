"""
HTML Report Generator for Eskimo Sale AI Agent (Eski) Conversations.
Generates a standalone, interactive, visually stunning HTML report with:
- Red highlight and detailed diagnostic analysis for all AI defects/errors
- Top 6 Critical AI Errors summary table with quick jump links
- Comprehensive Q&A transcript across all test sessions
- Pass/Fail stats, real-time search, interactive filters (All / Errors Only / Passed)
- Modern Dark & Light theme with glassmorphism aesthetics
- Responsive design, mobile-friendly, export to PDF
"""

import os
import re
import html
from datetime import datetime
from typing import List, Dict, Any, Optional

import sys
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

_REPORTS_DIR = os.path.join(_ROOT_DIR, "reports")
_LOGS_DIR = os.path.join(_REPORTS_DIR, "logs")
_HTML_DIR = os.path.join(_REPORTS_DIR, "html")

_CANDIDATE_MD = os.path.join(_LOGS_DIR, "ai_chat_transcript.md")
DEFAULT_MD_PATH = _CANDIDATE_MD if os.path.exists(_CANDIDATE_MD) else os.path.join(_ROOT_DIR, "ai_chat_transcript.md")
DEFAULT_HTML_PATH = os.path.join(_HTML_DIR, "ai_chat_report.html")

# Try to import scenario data if available
try:
    from data.ai_agent_scenarios_data import AI_AGENT_SCENARIOS
    SCENARIOS_MAP = {s['id']: s for s in AI_AGENT_SCENARIOS}
except Exception:
    try:
        from ai_agent_scenarios_data import AI_AGENT_SCENARIOS
        SCENARIOS_MAP = {s['id']: s for s in AI_AGENT_SCENARIOS}
    except Exception:
        SCENARIOS_MAP = {}

# Acceptance Criteria specifications
AC_RULES = {
    "AC1.1": {
        "keywords": ["mb", "gb", "data", "plan", "remaining", "left", "active", "balance"],
        "behavior": "Kiểm tra và báo chính xác số dung lượng data còn lại và số gói cước đang kích hoạt."
    },
    "AC1.2": {
        "keywords": ["purchase", "bought", "history", "order", "plan", "vietnam", "destination", "no purchase", "haven't", "past"],
        "behavior": "Hiển thị danh sách lịch sử các gói cước đã mua trong quá khứ và gợi ý mua lại."
    },
    "AC1.3": {
        "keywords": ["referral", "code", "friend", "bonus", "500", "mb", "share", "referred"],
        "behavior": "Báo số lượng bạn bè đã giới thiệu, dung lượng data thưởng và mã giới thiệu (referral code)."
    },
    "AC1.4": {
        "keywords": ["validity", "expiry", "countries", "roaming", "esim", "plan", "data", "eskimo"],
        "behavior": "Cung cấp thông tin chi tiết về các loại gói cước Eskimo và thời hạn sử dụng (no expiry / validity)."
    },
    "AC1.5": {
        "keywords": ["cashback", "$", "usd", "balance", "amount", "current", "earn", "0"],
        "behavior": "Thông báo số dư tiền hoàn (cashback) hiện tại và điều kiện rút tiền."
    },
    "AC1.6": {
        "keywords": ["promo", "code", "discount", "voucher", "promotion", "offer", "available", "currently", "don't have", "no"],
        "behavior": "Thông báo mã khuyến mại / voucher giảm giá hiện có trên tài khoản."
    },
    "AC2": {
        "keywords": ["1gb", "3gb", "5gb", "10gb", "options", "plans", "japan", "list"],
        "behavior": "Gợi ý đồng thời nhiều gói cước phù hợp dưới dạng danh sách hoặc carousel lựa chọn."
    },
    "AC3.1": {
        "keywords": ["settings", "sim", "network", "qr", "esim", "add", "install", "android", "connections"],
        "behavior": "Hướng dẫn chi tiết từng bước cài đặt eSIM trên hệ điều hành Android."
    },
    "AC3.2": {
        "keywords": ["settings", "cellular", "mobile data", "add esim", "qr", "iphone", "ios", "install"],
        "behavior": "Hướng dẫn chi tiết từng bước cài đặt eSIM trên iPhone / iOS."
    },
    "AC4.1": {
        "keywords": ["chào", "eskimo", "gói", "cước", "du lịch", "dữ liệu", "kết nối", "bạn", "tôi", "cho", "xin chào"],
        "behavior": "Chuyển đổi ngôn ngữ phản hồi sang Tiếng Việt một cách tự nhiên và chính xác."
    },
    "AC4.2": {
        "keywords": ["s24", "samsung", "compatible", "supports", "yes", "support", "variant", "tương thích", "không tương thích", "không hỗ trợ"],
        "behavior": "Xác nhận khả năng tương thích eSIM của Samsung Galaxy S24 và thông báo iPhone 6 không hỗ trợ."
    }
}


def evaluate_response(ac_tag: str, query: str, response: str) -> Dict[str, Any]:
    """
    Evaluates whether an AI response is valid or defective, returning failure reasons.
    """
    resp_lower = response.lower()
    
    # 1. Timeout / No response check
    if "[timeout" in resp_lower or not response.strip():
        return {
            "is_error": True,
            "status": "failed",
            "reason": "Hệ thống AI không phản hồi kịp thời (Request Timeout > 40s)",
            "expected": "Phản hồi trong thời gian chờ quy định",
            "matched_kws": []
        }

    # 2. Check AC flow rules
    for ac_key, ac_rule in AC_RULES.items():
        if ac_tag.startswith(ac_key) or f"[{ac_key}" in ac_tag:
            # Check specific context misalignments
            if ac_key == "AC1.1" and ("samsung" in resp_lower or "iphone 6" in resp_lower):
                return {
                    "is_error": True,
                    "status": "failed",
                    "reason": "Lệch ngữ cảnh nghiêm trọng: Khách hỏi số dư data còn lại, AI lại trả lời về tương thích máy Samsung S24 & iPhone 6",
                    "expected": ac_rule["behavior"],
                    "matched_kws": []
                }
            if ac_key == "AC1.2" and ("active plans" in resp_lower or "đang được kích hoạt" in resp_lower):
                return {
                    "is_error": True,
                    "status": "failed",
                    "reason": "Lệch ngữ cảnh: Khách hỏi lịch sử mua hàng, AI lại trả lời danh sách gói đang kích hoạt",
                    "expected": ac_rule["behavior"],
                    "matched_kws": []
                }
            if ac_key == "AC1.3" and ("most recent purchases" in resp_lower or "5 active plans" in resp_lower):
                return {
                    "is_error": True,
                    "status": "failed",
                    "reason": "Lệch ngữ cảnh: Khách hỏi trạng thái Referral & mã giới thiệu, AI lại trả lời lịch sử mua hàng / gói kích hoạt",
                    "expected": ac_rule["behavior"],
                    "matched_kws": []
                }
            if ac_key == "AC1.6" and "cashback balance is" in resp_lower:
                return {
                    "is_error": True,
                    "status": "failed",
                    "reason": "Lệch ngữ cảnh: Khách hỏi mã khuyến mại (promo code), AI lại trả lời về số dư hoàn tiền cashback",
                    "expected": ac_rule["behavior"],
                    "matched_kws": []
                }
            if ac_key == "AC2" and ("no active promotional campaigns" in resp_lower or "promo code was redeemed" in resp_lower):
                return {
                    "is_error": True,
                    "status": "failed",
                    "reason": "Lệch ngữ cảnh: Khách yêu cầu gợi ý danh sách gói đi Nhật, AI lại trả lời về chương trình khuyến mãi",
                    "expected": ac_rule["behavior"],
                    "matched_kws": []
                }
            if ac_key == "AC3.1" and ("japan options to choose from" in resp_lower or "verified japan options" in resp_lower):
                return {
                    "is_error": True,
                    "status": "failed",
                    "reason": "Lệch ngữ cảnh: Khách hỏi cách cài đặt eSIM trên Android, AI lại trả lời danh sách gói cước Nhật Bản",
                    "expected": ac_rule["behavior"],
                    "matched_kws": []
                }

            matched = [k for k in ac_rule["keywords"] if k in resp_lower]
            if not matched:
                return {
                    "is_error": True,
                    "status": "failed",
                    "reason": f"Phản hồi không chứa các từ khóa nghiệp vụ kỳ vọng: {ac_rule['keywords'][:5]}",
                    "expected": ac_rule["behavior"],
                    "matched_kws": []
                }
            return {
                "is_error": False,
                "status": "passed",
                "reason": "",
                "expected": ac_rule["behavior"],
                "matched_kws": matched
            }

    # 3. Check scenario catalog
    s_id = ac_tag.split(" - ")[0].strip()
    scenario = SCENARIOS_MAP.get(s_id)
    if scenario:
        # Check specific known misalignment in scenario runs
        if s_id == "SALES_01" and ("don’t make any more purchases" in resp_lower or "don't make any more" in resp_lower):
            return {
                "is_error": True,
                "status": "failed",
                "reason": "Lệch ngữ cảnh: Khách hỏi tư vấn gói du lịch dùng Maps & WhatsApp, AI lại cảnh báo ngừng mua hoặc chuyển data",
                "expected": scenario["expected_behavior"],
                "matched_kws": []
            }
        if s_id == "COMPAT_01" and "for france, italy, germany" in resp_lower:
            return {
                "is_error": True,
                "status": "failed",
                "reason": "Lệch ngữ cảnh: Khách hỏi kiểm tra tương thích máy trước khi mua, AI lại tư vấn gói Châu Âu 4 nước",
                "expected": scenario["expected_behavior"],
                "matched_kws": []
            }
        if s_id == "USAGE_05" and "a country plan generally can’t be changed" in resp_lower:
            return {
                "is_error": True,
                "status": "failed",
                "reason": "Lệch ngữ cảnh: Khách hỏi gói Unlimited có bị bóp băng thông không, AI lại trả lời về đổi gói quốc gia",
                "expected": scenario["expected_behavior"],
                "matched_kws": []
            }
        if s_id == "CASHBACK_01" and "an unlimited plan includes 3gb" in resp_lower:
            return {
                "is_error": True,
                "status": "failed",
                "reason": "Lệch ngữ cảnh: Khách hỏi cách tính cashback qua đối tác, AI lại trả lời về gói Unlimited 3GB/ngày",
                "expected": scenario["expected_behavior"],
                "matched_kws": []
            }
        if s_id == "COMPLAINT_01" and "your cashback balance is" in resp_lower:
            return {
                "is_error": True,
                "status": "failed",
                "reason": "Lệch ngữ cảnh: Khách đòi hoàn tiền gói data đã dùng, AI lại thông báo số dư cashback $868.20",
                "expected": scenario["expected_behavior"],
                "matched_kws": []
            }

        expected_kws = [k.lower() for k in scenario.get("expected_keywords", [])]
        matched = [k for k in expected_kws if k in resp_lower]
        if not matched:
            return {
                "is_error": True,
                "status": "failed",
                "reason": f"Thiếu từ khóa kỳ vọng nghiệp vụ: {expected_kws[:6]}",
                "expected": scenario.get("expected_behavior", ""),
                "matched_kws": []
            }

        neg_kws = [k.lower() for k in scenario.get("negative_keywords", [])]
        found_neg = [k for k in neg_kws if k in resp_lower]
        if found_neg:
            return {
                "is_error": True,
                "status": "failed",
                "reason": f"Chứa từ khóa tiêu cực/cấm: {found_neg}",
                "expected": scenario.get("expected_behavior", ""),
                "matched_kws": matched
            }

        return {
            "is_error": False,
            "status": "passed",
            "reason": "",
            "expected": scenario.get("expected_behavior", ""),
            "matched_kws": matched
        }

    return {
        "is_error": False,
        "status": "passed",
        "reason": "",
        "expected": "",
        "matched_kws": []
    }


def format_markdown_text(text: str) -> str:
    """Converts basic markdown formatting into safe HTML."""
    if not text:
        return ""

    escaped = html.escape(text.strip())

    # Code blocks
    escaped = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', escaped, flags=re.DOTALL)
    escaped = re.sub(r'`(.*?)`', r'<code>\1</code>', escaped)

    # Headers
    escaped = re.sub(r'^### (.*?)$', r'<h4 class="msg-h4">\1</h4>', escaped, flags=re.MULTILINE)
    escaped = re.sub(r'^## (.*?)$', r'<h3 class="msg-h3">\1</h3>', escaped, flags=re.MULTILINE)
    escaped = re.sub(r'^# (.*?)$', r'<h2 class="msg-h2">\1</h2>', escaped, flags=re.MULTILINE)

    # Bold and Italic
    escaped = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped)
    escaped = re.sub(r'\*(.*?)\*', r'<em>\1</em>', escaped)

    # Bullet and Numbered lists
    lines = escaped.splitlines()
    in_list = False
    in_num_list = False
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("• "):
            if not in_list:
                new_lines.append('<ul class="msg-list">')
                in_list = True
            item_text = stripped[2:]
            new_lines.append(f'<li>{item_text}</li>')
        elif re.match(r'^\d+\.\s+', stripped):
            if not in_num_list:
                new_lines.append('<ol class="msg-num-list">')
                in_num_list = True
            item_text = re.sub(r'^\d+\.\s+', '', stripped)
            new_lines.append(f'<li>{item_text}</li>')
        else:
            if in_list:
                new_lines.append('</ul>')
                in_list = False
            if in_num_list:
                new_lines.append('</ol>')
                in_num_list = False
            if line:
                new_lines.append(f'<p>{line}</p>')
            else:
                new_lines.append('<div class="spacer"></div>')

    if in_list:
        new_lines.append('</ul>')
    if in_num_list:
        new_lines.append('</ol>')

    return "\n".join(new_lines)


def get_category_label(entries: List[Dict[str, Any]]) -> str:
    """Detects primary business category from entry AC tags for clean tab labels."""
    tags = " ".join([e.get("ac_tag", "") for e in entries]).lower()
    if any(k in tags for k in ["ac1", "ac2", "ac3", "ac4"]):
        return "💬 Quy trình AC (AC1-AC4)"
    elif "sales" in tags:
        return "🛒 Sales & Plan Recommendation"
    elif "compat" in tags:
        return "📱 Compatibility & Install"
    elif "conn" in tags:
        return "📶 Connection Troubleshooting"
    elif "usage" in tags:
        return "📊 Usage Balance & Data"
    elif "cashback" in tags:
        return "💰 Cashback & Bookings"
    elif "complaint" in tags:
        return "⚠️ Complaints & Difficult Cases"
    return "🚀 Phiên kiểm thử"


def parse_markdown_transcript(md_path: str = DEFAULT_MD_PATH) -> List[Dict[str, Any]]:
    """
    Parses ai_chat_transcript.md into structured sessions and entries with automatic defect evaluation.
    """
    if not os.path.exists(md_path):
        return []

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    parts = re.split(r'(?:={50,}\s*\n)?## 🚀 PHIÊN KIỂM THỬ:\s*(.*?)\n(?:={50,}\s*\n)?', content)
    raw_sessions = []

    if parts and parts[0].strip():
        start_match = re.search(r'\*Thời gian bắt đầu:\s*(.*?)\*', parts[0])
        initial_name = start_match.group(1).strip() if start_match else "2026-09-22 13:37:53"
        raw_sessions.append((initial_name, parts[0]))

    for i in range(1, len(parts), 2):
        session_time = parts[i].strip()
        session_body = parts[i + 1] if i + 1 < len(parts) else ""
        raw_sessions.append((session_time, session_body))

    sessions = []
    global_turn_idx = 1

    for s_time, raw_s in raw_sessions:
        if not raw_s.strip():
            continue

        blocks = re.findall(r'### 🎯 \[(.*?)\] — \*(.*?)\*\s*\n\n(.*?)(?=\n---\n|### 🎯|\Z)', raw_s, re.DOTALL)
        entries = []

        for b_idx, (ac_tag, timestamp, body) in enumerate(blocks, start=1):
            # 1. User Question
            q_match = re.search(r'- 👤 \*\*User Question:\*\*\s*\n\s*>\s*\*\*\"?(.*?)\"?\*\*', body)
            query = q_match.group(1).strip() if q_match else ""

            # 2. AI Response
            r_match = re.search(r'- 🤖 \*\*AI Response \(Eski\):\*\*\s*\n(.*?)(?=- 📦|- 💡|\Z)', body, re.DOTALL)
            raw_response = r_match.group(1) if r_match else ""
            cleaned_response = "\n".join([re.sub(r'^\s*>\s?', '', l) for l in raw_response.strip().splitlines()])

            # 3. Plan Carousel
            plans = []
            if "- 📦 **Plan Carousel" in body:
                plan_matches = re.findall(r'- \*\*Gói #\d+:\*\*\s*`([^`]+)`(?:\s*~~([^~]+)~~)?', body)
                for price, old_price in plan_matches:
                    plans.append({
                        "price": price.strip(),
                        "old_price": old_price.strip() if old_price else ""
                    })

            # 4. Chips
            chips = []
            chips_match = re.search(r'- 💡 \*\*Follow-up Suggestion Chips:\*\*\s*(.*)', body)
            if chips_match:
                raw_chips = chips_match.group(1)
                chips = [c.strip().strip('`') for c in raw_chips.split(',') if c.strip()]

            # 5. Defect Evaluation
            eval_res = evaluate_response(ac_tag, query, cleaned_response)

            entry_id = f"turn-{global_turn_idx}"
            global_turn_idx += 1

            entries.append({
                "entry_id": entry_id,
                "index": b_idx,
                "ac_tag": ac_tag.strip(),
                "time": timestamp.strip(),
                "query": query,
                "response": cleaned_response,
                "plans": plans,
                "chips": chips,
                "is_error": eval_res["is_error"],
                "status": eval_res["status"],
                "reason": eval_res["reason"],
                "expected": eval_res["expected"],
                "matched_kws": eval_res["matched_kws"]
            })

        if entries:
            category_label = get_category_label(entries)
            short_time = s_time.split(" ")[-1] if " " in s_time else s_time
            display_title = f"{category_label} · {short_time}"
            sessions.append({
                "session_name": display_title,
                "session_full_time": s_time,
                "category_label": category_label,
                "entries": entries
            })

    return sessions


def build_html_report_content(sessions: List[Dict[str, Any]], title: str = "Eskimo Sale AI Agent — In-App Chat Report") -> str:
    """Builds the complete single-page interactive HTML report with red error highlighting."""
    all_entries = [e for s in sessions for e in s["entries"]]
    total_turns = len(all_entries)
    total_errors = sum(1 for e in all_entries if e["is_error"])
    total_passed = total_turns - total_errors
    total_plans = sum(len(e.get("plans", [])) for e in all_entries)
    total_chips = sum(len(e.get("chips", [])) for e in all_entries)
    pass_rate = round((total_passed / total_turns * 100), 1) if total_turns > 0 else 0

    # 1. AC Flow Critical 6 Errors
    ac_critical_errors = []
    seen_ac_tags = set()
    for e in all_entries:
        if e["is_error"] and any(e["ac_tag"].startswith(k) for k in ["AC1", "AC2", "AC3", "AC4"]):
            tag_base = e["ac_tag"].split(" - ")[0]
            if tag_base not in seen_ac_tags:
                ac_critical_errors.append(e)
                seen_ac_tags.add(tag_base)
            if len(ac_critical_errors) == 6:
                break

    # 2. Domain Scenario Critical 6 Errors (from Sales, Compat, Usage, Cashback, Complaints)
    scenario_critical_errors = []
    seen_scen_ids = set()
    priority_ids = ["SALES_01", "COMPAT_01", "USAGE_05", "CASHBACK_01", "CASHBACK_08", "COMPLAINT_01"]
    
    # First search for priority IDs
    for p_id in priority_ids:
        for e in all_entries:
            if e["is_error"] and e["ac_tag"].startswith(p_id):
                if p_id not in seen_scen_ids:
                    scenario_critical_errors.append(e)
                    seen_scen_ids.add(p_id)
                break
                
    # Pad to 6 if needed
    if len(scenario_critical_errors) < 6:
        for e in all_entries:
            if e["is_error"] and not any(e["ac_tag"].startswith(k) for k in ["AC1", "AC2", "AC3", "AC4"]):
                tag_base = e["ac_tag"].split(" - ")[0]
                if tag_base not in seen_scen_ids:
                    scenario_critical_errors.append(e)
                    seen_scen_ids.add(tag_base)
                if len(scenario_critical_errors) == 6:
                    break

    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _render_err_rows(err_list):
        rows = []
        for idx, err in enumerate(err_list, start=1):
            err_id = err["entry_id"]
            tag = html.escape(err["ac_tag"])
            q_text = html.escape(err["query"])
            resp_snippet = html.escape(err["response"][:140] + ("..." if len(err["response"]) > 140 else ""))
            reason_text = html.escape(err["reason"])
            rows.append(f"""
            <tr class="err-row" onclick="jumpToTurn('{err_id}')" title="Click để cuộn ngay đến câu hỏi này">
                <td class="err-idx">#{idx}</td>
                <td class="err-tag"><span class="badge-ac-red">{tag}</span></td>
                <td class="err-q"><strong>{q_text}</strong></td>
                <td class="err-r">{resp_snippet}</td>
                <td class="err-reason"><span class="defect-highlight">🚨 {reason_text}</span></td>
                <td class="err-action"><button class="btn-jump">🔍 Xem chi tiết</button></td>
            </tr>
            """)
        return "".join(rows)

    ac_table_rows = _render_err_rows(ac_critical_errors)
    scenario_table_rows = _render_err_rows(scenario_critical_errors)

    # Render Sessions HTML & Tabs
    sessions_html = []
    nav_tabs_html = []

    # First Tab: Consolidated View (All Q&A in one place)
    nav_tabs_html.append(f"""
    <button class="session-tab active" onclick="switchSession('session-all', this)">
        <span class="dot dot-all"></span>
        <span class="tab-title">🌐 Tất cả phiên ({total_turns} Q&A)</span>
        <span class="tab-badge-error">{total_errors} Lỗi</span>
    </button>
    """)

    # Consolidated View Panel
    all_turns_html = []
    for e in all_entries:
        all_turns_html.append(_render_turn_card(e))

    sessions_html.append(f"""
    <div id="session-all" class="session-panel active">
        <div class="session-panel-header">
            <div>
                <h3>Toàn bộ lịch sử đối thoại: <strong>Tất cả các phiên kiểm thử ({total_turns} câu hỏi)</strong></h3>
                <p class="panel-sub">Tô đỏ nổi bật toàn bộ các câu AI trả lời sai, lệch ngữ cảnh hoặc timeout.</p>
            </div>
            <div class="panel-meta-badges">
                <span class="badge-pill pill-red">🔴 {total_errors} Lỗi phát hiện</span>
                <span class="badge-pill pill-green">🟢 {total_passed} Đạt yêu cầu</span>
            </div>
        </div>
        <div class="turns-list">
            {''.join(all_turns_html)}
        </div>
    </div>
    """)

    # Individual Session Tabs & Panels
    for s_idx, s in enumerate(sessions):
        s_id = f"session-{s_idx}"
        s_errors = sum(1 for e in s["entries"] if e["is_error"])
        err_badge = f'<span class="tab-badge-error">{s_errors} Lỗi</span>' if s_errors > 0 else '<span class="tab-badge">0 Lỗi</span>'

        nav_tabs_html.append(f"""
        <button class="session-tab" onclick="switchSession('{s_id}', this)">
            <span class="dot {'dot-err' if s_errors > 0 else 'dot-pass'}"></span>
            <span class="tab-title">{html.escape(s['session_name'])}</span>
            {err_badge}
        </button>
        """)

        entries_html = [_render_turn_card(e) for e in s["entries"]]

        sessions_html.append(f"""
        <div id="{s_id}" class="session-panel">
            <div class="session-panel-header">
                <div>
                    <h3>Phiên kiểm thử: <strong>{html.escape(s['session_name'])}</strong></h3>
                    <p class="panel-sub">Thời gian bắt đầu: {html.escape(s['session_full_time'])}</p>
                </div>
                <div class="panel-meta-badges">
                    <span class="badge-pill pill-red">🔴 {s_errors} Lỗi</span>
                    <span class="badge-pill pill-green">🟢 {len(s['entries']) - s_errors} Đạt</span>
                    <span class="badge-pill pill-neutral">{len(s['entries'])} Tổng số</span>
                </div>
            </div>
            <div class="turns-list">
                {''.join(entries_html)}
            </div>
        </div>
        """)

    # Full HTML Template
    return f"""<!DOCTYPE html>
<html lang="vi" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #0b0f19;
            --bg-surface: #111827;
            --bg-card: #1f2937;
            --bg-card-hover: #283548;
            --border-color: rgba(255, 255, 255, 0.08);
            --border-focus: #3b82f6;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --text-sub: #6b7280;
            --primary: #3b82f6;
            --primary-gradient: linear-gradient(135deg, #2563eb, #1d4ed8);
            --user-bubble-bg: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --bot-bubble-bg: #1e293b;
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --accent-purple: #8b5cf6;
            
            /* Error Palette */
            --danger-red: #ef4444;
            --danger-dark: #dc2626;
            --danger-bg: rgba(239, 68, 68, 0.12);
            --danger-border: #ef4444;
            --danger-glow: 0 0 25px rgba(239, 68, 68, 0.28);
            
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -4px rgba(0, 0, 0, 0.5);
        }}

        [data-theme="light"] {{
            --bg-base: #f8fafc;
            --bg-surface: #ffffff;
            --bg-card: #f1f5f9;
            --bg-card-hover: #e2e8f0;
            --border-color: #cbd5e1;
            --border-focus: #2563eb;
            --text-main: #0f172a;
            --text-muted: #475569;
            --text-sub: #64748b;
            --user-bubble-bg: linear-gradient(135deg, #2563eb, #3b82f6);
            --bot-bubble-bg: #ffffff;
            --danger-bg: #fef2f2;
            --danger-border: #ef4444;
            --danger-glow: 0 0 20px rgba(239, 68, 68, 0.18);
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            line-height: 1.6;
            padding: 24px 16px;
            transition: background-color 0.3s ease, color 0.3s ease;
        }}

        .container {{
            max-width: 1180px;
            margin: 0 auto;
        }}

        /* Header & Dashboard Stats */
        .report-header {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            padding: 28px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-md);
        }}

        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
        }}

        .brand-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(59, 130, 246, 0.12);
            color: var(--primary);
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 8px;
        }}

        .report-title {{
            font-size: 1.95rem;
            font-weight: 800;
            color: var(--text-main);
            letter-spacing: -0.02em;
        }}

        .report-subtitle {{
            font-size: 0.98rem;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 18px;
            border-radius: 10px;
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            color: var(--text-main);
            transition: all 0.2s ease;
        }}

        .btn:hover {{
            background: var(--bg-card-hover);
            border-color: var(--primary);
        }}

        .btn-primary {{
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }}

        .btn-primary:hover {{
            background: #2563eb;
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            border-top: 1px solid var(--border-color);
            padding-top: 24px;
        }}

        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px;
            display: flex;
            align-items: center;
            gap: 16px;
            position: relative;
            overflow: hidden;
        }}

        .stat-card.card-danger {{
            border-color: var(--danger-border);
            background: var(--danger-bg);
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.15);
        }}

        .stat-icon {{
            font-size: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            width: 52px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .stat-val {{
            font-size: 1.65rem;
            font-weight: 800;
            color: var(--text-main);
        }}

        .stat-val.text-red {{
            color: var(--danger-red);
        }}

        .stat-val.text-green {{
            color: var(--accent-green);
        }}

        .stat-lbl {{
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}

        /* Critical Errors Banner */
        .critical-errors-section {{
            background: var(--bg-surface);
            border: 2px solid var(--danger-border);
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 28px;
            box-shadow: var(--danger-glow);
            position: relative;
        }}

        .critical-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .critical-title {{
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--danger-red);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .critical-sub {{
            font-size: 0.88rem;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        .err-tab-buttons {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .btn-err-tab {{
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #fca5a5;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.84rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .btn-err-tab:hover {{
            background: rgba(239, 68, 68, 0.25);
            color: #ffffff;
        }}

        .btn-err-tab.active {{
            background: var(--danger-red);
            border-color: var(--danger-red);
            color: #ffffff;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.35);
        }}

        .err-tab-panel {{
            display: none;
        }}

        .err-tab-panel.active {{
            display: block;
        }}

        .table-responsive {{
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }}

        .error-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
            background: var(--bg-card);
            text-align: left;
        }}

        .error-table th {{
            background: rgba(0, 0, 0, 0.25);
            padding: 12px 16px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.76rem;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--border-color);
        }}

        .error-table td {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
        }}

        .err-row {{
            cursor: pointer;
            transition: background 0.2s;
        }}

        .err-row:hover {{
            background: rgba(239, 68, 68, 0.12);
        }}

        .err-idx {{
            font-weight: 800;
            color: var(--danger-red);
            font-size: 0.95rem;
        }}

        .badge-ac-red {{
            background: rgba(239, 68, 68, 0.18);
            color: var(--danger-red);
            border: 1px solid rgba(239, 68, 68, 0.4);
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.78rem;
            white-space: nowrap;
        }}

        .defect-highlight {{
            color: #f87171;
            font-weight: 600;
            display: inline-block;
            line-height: 1.4;
        }}

        .btn-jump {{
            background: var(--danger-red);
            color: #ffffff;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap;
        }}

        .btn-jump:hover {{
            background: var(--danger-dark);
        }}

        /* Toolbar & Filters */
        .toolbar {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .search-box {{
            flex: 1;
            min-width: 280px;
            position: relative;
        }}

        .search-box input {{
            width: 100%;
            padding: 10px 14px 10px 40px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-main);
            font-size: 0.92rem;
            outline: none;
            transition: border-color 0.2s ease;
        }}

        .search-box input:focus {{
            border-color: var(--border-focus);
        }}

        .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-sub);
            font-size: 1.1rem;
        }}

        .filter-group {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .btn-filter {{
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.84rem;
            font-weight: 600;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s;
        }}

        .btn-filter:hover {{
            background: var(--bg-card-hover);
            color: var(--text-main);
        }}

        .btn-filter.active {{
            background: var(--primary);
            border-color: var(--primary);
            color: #ffffff;
        }}

        .btn-filter.filter-danger.active {{
            background: var(--danger-red);
            border-color: var(--danger-red);
            color: #ffffff;
        }}

        .btn-filter.filter-success.active {{
            background: var(--accent-green);
            border-color: var(--accent-green);
            color: #ffffff;
        }}

        /* Session Tabs */
        .session-tabs {{
            display: flex;
            gap: 10px;
            overflow-x: auto;
            margin-bottom: 22px;
            padding-bottom: 6px;
        }}

        .session-tab {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 11px 18px;
            border-radius: 12px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}

        .session-tab:hover {{
            background: var(--bg-card);
            color: var(--text-main);
        }}

        .session-tab.active {{
            background: var(--primary);
            border-color: var(--primary);
            color: #ffffff;
        }}

        .session-tab .dot {{
            width: 9px;
            height: 9px;
            border-radius: 50%;
        }}

        .dot-all {{ background: #38bdf8; }}
        .dot-pass {{ background: var(--accent-green); }}
        .dot-err {{ background: var(--danger-red); }}

        .tab-badge {{
            background: rgba(0, 0, 0, 0.25);
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            color: var(--text-muted);
        }}

        .tab-badge-error {{
            background: var(--danger-dark);
            color: #ffffff;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
        }}

        .session-panel {{
            display: none;
        }}

        .session-panel.active {{
            display: block;
        }}

        .session-panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .panel-sub {{
            font-size: 0.88rem;
            color: var(--text-muted);
            margin-top: 3px;
        }}

        .panel-meta-badges {{
            display: flex;
            gap: 8px;
        }}

        .badge-pill {{
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            border: 1px solid var(--border-color);
        }}

        .pill-red {{
            background: var(--danger-bg);
            color: var(--danger-red);
            border-color: rgba(239, 68, 68, 0.4);
        }}

        .pill-green {{
            background: rgba(16, 185, 129, 0.12);
            color: var(--accent-green);
            border-color: rgba(16, 185, 129, 0.4);
        }}

        .pill-neutral {{
            background: var(--bg-card);
            color: var(--text-muted);
        }}

        /* Chat Turn Card */
        .chat-turn {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            margin-bottom: 24px;
            overflow: hidden;
            box-shadow: var(--shadow-sm);
            transition: all 0.25s ease;
            position: relative;
        }}

        .chat-turn:hover {{
            border-color: rgba(59, 130, 246, 0.4);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}

        /* RED HIGHLIGHT STYLING FOR ERRORS */
        .chat-turn.is-error {{
            border: 2px solid var(--danger-border) !important;
            background: linear-gradient(180deg, var(--danger-bg) 0%, var(--bg-surface) 100%) !important;
            box-shadow: var(--danger-glow) !important;
        }}

        .turn-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-card);
            padding: 14px 22px;
            border-bottom: 1px solid var(--border-color);
            flex-wrap: wrap;
            gap: 12px;
        }}

        .chat-turn.is-error .turn-header {{
            background: rgba(239, 68, 68, 0.14);
            border-bottom: 1px solid rgba(239, 68, 68, 0.3);
        }}

        .turn-meta {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .turn-num {{
            background: var(--primary);
            color: #ffffff;
            font-weight: 800;
            font-size: 0.78rem;
            padding: 3px 9px;
            border-radius: 6px;
        }}

        .chat-turn.is-error .turn-num {{
            background: var(--danger-dark);
        }}

        .ac-tag {{
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--text-main);
        }}

        .status-badge {{
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .status-passed {{
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }}

        .status-failed {{
            background: var(--danger-red);
            color: #ffffff;
            border: 1px solid var(--danger-dark);
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
        }}

        .turn-actions {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .timestamp {{
            font-size: 0.82rem;
            color: var(--text-sub);
        }}

        .copy-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .copy-btn:hover {{
            background: var(--bg-card-hover);
            color: var(--text-main);
        }}

        .exchange-body {{
            padding: 24px 22px;
            display: flex;
            flex-direction: column;
            gap: 22px;
        }}

        /* Messages */
        .msg-row {{
            display: flex;
            gap: 14px;
            max-width: 92%;
        }}

        .user-row {{
            align-self: flex-end;
            flex-direction: row-reverse;
        }}

        .bot-row {{
            align-self: flex-start;
        }}

        .avatar {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
            flex-shrink: 0;
            box-shadow: var(--shadow-sm);
        }}

        .user-avatar {{
            background: var(--primary);
        }}

        .bot-avatar {{
            background: #475569;
        }}

        .chat-turn.is-error .bot-avatar {{
            background: var(--danger-dark);
        }}

        .bubble {{
            border-radius: 18px;
            padding: 16px 20px;
            font-size: 0.94rem;
            position: relative;
            box-shadow: var(--shadow-sm);
            max-width: 100%;
        }}

        .user-bubble {{
            background: var(--user-bubble-bg);
            color: #ffffff;
            border-top-right-radius: 4px;
        }}

        .bot-bubble {{
            background: var(--bot-bubble-bg);
            color: var(--text-main);
            border: 1px solid var(--border-color);
            border-top-left-radius: 4px;
        }}

        .bubble-sender {{
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 8px;
            opacity: 0.85;
        }}

        .bubble-text p {{
            margin-bottom: 8px;
        }}

        .bubble-text p:last-child {{
            margin-bottom: 0;
        }}

        .msg-list, .msg-num-list {{
            margin-left: 22px;
            margin-top: 8px;
            margin-bottom: 8px;
        }}

        .msg-list li, .msg-num-list li {{
            margin-bottom: 5px;
        }}

        .msg-h2 {{ font-size: 1.2rem; color: #60a5fa; margin-top: 14px; margin-bottom: 6px; font-weight: 700; }}
        .msg-h3 {{ font-size: 1.08rem; color: #93c5fd; margin-top: 12px; margin-bottom: 6px; font-weight: 700; }}
        .msg-h4 {{ font-size: 0.98rem; margin-top: 10px; margin-bottom: 4px; font-weight: 600; }}

        code {{
            background: rgba(0, 0, 0, 0.28);
            padding: 2px 7px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.88em;
        }}

        /* Error Diagnosis Box */
        .error-diagnosis-box {{
            background: rgba(239, 68, 68, 0.12);
            border: 1px solid var(--danger-border);
            border-radius: 12px;
            padding: 16px;
            margin-top: 18px;
            border-left: 6px solid var(--danger-red);
        }}

        .error-diag-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
        }}

        .error-diag-header .error-title {{
            font-weight: 800;
            color: var(--danger-red);
            font-size: 0.86rem;
            letter-spacing: 0.04em;
        }}

        .error-diag-body {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 0.88rem;
        }}

        .diag-row {{
            display: flex;
            gap: 8px;
            align-items: baseline;
        }}

        .diag-label {{
            font-weight: 700;
            color: var(--text-muted);
            min-width: 140px;
            flex-shrink: 0;
            font-size: 0.82rem;
            text-transform: uppercase;
        }}

        .diag-val {{
            color: var(--text-main);
            flex: 1;
        }}

        .diag-val.text-red {{
            color: #f87171;
            font-weight: 600;
        }}

        /* Plan Carousel Cards */
        .carousel-section {{
            margin-top: 18px;
            padding-top: 16px;
            border-top: 1px solid var(--border-color);
        }}

        .section-label {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .carousel-cards {{
            display: flex;
            gap: 12px;
            overflow-x: auto;
            padding-bottom: 8px;
        }}

        .plan-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 14px 18px;
            min-width: 150px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            box-shadow: var(--shadow-sm);
        }}

        .plan-badge {{
            font-size: 0.74rem;
            color: var(--text-muted);
            font-weight: 700;
            text-transform: uppercase;
        }}

        .plan-price-wrap {{
            display: flex;
            align-items: baseline;
            gap: 8px;
        }}

        .curr-price {{
            font-size: 1.22rem;
            font-weight: 800;
            color: var(--accent-green);
        }}

        .old-price {{
            font-size: 0.88rem;
            color: var(--text-sub);
            text-decoration: line-through;
        }}

        /* Chips Section */
        .chips-section {{
            margin-top: 16px;
            padding-top: 14px;
            border-top: 1px solid var(--border-color);
        }}

        .chips-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .chip-item {{
            background: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(59, 130, 246, 0.25);
            color: #93c5fd;
            padding: 5px 13px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            transition: all 0.2s;
            cursor: default;
        }}

        .chip-item:hover {{
            background: rgba(59, 130, 246, 0.24);
            border-color: #60a5fa;
            color: #ffffff;
        }}

        /* Flash highlight animation when jumping */
        @keyframes flashRed {{
            0% {{ outline: 4px solid var(--danger-red); transform: scale(1.02); }}
            100% {{ outline: 0px solid transparent; transform: scale(1); }}
        }}

        .flash-highlight {{
            animation: flashRed 1.8s ease-out;
        }}

        /* Toast notification */
        .toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #10b981;
            color: #ffffff;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 0.88rem;
            font-weight: 600;
            box-shadow: var(--shadow-lg);
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease;
            pointer-events: none;
            z-index: 1000;
        }}

        .toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}

        @media (max-width: 820px) {{
            .msg-row {{ max-width: 100%; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .header-top {{ flex-direction: column; }}
            .diag-row {{ flex-direction: column; gap: 2px; }}
            .diag-label {{ min-width: auto; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Main Report Header -->
        <header class="report-header">
            <div class="header-top">
                <div>
                    <div class="brand-badge">❄️ Eskimo Mobile eSIM Automation Test Suite</div>
                    <h1 class="report-title">{html.escape(title)}</h1>
                    <p class="report-subtitle">Báo cáo đánh giá chất lượng phản hồi của trợ lý ảo Eski trên kênh In-App Chat</p>
                </div>
                <div class="header-actions">
                    <button class="btn" onclick="toggleTheme()" title="Đổi giao diện sáng/tối">🌓 Đổi theme</button>
                    <button class="btn btn-primary" onclick="window.print()">🖨️ In / Lưu PDF</button>
                </div>
            </div>

            <!-- Stats Grid -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">💬</div>
                    <div>
                        <div class="stat-val">{total_turns}</div>
                        <div class="stat-lbl">Tổng lượt trao đổi Q&A</div>
                    </div>
                </div>
                <div class="stat-card card-danger">
                    <div class="stat-icon">🚨</div>
                    <div>
                        <div class="stat-val text-red">{total_errors}</div>
                        <div class="stat-lbl">Phát hiện lỗi / Defect</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div>
                        <div class="stat-val text-green">{total_passed} ({pass_rate}%)</div>
                        <div class="stat-lbl">Phản hồi đạt yêu cầu</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📦</div>
                    <div>
                        <div class="stat-val">{total_plans} / {total_chips}</div>
                        <div class="stat-lbl">Gói Carousel / Chips</div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Critical Errors Section (TÔ ĐỎ 6 LỖI NỔI BẬT CỦA AI) -->
        <section class="critical-errors-section">
            <div class="critical-header">
                <div>
                    <div class="critical-title">🚨 BẢNG TỔNG HỢP CÁC LỖI TRỌNG ĐIỂM CỦA AI (DEFECTS SUMMARY)</div>
                    <p class="critical-sub">Bảng tổng hợp chi tiết các câu hỏi bị AI trả lời lệch ngữ cảnh, sai thông tin nghiệp vụ hoặc timeout. Click vào hàng để xem chi tiết.</p>
                </div>
                <div class="err-tab-buttons">
                    <button class="btn-err-tab active" onclick="switchErrorTab('err-tab-ac', this)">🎯 6 Lỗi Luồng AC (AC1 - AC4)</button>
                    <button class="btn-err-tab" onclick="switchErrorTab('err-tab-scen', this)">📋 6 Lỗi Kịch Bản Nghiệp Vụ (Nhóm 1 - 6)</button>
                </div>
            </div>

            <!-- Tab 1: 6 AC Errors -->
            <div id="err-tab-ac" class="err-tab-panel active">
                <div class="table-responsive">
                    <table class="error-table">
                        <thead>
                            <tr>
                                <th>STT</th>
                                <th>Tiêu chí AC</th>
                                <th>Câu hỏi từ người dùng (Query)</th>
                                <th>Trích đoạn phản hồi thực tế của AI</th>
                                <th>Nguyên nhân lỗi</th>
                                <th>Thao tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {ac_table_rows}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Tab 2: 6 Scenario Errors -->
            <div id="err-tab-scen" class="err-tab-panel">
                <div class="table-responsive">
                    <table class="error-table">
                        <thead>
                            <tr>
                                <th>STT</th>
                                <th>Mã Kịch Bản</th>
                                <th>Câu hỏi từ người dùng (Query)</th>
                                <th>Trích đoạn phản hồi thực tế của AI</th>
                                <th>Nguyên nhân lỗi</th>
                                <th>Thao tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {scenario_table_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- Search & Filter Toolbar -->
        <div class="toolbar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" placeholder="Tìm kiếm câu hỏi, câu trả lời, từ khóa, mã lỗi..." oninput="filterTurns()">
            </div>
            <div class="filter-group">
                <button class="btn-filter active" onclick="setQuickFilter('all', this)">Tất cả ({total_turns})</button>
                <button class="btn-filter filter-danger" onclick="setQuickFilter('errors', this)">🔴 Chỉ xem LỖI ({total_errors})</button>
                <button class="btn-filter filter-success" onclick="setQuickFilter('passed', this)">🟢 Chỉ xem ĐẠT ({total_passed})</button>
                <button class="btn-filter" onclick="toggleOnlyCarousel(this)">📦 Có Carousel</button>
            </div>
        </div>

        <!-- Session Tabs -->
        <div class="session-tabs">
            {''.join(nav_tabs_html)}
        </div>

        <!-- Session Panels -->
        <main class="sessions-container">
            {''.join(sessions_html)}
        </main>
    </div>

    <!-- Toast message -->
    <div id="toast" class="toast">Đã sao chép vào bộ nhớ tạm!</div>

    <script>
        let currentFilter = 'all'; // 'all', 'errors', 'passed'
        let onlyCarousel = false;

        function switchErrorTab(tabId, btn) {{
            document.querySelectorAll('.err-tab-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.btn-err-tab').forEach(b => b.classList.remove('active'));
            const target = document.getElementById(tabId);
            if (target) target.classList.add('active');
            if (btn) btn.classList.add('active');
        }}

        function switchSession(sessionId, tabElem) {{
            document.querySelectorAll('.session-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.session-tab').forEach(t => t.classList.remove('active'));
            
            const target = document.getElementById(sessionId);
            if (target) target.classList.add('active');
            if (tabElem) tabElem.classList.add('active');
            
            filterTurns();
        }}

        function toggleTheme() {{
            const html = document.documentElement;
            const current = html.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
        }}

        function setQuickFilter(mode, btn) {{
            currentFilter = mode;
            document.querySelectorAll('.filter-group .btn-filter').forEach(b => {{
                if (b.innerText.includes('Tất cả') || b.innerText.includes('LỖI') || b.innerText.includes('ĐẠT')) {{
                    b.classList.remove('active');
                }}
            }});
            btn.classList.add('active');
            filterTurns();
        }}

        function toggleOnlyCarousel(btn) {{
            onlyCarousel = !onlyCarousel;
            btn.classList.toggle('active', onlyCarousel);
            filterTurns();
        }}

        function filterTurns() {{
            const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
            const activeSession = document.querySelector('.session-panel.active');
            if (!activeSession) return;

            const turns = activeSession.querySelectorAll('.chat-turn');
            turns.forEach(turn => {{
                const text = turn.innerText.toLowerCase();
                const isError = turn.classList.contains('is-error');
                const hasCarousel = turn.querySelector('.carousel-section') !== null;

                let match = true;
                if (query && !text.includes(query)) match = false;
                if (currentFilter === 'errors' && !isError) match = false;
                if (currentFilter === 'passed' && isError) match = false;
                if (onlyCarousel && !hasCarousel) match = false;

                turn.style.display = match ? 'block' : 'none';
            }});
        }}

        function jumpToTurn(turnId) {{
            // Ensure we are viewing either the consolidated tab or find the element
            let target = document.getElementById(turnId);
            if (!target) {{
                // Switch to all sessions tab
                const allTab = document.querySelector('.session-tab');
                if (allTab) switchSession('session-all', allTab);
                target = document.getElementById(turnId);
            }}

            if (target) {{
                target.style.display = 'block';
                target.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                target.classList.add('flash-highlight');
                setTimeout(() => target.classList.remove('flash-highlight'), 2000);
            }}
        }}

        function copyTurn(btn) {{
            const card = btn.closest('.chat-turn');
            const q = card.querySelector('.query-content')?.innerText || '';
            const r = card.querySelector('.response-content')?.innerText || '';
            const ac = card.getAttribute('data-ac') || '';
            const copyText = `[${{ac}}]\nQ: ${{q}}\nA: ${{r}}`;

            navigator.clipboard.writeText(copyText).then(() => {{
                showToast("Đã sao chép nội dung hội thoại!");
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


def _render_turn_card(e: Dict[str, Any]) -> str:
    """Helper to render an individual chat exchange turn card."""
    entry_id = e["entry_id"]
    e_idx = e.get("index", 1)
    ac_tag = html.escape(e.get("ac_tag", ""))
    timestamp = html.escape(e.get("time", ""))
    query = html.escape(e.get("query", ""))
    formatted_resp = format_markdown_text(e.get("response", ""))
    plans = e.get("plans", [])
    chips = e.get("chips", [])
    is_error = e.get("is_error", False)
    reason = html.escape(e.get("reason", ""))
    expected = html.escape(e.get("expected", ""))

    error_class = "is-error" if is_error else "is-passed"
    status_badge = (
        '<span class="status-badge status-failed">❌ LỖI / FAILED</span>'
        if is_error else
        '<span class="status-badge status-passed">✅ ĐẠT / PASSED</span>'
    )

    # Diagnostic Box for errors
    error_diag_html = ""
    if is_error:
        error_diag_html = f"""
        <div class="error-diagnosis-box">
            <div class="error-diag-header">
                <span class="error-title">🚨 CHI TIẾT LỖI PHẢN HỒI (DEFECT ANALYSIS)</span>
            </div>
            <div class="error-diag-body">
                <div class="diag-row">
                    <span class="diag-label">Nguyên nhân lỗi:</span>
                    <span class="diag-val text-red">{reason}</span>
                </div>
                <div class="diag-row">
                    <span class="diag-label">Kỳ vọng hành vi:</span>
                    <span class="diag-val">{expected}</span>
                </div>
            </div>
        </div>
        """

    # Carousel HTML
    plans_html = ""
    if plans:
        plan_cards = []
        for p_i, p in enumerate(plans, 1):
            price = html.escape(p.get("price", ""))
            old_price = html.escape(p.get("old_price", ""))
            old_badge = f'<span class="old-price">{old_price}</span>' if old_price else ""
            plan_cards.append(f"""
            <div class="plan-card">
                <div class="plan-badge">Option #{p_i}</div>
                <div class="plan-price-wrap">
                    <span class="curr-price">{price}</span>
                    {old_badge}
                </div>
            </div>
            """)
        plans_html = f"""
        <div class="carousel-section">
            <div class="section-label"><span class="icon">📦</span> Plan Carousel Recommended ({len(plans)} plans)</div>
            <div class="carousel-cards">{''.join(plan_cards)}</div>
        </div>
        """

    # Chips HTML
    chips_html = ""
    if chips:
        chip_tags = [f'<span class="chip-item">💡 {html.escape(c)}</span>' for c in chips]
        chips_html = f"""
        <div class="chips-section">
            <div class="section-label"><span class="icon">✨</span> Follow-up Suggestion Chips</div>
            <div class="chips-container">{''.join(chip_tags)}</div>
        </div>
        """

    return f"""
    <article id="{entry_id}" class="chat-turn {error_class}" data-ac="{ac_tag}" data-turn="{e_idx}">
        <header class="turn-header">
            <div class="turn-meta">
                <span class="turn-num">#{e_idx}</span>
                <span class="ac-tag">{ac_tag}</span>
                {status_badge}
            </div>
            <div class="turn-actions">
                <span class="timestamp">🕒 {timestamp}</span>
                <button class="copy-btn" onclick="copyTurn(this)" title="Copy Q&A">📋 Copy</button>
            </div>
        </header>

        <div class="exchange-body">
            <!-- User Message -->
            <div class="msg-row user-row">
                <div class="avatar user-avatar">👤</div>
                <div class="bubble user-bubble">
                    <div class="bubble-sender">User Question</div>
                    <div class="bubble-text query-content">{query}</div>
                </div>
            </div>

            <!-- Bot Message -->
            <div class="msg-row bot-row">
                <div class="avatar bot-avatar">🤖</div>
                <div class="bubble bot-bubble">
                    <div class="bubble-sender">Eski (Sale AI Agent)</div>
                    <div class="bubble-text response-content">{formatted_resp}</div>
                    {plans_html}
                    {chips_html}
                    {error_diag_html}
                </div>
            </div>
        </div>
    </article>
    """


def export_html_report(
    md_path: str = DEFAULT_MD_PATH,
    output_html_path: str = DEFAULT_HTML_PATH,
    title: str = "Eskimo Sale AI Agent — In-App Chat Report"
) -> str:
    """
    Parses the Markdown transcript file and exports the polished HTML report.
    Returns the absolute path to the generated HTML report file.
    """
    sessions = parse_markdown_transcript(md_path)
    html_content = build_html_report_content(sessions, title=title)

    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return os.path.abspath(output_html_path)


if __name__ == "__main__":
    report_file = export_html_report()
    print(f"HTML report successfully exported to: {report_file}")
