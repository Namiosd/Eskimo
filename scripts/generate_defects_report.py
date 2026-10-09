"""
Specialized HTML Defect & Failure Bug Report Generator for Devs.
Extracts ONLY failed/defective test turns from ai_chat_transcript.md and generates
a focused, developer-ready bug report with:
- Executive Defect Metrics & Root Cause breakdown
- Interactive Bug Matrix Table with severity badges
- Detailed Bug Cards with User Prompt, Actual AI Response, Expected Behavior,
  Defect Analysis, and Steps to Reproduce
- 1-Click "Copy Bug Jira/Markdown" for easy defect ticketing
- Filtering by Domain Category & Defect Type, live search
- Ultra-premium dark/light UI, print to PDF support
"""

import os
import re
import html
from datetime import datetime
from typing import List, Dict, Any

import sys
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

try:
    from scripts.html_report_generator import (
        parse_markdown_transcript,
        format_markdown_text,
        DEFAULT_MD_PATH
    )
except ImportError:
    from html_report_generator import (
        parse_markdown_transcript,
        format_markdown_text,
        DEFAULT_MD_PATH
    )

OUTPUT_DEFECTS_HTML = os.path.join(_ROOT_DIR, "reports", "html", "ai_chat_defects_report.html")


def classify_defect_type(reason: str) -> Dict[str, str]:
    """Classifies a defect into developer-friendly categories and severities."""
    r_lower = reason.lower()
    if "lệch ngữ cảnh" in r_lower or "nghiêm trọng" in r_lower:
        return {
            "type": "Lệch ngữ cảnh (Context Drift)",
            "type_code": "drift",
            "severity": "CRITICAL",
            "severity_class": "sev-critical",
            "icon": "🔄"
        }
    elif "timeout" in r_lower or "không phản hồi" in r_lower:
        return {
            "type": "Hệ thống Timeout (>40s)",
            "type_code": "timeout",
            "severity": "HIGH",
            "severity_class": "sev-high",
            "icon": "⏱️"
        }
    elif "tiêu cực" in r_lower or "cấm" in r_lower:
        return {
            "type": "Chứa từ khóa cấm / tiêu cực",
            "type_code": "forbidden",
            "severity": "HIGH",
            "severity_class": "sev-high",
            "icon": "⛔"
        }
    else:
        return {
            "type": "Thiếu thông tin / Từ khóa kiểm thử",
            "type_code": "missing",
            "severity": "MEDIUM",
            "severity_class": "sev-medium",
            "icon": "🔍"
        }


def generate_defects_report_content(sessions: List[Dict[str, Any]]) -> str:
    """Builds the specialized defects-only HTML bug report."""
    raw_errors = []
    seen = set()

    for s in sessions:
        s_name = s.get("session_name", "Phiên kiểm thử")
        for e in s.get("entries", []):
            if e.get("is_error"):
                # Unique by AC tag and query
                key = (e.get("ac_tag"), e.get("query"))
                if key not in seen:
                    seen.add(key)
                    classification = classify_defect_type(e.get("reason", ""))
                    raw_errors.append({
                        "session": s_name,
                        "entry": e,
                        "classification": classification
                    })

    total_defects = len(raw_errors)
    count_critical = sum(1 for d in raw_errors if d["classification"]["severity"] == "CRITICAL")
    count_high = sum(1 for d in raw_errors if d["classification"]["severity"] == "HIGH")
    count_medium = sum(1 for d in raw_errors if d["classification"]["severity"] == "MEDIUM")

    count_drift = sum(1 for d in raw_errors if d["classification"]["type_code"] == "drift")
    count_timeout = sum(1 for d in raw_errors if d["classification"]["type_code"] == "timeout")
    count_missing = sum(1 for d in raw_errors if d["classification"]["type_code"] == "missing")

    # Table rows
    table_rows = []
    # Detail cards
    cards_html = []

    for idx, d in enumerate(raw_errors, start=1):
        e = d["entry"]
        cls = d["classification"]
        defect_id = f"BUG-{idx:02d}"
        card_dom_id = f"defect-card-{idx}"

        ac_tag = html.escape(e.get("ac_tag", ""))
        query = html.escape(e.get("query", ""))
        raw_resp = e.get("response", "")
        resp_formatted = format_markdown_text(raw_resp)
        resp_snippet = html.escape(raw_resp[:130] + ("..." if len(raw_resp) > 130 else ""))
        reason = html.escape(e.get("reason", ""))
        expected = html.escape(e.get("expected", ""))
        session_name = html.escape(d["session"])
        timestamp = html.escape(e.get("time", ""))

        # Category domain detection
        domain = "Quy trình AC"
        tag_lower = ac_tag.lower()
        if "sales" in tag_lower: domain = "Sales & Plans"
        elif "compat" in tag_lower: domain = "Compatibility"
        elif "conn" in tag_lower: domain = "Connection"
        elif "usage" in tag_lower: domain = "Usage & Plans"
        elif "cashback" in tag_lower: domain = "Cashback"
        elif "complaint" in tag_lower: domain = "Complaints"

        # Table row
        table_rows.append(f"""
        <tr class="bug-row" onclick="jumpToDefect('{card_dom_id}')">
            <td class="col-id"><strong>{defect_id}</strong></td>
            <td class="col-sev"><span class="badge-sev {cls['severity_class']}">{cls['severity']}</span></td>
            <td class="col-domain"><span class="badge-domain">{domain}</span></td>
            <td class="col-tag"><code>{ac_tag.split(' - ')[0]}</code></td>
            <td class="col-q"><strong>{query}</strong></td>
            <td class="col-type"><span class="type-pill">{cls['icon']} {cls['type']}</span></td>
            <td class="col-action"><button class="btn-sm-jump">🔍 Chi tiết</button></td>
        </tr>
        """)

        # Jira / Markdown copy text
        jira_copy_text = (
            f"*Issue:* [{defect_id}] {ac_tag}\\n"
            f"*Severity:* {cls['severity']}\\n"
            f"*Defect Type:* {cls['type']}\\n"
            f"*User Query:* {e.get('query')}\\n"
            f"*Actual AI Response:* {raw_resp[:300]}...\\n"
            f"*Expected Behavior:* {e.get('expected')}\\n"
            f"*Root Cause:* {e.get('reason')}"
        )
        jira_copy_attr = html.escape(jira_copy_text)

        # Bug Card
        cards_html.append(f"""
        <div id="{card_dom_id}" class="defect-card" data-domain="{domain.lower()}" data-type="{cls['type_code']}">
            <div class="card-header">
                <div class="header-left">
                    <span class="bug-code">{defect_id}</span>
                    <span class="badge-sev {cls['severity_class']}">{cls['severity']}</span>
                    <span class="card-ac-tag">{ac_tag}</span>
                </div>
                <div class="header-right">
                    <span class="defect-cat-pill">{cls['icon']} {cls['type']}</span>
                    <button class="btn-copy-ticket" onclick="copyBugTicket(this, '{jira_copy_attr}')">📋 Copy Jira Bug</button>
                </div>
            </div>

            <div class="card-body">
                <!-- Section 1: User Prompt -->
                <div class="section-box prompt-box">
                    <div class="box-title"><span class="icon">👤</span> 1. USER PROMPT (CÂU HỎI TỪ NGƯỜI DÙNG)</div>
                    <div class="box-content prompt-text">"{query}"</div>
                </div>

                <!-- Section 2: Actual AI Response (DEFECTIVE) -->
                <div class="section-box response-box">
                    <div class="box-title"><span class="icon">🤖</span> 2. ACTUAL AI RESPONSE (PHẢN HỒI THỰC TẾ BỊ SAI LỆCH)</div>
                    <div class="box-content response-text">{resp_formatted}</div>
                </div>

                <!-- Section 3: Defect Analysis & Root Cause -->
                <div class="section-box defect-analysis-box">
                    <div class="box-title"><span class="icon">🚨</span> 3. PHÂN TÍCH LỖI & NGUYÊN NHÂN (DEFECT ANALYSIS)</div>
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
                            <span class="item-label">🕒 Thời điểm ghi nhận:</span>
                            <span class="item-val text-muted">{timestamp} ({session_name})</span>
                        </div>
                    </div>
                </div>

                <!-- Section 4: Reproduction Steps -->
                <div class="section-box repro-box">
                    <div class="box-title"><span class="icon">🛠️</span> 4. CÁC BƯỚC TÁI HIỆN (STEPS TO REPRODUCE)</div>
                    <ol class="repro-list">
                        <li>Mở ứng dụng Eskimo UAT và truy cập màn hình <strong>In-App Chat ("Ask Eski!")</strong>.</li>
                        <li>Gửi câu hỏi chính xác: <code>{query}</code></li>
                        <li>Quan sát nội dung phản hồi từ Eski và đối chiếu với hành vi kỳ vọng nêu trên.</li>
                    </ol>
                </div>
            </div>
        </div>
        """)

    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""<!DOCTYPE html>
<html lang="vi" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eskimo Sale AI Agent — Báo Cáo Tổng Hợp Lỗi Phản Hồi (Defect Report)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #090d16;
            --bg-surface: #111827;
            --bg-card: #1f2937;
            --bg-card-hover: #2a3749;
            --border-color: rgba(255, 255, 255, 0.09);
            --border-focus: #ef4444;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --text-sub: #6b7280;
            --primary: #3b82f6;
            
            /* Crimson / Red Alert Palette */
            --danger-red: #ef4444;
            --danger-dark: #b91c1c;
            --danger-bg: rgba(239, 68, 68, 0.1);
            --danger-border: rgba(239, 68, 68, 0.45);
            --danger-glow: 0 0 25px rgba(239, 68, 68, 0.25);
            
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.4);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -2px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.6), 0 4px 6px -4px rgba(0, 0, 0, 0.5);
        }}

        [data-theme="light"] {{
            --bg-base: #f8fafc;
            --bg-surface: #ffffff;
            --bg-card: #f1f5f9;
            --bg-card-hover: #e2e8f0;
            --border-color: #cbd5e1;
            --border-focus: #ef4444;
            --text-main: #0f172a;
            --text-muted: #475569;
            --text-sub: #64748b;
            --danger-bg: #fef2f2;
            --danger-border: rgba(239, 68, 68, 0.5);
            --danger-glow: 0 0 20px rgba(239, 68, 68, 0.15);
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            line-height: 1.6;
            padding: 24px 16px;
            transition: background-color 0.3s ease, color 0.3s ease;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        /* Header */
        .report-header {{
            background: var(--bg-surface);
            border: 2px solid var(--danger-border);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 24px;
            box-shadow: var(--danger-glow);
        }}

        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
        }}

        .badge-brand {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(239, 68, 68, 0.15);
            color: var(--danger-red);
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 8px;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}

        .report-title {{
            font-size: 2rem;
            font-weight: 800;
            color: var(--text-main);
            letter-spacing: -0.02em;
        }}

        .report-subtitle {{
            font-size: 0.98rem;
            color: var(--text-muted);
            margin-top: 5px;
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
            padding: 10px 18px;
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
            border-color: var(--danger-red);
        }}

        .btn-danger {{
            background: var(--danger-red);
            color: #ffffff;
            border-color: var(--danger-red);
        }}

        .btn-danger:hover {{
            background: var(--danger-dark);
        }}

        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            border-top: 1px solid var(--border-color);
            padding-top: 24px;
        }}

        .metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px;
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .metric-card.card-crit {{
            border-color: var(--danger-border);
            background: var(--danger-bg);
        }}

        .metric-icon {{
            font-size: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            width: 52px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .metric-val {{
            font-size: 1.7rem;
            font-weight: 800;
            color: var(--text-main);
        }}

        .metric-val.text-red {{ color: var(--danger-red); }}
        .metric-val.text-amber {{ color: var(--accent-amber); }}
        .metric-val.text-blue {{ color: var(--primary); }}

        .metric-lbl {{
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 700;
        }}

        /* Defect Matrix Section */
        .matrix-section {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 28px;
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
            font-size: 1.3rem;
            font-weight: 800;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .table-wrap {{
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }}

        .bug-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
            background: var(--bg-card);
            text-align: left;
        }}

        .bug-table th {{
            background: rgba(0, 0, 0, 0.3);
            padding: 12px 16px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.76rem;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--border-color);
        }}

        .bug-table td {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
        }}

        .bug-row {{
            cursor: pointer;
            transition: background 0.2s;
        }}

        .bug-row:hover {{
            background: rgba(239, 68, 68, 0.12);
        }}

        .col-id {{
            color: var(--danger-red);
            font-weight: 800;
        }}

        .badge-sev {{
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.05em;
        }}

        .sev-critical {{
            background: #ef4444;
            color: #ffffff;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
        }}

        .sev-high {{
            background: #f59e0b;
            color: #ffffff;
        }}

        .sev-medium {{
            background: #3b82f6;
            color: #ffffff;
        }}

        .badge-domain {{
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-muted);
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
        }}

        .type-pill {{
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 700;
        }}

        .btn-sm-jump {{
            background: var(--danger-red);
            color: #ffffff;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap;
        }}

        .btn-sm-jump:hover {{
            background: var(--danger-dark);
        }}

        /* Toolbar */
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
            gap: 8px;
            flex-wrap: wrap;
        }}

        .btn-filter {{
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.84rem;
            font-weight: 700;
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
            background: var(--danger-red);
            border-color: var(--danger-red);
            color: #ffffff;
        }}

        /* Detailed Bug Cards */
        .defect-cards-section {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}

        .defect-card {{
            background: var(--bg-surface);
            border: 2px solid var(--danger-border);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: var(--shadow-md);
            transition: all 0.25s ease;
            position: relative;
        }}

        .defect-card:hover {{
            box-shadow: var(--danger-glow);
            border-color: var(--danger-red);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(239, 68, 68, 0.12);
            padding: 16px 24px;
            border-bottom: 1px solid var(--danger-border);
            flex-wrap: wrap;
            gap: 12px;
        }}

        .header-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .bug-code {{
            background: var(--danger-dark);
            color: #ffffff;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.88rem;
            letter-spacing: 0.04em;
        }}

        .card-ac-tag {{
            font-weight: 700;
            color: var(--text-main);
            font-size: 0.95rem;
        }}

        .header-right {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .defect-cat-pill {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-main);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .btn-copy-ticket {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .btn-copy-ticket:hover {{
            background: var(--danger-red);
            color: #ffffff;
            border-color: var(--danger-red);
        }}

        .card-body {{
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 18px;
        }}

        .section-box {{
            border-radius: 12px;
            padding: 16px;
            border: 1px solid var(--border-color);
        }}

        .box-title {{
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 8px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .prompt-box {{
            background: rgba(59, 130, 246, 0.08);
            border-left: 5px solid var(--primary);
        }}

        .prompt-text {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #93c5fd;
        }}

        .response-box {{
            background: rgba(239, 68, 68, 0.08);
            border-left: 5px solid var(--danger-red);
        }}

        .response-text {{
            font-size: 0.95rem;
            color: #fca5a5;
        }}

        .defect-analysis-box {{
            background: var(--bg-card);
            border-left: 5px solid var(--accent-amber);
        }}

        .analysis-grid {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 0.92rem;
        }}

        .analysis-item {{
            display: flex;
            gap: 10px;
            align-items: baseline;
        }}

        .item-label {{
            font-weight: 700;
            color: var(--text-muted);
            min-width: 160px;
            flex-shrink: 0;
            font-size: 0.84rem;
            text-transform: uppercase;
        }}

        .item-val {{
            flex: 1;
        }}

        .highlight-red {{
            color: #f87171;
            font-weight: 700;
        }}

        .highlight-green {{
            color: #34d399;
            font-weight: 600;
        }}

        .repro-box {{
            background: rgba(255, 255, 255, 0.02);
            border-left: 5px solid var(--text-muted);
        }}

        .repro-list {{
            margin-left: 20px;
            font-size: 0.88rem;
            color: var(--text-muted);
        }}

        .repro-list li {{
            margin-bottom: 4px;
        }}

        .repro-list code {{
            background: rgba(0, 0, 0, 0.3);
            color: #fbcfe8;
            padding: 2px 6px;
            border-radius: 4px;
        }}

        /* Toast notification */
        .toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: var(--danger-dark);
            color: #ffffff;
            padding: 12px 22px;
            border-radius: 10px;
            font-size: 0.92rem;
            font-weight: 700;
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

        @keyframes flashRed {{
            0% {{ outline: 5px solid var(--danger-red); transform: scale(1.01); }}
            100% {{ outline: 0px solid transparent; transform: scale(1); }}
        }}

        .flash-highlight {{
            animation: flashRed 1.8s ease-out;
        }}

        @media (max-width: 768px) {{
            .metrics-grid {{ grid-template-columns: 1fr; }}
            .analysis-item {{ flex-direction: column; gap: 2px; }}
            .item-label {{ min-width: auto; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="report-header">
            <div class="header-top">
                <div>
                    <div class="badge-brand">🚨 Eskimo QA · Defect Report</div>
                    <h1 class="report-title">Danh Sách Các Lỗi Phản Hồi Từ AI (Failures Only)</h1>
                    <p class="report-subtitle">Tài liệu tổng hợp các case kiểm thử không đạt để bàn giao đội ngũ phát triển (Dev) điều chỉnh Prompt / Logic Agent</p>
                </div>
                <div class="header-actions">
                    <button class="btn" onclick="toggleTheme()">🌓 Đổi theme</button>
                    <button class="btn btn-danger" onclick="window.print()">🖨️ Xuất PDF / In</button>
                </div>
            </div>

            <!-- Metrics Grid -->
            <div class="metrics-grid">
                <div class="metric-card card-crit">
                    <div class="metric-icon">🚨</div>
                    <div>
                        <div class="metric-val text-red">{total_defects} LỖI</div>
                        <div class="metric-lbl">Tổng số ca lỗi phát hiện</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">🔄</div>
                    <div>
                        <div class="metric-val text-red">{count_drift}</div>
                        <div class="metric-lbl">Lỗi lệch ngữ cảnh (Drift)</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">⏱️</div>
                    <div>
                        <div class="metric-val text-amber">{count_timeout}</div>
                        <div class="metric-lbl">Lỗi Timeout (>40s)</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">🔍</div>
                    <div>
                        <div class="metric-val text-blue">{count_missing}</div>
                        <div class="metric-lbl">Thiếu thông tin / Từ khóa</div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Defect Matrix Table -->
        <section class="matrix-section">
            <div class="section-header">
                <div>
                    <h2 class="section-title">📊 BẢNG TRA CỨU NHANH DANH SÁCH LỖI ({total_defects} DEFECTS)</h2>
                    <p class="report-subtitle">Click vào bất kỳ hàng nào để cuộn nhanh đến thẻ chi tiết và copy định dạng Jira bug ticket.</p>
                </div>
            </div>

            <div class="table-wrap">
                <table class="bug-table">
                    <thead>
                        <tr>
                            <th>Mã Bug</th>
                            <th>Mức độ</th>
                            <th>Nhóm</th>
                            <th>Tiêu chí</th>
                            <th>Câu hỏi từ người dùng (Query)</th>
                            <th>Phân loại lỗi</th>
                            <th>Thao tác</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(table_rows)}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Search & Filter Toolbar -->
        <div class="toolbar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" placeholder="Tìm kiếm theo mã bug, câu hỏi, từ khóa lỗi..." oninput="filterCards()">
            </div>
            <div class="filter-group">
                <button class="btn-filter active" onclick="setFilterType('all', this)">Tất cả ({total_defects})</button>
                <button class="btn-filter" onclick="setFilterType('drift', this)">🔄 Lệch ngữ cảnh ({count_drift})</button>
                <button class="btn-filter" onclick="setFilterType('timeout', this)">⏱️ Timeout ({count_timeout})</button>
                <button class="btn-filter" onclick="setFilterType('missing', this)">🔍 Thiếu từ khóa ({count_missing})</button>
            </div>
        </div>

        <!-- Defect Detail Cards List -->
        <main class="defect-cards-section">
            {''.join(cards_html)}
        </main>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="toast">Đã copy nội dung Jira Bug Ticket!</div>

    <script>
        let currentType = 'all';

        function toggleTheme() {{
            const html = document.documentElement;
            const current = html.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
        }}

        function setFilterType(type, btn) {{
            currentType = type;
            document.querySelectorAll('.filter-group .btn-filter').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterCards();
        }}

        function filterCards() {{
            const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
            const cards = document.querySelectorAll('.defect-card');

            cards.forEach(card => {{
                const text = card.innerText.toLowerCase();
                const cardType = card.getAttribute('data-type');

                let match = true;
                if (query && !text.includes(query)) match = false;
                if (currentType !== 'all' && cardType !== currentType) match = false;

                card.style.display = match ? 'block' : 'none';
            }});
        }}

        function jumpToDefect(cardId) {{
            const target = document.getElementById(cardId);
            if (target) {{
                target.style.display = 'block';
                target.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                target.classList.add('flash-highlight');
                setTimeout(() => target.classList.remove('flash-highlight'), 2000);
            }}
        }}

        function copyBugTicket(btn, text) {{
            // unescape newline
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


def export_defects_html(md_path: str = DEFAULT_MD_PATH, output_path: str = OUTPUT_DEFECTS_HTML) -> str:
    """Parses transcript and writes defects-only HTML report."""
    sessions = parse_markdown_transcript(md_path)
    html_content = generate_defects_report_content(sessions)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return os.path.abspath(output_path)


if __name__ == "__main__":
    out_file = export_defects_html()
    print(f"Defects report successfully generated at: {out_file}")
