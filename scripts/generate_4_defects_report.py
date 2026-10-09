"""
Generator for Dedicated 4 Critical Failures Defect Report (Eskimo Sale AI Agent).
Builds a focused, executive-ready, highly polished HTML report for the 4 critical
context-drift / response desynchronization defects.
"""

import os
import html
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_HTML_PATH = os.path.join(ROOT_DIR, "reports", "html", "report_4_defects_fail.html")

DEFECTS_DATA = [
    {
        "id": "BUG-01",
        "ac": "AC1.1",
        "title": "Kiểm tra số dư Data và Gói cước còn lại (Check Data Plans Remaining)",
        "query": "How much data do I have left, and how many plans do I currently have?",
        "expected": "Kiểm tra và thông báo chính xác số dung lượng data còn lại (MB/GB) và danh sách các gói cước đang kích hoạt trong tài khoản.",
        "actual": "- Samsung Galaxy S24: The exact model wasn’t found in our compatibility list, so I can’t confirm it definitively. eSIM support can vary by regional variant and carrier. Please check Settings → Connections → SIM manager for Add eSIM.\n- iPhone 6: Not compatible with eSIM. You’ll need an eSIM-compatible iPhone model or Android device.",
        "root_cause": "Lệch ngữ cảnh nghiêm trọng (Context Drift) do trôi dữ liệu phiên trước. Khách hỏi số dư tài khoản nhưng AI lại trả lời kịch bản kiểm tra tương thích thiết bị của phiên test trước đó.",
        "severity": "CRITICAL",
        "chips": ["I want to check another phone", "How do I install eSIM on Android", "How do I install eSIM on iPhone"],
        "technical_fix": "Cần thêm bước xóa sạch Session Memory / Chat Context cache khi user reset chat hoặc bắt đầu phiên mới; đồng thời bắt buộc gửi `session_id` duy nhất cho mỗi cuộc hội thoại."
    },
    {
        "id": "BUG-02",
        "ac": "AC1.3",
        "title": "Trạng thái Referral & Mã giới thiệu (Referral Status & Code)",
        "query": "Check my referral status: how many friends referred, bonus data remaining, and what is my referral code?",
        "expected": "Báo số lượng bạn bè đã giới thiệu thành công, dung lượng data thưởng nhận được và hiển thị rõ mã giới thiệu (ví dụ: KIEU1606).",
        "actual": "You currently have 5 active plans:\n- Global 10GB (Activated: Sept 18, 2026 - No expiry)\n- Global 10GB (Activated: Sept 18, 2026 - No expiry)\n- Global 1GB (Activated: Sept 18, 2026 - No expiry)\n- Japan 1GB (Activated: Sept 18, 2026 - No expiry)\n- Asia Pacific 1GB (Activated: Sept 14, 2026 - No expiry)\nYour exact remaining data for these active plans couldn’t be confirmed right now...",
        "root_cause": "Trễ 1 nhịp hội thoại (1-Step Sequential Lag). AI trả lời nội dung của câu hỏi AC1.1 (hỏi về gói cước) thay vì trả lời câu hỏi hiện tại về Referral.",
        "severity": "CRITICAL",
        "chips": ["Show my plan details", "How do I check usage?", "Which plan works in Japan?"],
        "technical_fix": "Đồng bộ hóa hàng đợi tin nhắn (Message Queue Sync). Đảm bảo response của prompt N đã hoàn tất và kết thúc stream trước khi client nhận prompt N+1."
    },
    {
        "id": "BUG-03",
        "ac": "AC2",
        "title": "Gợi ý nhiều gói cước cùng lúc đi Nhật Bản (Recommend Multiple Plans for Japan)",
        "query": "Recommend multiple plans at once as a list for Japan for me to choose from.",
        "expected": "Liệt kê danh sách đa dạng các gói cước đi Nhật (1GB, 3GB, 5GB, 10GB...) kèm giá tiền, ưu đãi và hiển thị Plan Carousel (rvPlans).",
        "actual": "Great news! Your WELCOME promo code was redeemed successfully and gives you 50% off.",
        "root_cause": "Trễ phản hồi / Desync ngữ cảnh. Khách hỏi tư vấn gói du lịch Nhật Bản, AI lại phản hồi thông báo nạp thành công mã giảm giá WELCOME.",
        "severity": "CRITICAL",
        "chips": ["Show plans for my next trip", "How does Eskimo cashback work?", "Can I use a gift code?"],
        "technical_fix": "Xử lý Request Cancellation trên backend: Nếu user gửi tin nhắn mới, backend phải hủy luồng xử lý của prompt cũ và map chính xác Intent của tin nhắn mới nhất."
    },
    {
        "id": "BUG-04",
        "ac": "AC3.1",
        "title": "Hướng dẫn cài đặt eSIM trên Android (Installation Instructions Android)",
        "query": "Provide step-by-step installation instructions for Android.",
        "expected": "Cung cấp các bước cài đặt eSIM rõ ràng trên thiết bị Android: Vào Settings -> Connections -> SIM manager -> Add eSIM -> Scan QR code.",
        "actual": "Here are three verified Japan options. Your WELCOME code gives 50% off, reflected in the prices below:\n1. Best for light usage — Japan 1GB: No expiry · $1.95\n2. Best balance — Japan 5GB: No expiry · $5.45\n3. Best for heavier usage — Japan 10GB: No expiry · $8.95\n(Kèm hiển thị Carousel 2 gói cước)",
        "root_cause": "Lệch phản hồi 1 bước (Lagged Response). Câu trả lời về các gói cước Nhật Bản (được hỏi ở AC2) lại được AI trả về cho câu hỏi hướng dẫn cài đặt Android (AC3.1).",
        "severity": "CRITICAL",
        "chips": ["I want the Japan 1GB plan", "I want the Japan 5GB plan", "I want the Japan 10GB plan"],
        "technical_fix": "Triển khai Correlation ID (Request-ID / Turn-ID) cho từng tin nhắn. App client chỉ render câu trả lời khi response.request_id khớp với tin nhắn đang active."
    }
]


def generate_html_content() -> str:
    cards_html = []
    table_rows = []

    for idx, d in enumerate(DEFECTS_DATA, start=1):
        chips_str = "".join([f'<span class="chip">💡 {c}</span>' for c in d["chips"]])
        actual_formatted = d["actual"].replace("\n", "<br>")

        jira_markup = f"""*Defect ID:* {d['id']}
*Acceptance Criteria:* {d['ac']} - {d['title']}
*Severity:* {d['severity']}
*User Query:* {d['query']}
*Expected:* {d['expected']}
*Actual:* {d['actual']}
*Root Cause:* {d['root_cause']}
*Recommended Fix:* {d['technical_fix']}"""
        jira_escaped = html.escape(jira_markup).replace('"', '&quot;')

        table_rows.append(f"""
        <tr>
            <td><strong class="bug-badge">{d['id']}</strong></td>
            <td><span class="ac-tag">{d['ac']}</span></td>
            <td><strong>{html.escape(d['title'])}</strong></td>
            <td class="query-cell">"{html.escape(d['query'])}"</td>
            <td><span class="sev-badge sev-critical">{d['severity']}</span></td>
            <td><a href="#card-{d['id']}" class="jump-link">Xem chi tiết ➔</a></td>
        </tr>
        """)

        cards_html.append(f"""
        <div class="defect-card" id="card-{d['id']}">
            <div class="card-header">
                <div class="card-title-group">
                    <span class="bug-id">{d['id']}</span>
                    <span class="ac-badge">{d['ac']}</span>
                    <h3 class="card-title">{html.escape(d['title'])}</h3>
                </div>
                <div class="card-actions">
                    <span class="sev-badge sev-critical">CRITICAL</span>
                    <button class="btn-copy" onclick="copyJiraTicket('{jira_escaped}', this)">
                        📋 Copy Jira / Bug
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
                    <div class="box-label">🤖 AI Phản hồi thực tế (Actual AI Response):</div>
                    <div class="box-content actual-text">{actual_formatted}</div>
                    <div class="chips-container">
                        {chips_str}
                    </div>
                </div>

                <div class="analysis-box">
                    <div class="analysis-title">⚠️ Phân tích nguyên nhân lỗi (Root Cause Analysis):</div>
                    <p class="analysis-desc">{html.escape(d['root_cause'])}</p>
                    <div class="fix-title">🛠️ Khuyến nghị khắc phục cho Developer (Recommended Fix):</div>
                    <p class="fix-desc">{html.escape(d['technical_fix'])}</p>
                </div>
            </div>
        </div>
        """)

    html_template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eskimo Sale AI Agent — Báo Cáo 4 Lỗi Nghiêm Trọng (Context Drift)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0f1d;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.85);
            --border-color: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(239, 68, 68, 0.4);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-red: #ef4444;
            --accent-red-bg: rgba(239, 68, 68, 0.12);
            --accent-blue: #38bdf8;
            --accent-blue-bg: rgba(56, 189, 248, 0.1);
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --shadow-card: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            --glass-filter: blur(16px);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding-bottom: 80px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
        }}

        /* Header */
        header {{
            padding: 40px 0 28px;
            border-bottom: 1px solid var(--border-color);
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, transparent 100%);
            margin-bottom: 32px;
        }}

        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .brand-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-red);
            background: var(--accent-red-bg);
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 6px 14px;
            border-radius: 999px;
            margin-bottom: 12px;
        }}

        h1 {{
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #fff 40%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .subtitle {{
            color: var(--text-secondary);
            font-size: 15px;
            max-width: 700px;
        }}

        .header-actions {{
            display: flex;
            gap: 12px;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            border: 1px solid var(--border-color);
        }}

        .btn-primary {{
            background: var(--accent-red);
            color: #fff;
            border-color: transparent;
        }}
        .btn-primary:hover {{
            background: #dc2626;
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
        }}

        .btn-outline {{
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-primary);
        }}
        .btn-outline:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}

        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 20px;
            margin-bottom: 36px;
        }}

        .metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            padding: 24px;
            border-radius: 16px;
            backdrop-filter: var(--glass-filter);
            box-shadow: var(--shadow-card);
            position: relative;
            overflow: hidden;
        }}

        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
        }}

        .metric-card.red::before {{ background: var(--accent-red); }}
        .metric-card.amber::before {{ background: var(--accent-amber); }}
        .metric-card.blue::before {{ background: var(--accent-blue); }}

        .metric-label {{
            font-size: 13px;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .metric-value {{
            font-size: 34px;
            font-weight: 800;
            color: #fff;
            margin-bottom: 6px;
        }}

        .metric-sub {{
            font-size: 13px;
            color: var(--text-muted);
        }}

        /* Summary Table Section */
        .section-title {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .table-container {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 40px;
            box-shadow: var(--shadow-card);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th {{
            background: rgba(255, 255, 255, 0.03);
            color: var(--text-secondary);
            font-size: 13px;
            font-weight: 600;
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-color);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        td {{
            padding: 18px 20px;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
            vertical-align: middle;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}

        .bug-badge {{
            font-family: 'JetBrains Mono', monospace;
            color: var(--accent-red);
            font-weight: 700;
        }}

        .ac-tag {{
            background: rgba(255, 255, 255, 0.08);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-family: 'JetBrains Mono', monospace;
        }}

        .query-cell {{
            max-width: 320px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: var(--text-secondary);
            font-style: italic;
        }}

        .sev-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.5px;
        }}

        .sev-critical {{
            background: var(--accent-red-bg);
            color: var(--accent-red);
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}

        .jump-link {{
            color: var(--accent-blue);
            text-decoration: none;
            font-weight: 600;
            font-size: 13px;
            transition: color 0.2s;
        }}
        .jump-link:hover {{
            text-decoration: underline;
        }}

        /* Defect Cards */
        .defects-list {{
            display: flex;
            flex-direction: column;
            gap: 28px;
        }}

        .defect-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: var(--shadow-card);
            transition: border-color 0.2s, box-shadow 0.2s;
        }}

        .defect-card:hover {{
            border-color: var(--border-hover);
            box-shadow: 0 12px 36px -10px rgba(239, 68, 68, 0.2);
        }}

        .card-header {{
            padding: 20px 26px;
            background: rgba(255, 255, 255, 0.02);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .card-title-group {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .bug-id {{
            font-family: 'JetBrains Mono', monospace;
            background: var(--accent-red);
            color: #fff;
            font-size: 12px;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 6px;
        }}

        .ac-badge {{
            font-family: 'JetBrains Mono', monospace;
            background: var(--accent-blue-bg);
            color: var(--accent-blue);
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
        }}

        .card-title {{
            font-size: 18px;
            font-weight: 700;
            color: #fff;
        }}

        .card-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .btn-copy {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: var(--text-primary);
            font-size: 12px;
            font-weight: 600;
            padding: 6px 14px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .btn-copy:hover {{
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
        }}

        .card-body {{
            padding: 26px;
        }}

        .dialogue-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
            margin-bottom: 20px;
        }}

        @media (max-width: 768px) {{
            .dialogue-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .dialogue-box {{
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px 18px;
        }}

        .box-label {{
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .user-box .box-label {{ color: var(--accent-blue); }}
        .expected-box .box-label {{ color: var(--accent-green); }}

        .prompt-text {{
            font-size: 15px;
            font-weight: 600;
            color: #fff;
            font-style: italic;
        }}

        .expected-text {{
            font-size: 14px;
            color: #cbd5e1;
        }}

        .actual-box {{
            background: rgba(239, 68, 68, 0.06);
            border: 1px solid rgba(239, 68, 68, 0.25);
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 20px;
        }}

        .actual-box .box-label {{
            color: var(--accent-red);
            font-size: 13px;
        }}

        .actual-text {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #fca5a5;
            line-height: 1.6;
            margin-top: 6px;
            white-space: pre-wrap;
            background: rgba(0, 0, 0, 0.3);
            padding: 14px;
            border-radius: 8px;
        }}

        .chips-container {{
            margin-top: 12px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .chip {{
            font-size: 12px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-secondary);
            padding: 4px 10px;
            border-radius: 20px;
        }}

        .analysis-box {{
            background: rgba(15, 23, 42, 0.6);
            border-left: 4px solid var(--accent-amber);
            border-radius: 0 12px 12px 0;
            padding: 16px 20px;
        }}

        .analysis-title {{
            color: var(--accent-amber);
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 6px;
        }}

        .analysis-desc {{
            font-size: 14px;
            color: #e2e8f0;
            margin-bottom: 12px;
        }}

        .fix-title {{
            color: var(--accent-blue);
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 6px;
        }}

        .fix-desc {{
            font-size: 13.5px;
            color: #94a3b8;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Toast */
        .toast {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #10b981;
            color: #fff;
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s;
            pointer-events: none;
            z-index: 1000;
        }}

        .toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}

        /* Print Media */
        @media print {{
            body {{
                background: #fff !important;
                color: #000 !important;
                padding-bottom: 0;
            }}
            .header-actions, .btn-copy, .jump-link {{
                display: none !important;
            }}
            .defect-card, .table-container, .metric-card {{
                box-shadow: none !important;
                border: 1px solid #ccc !important;
                background: #fff !important;
                page-break-inside: avoid;
            }}
            h1, .card-title, .box-content, .analysis-desc {{
                color: #000 !important;
                -webkit-text-fill-color: initial !important;
            }}
            .actual-box {{
                background: #fff5f5 !important;
                border: 1px solid #feb2b2 !important;
            }}
            .actual-text {{
                background: #f7fafc !important;
                color: #c53030 !important;
            }}
        }}
    </style>
</head>
<body>

    <header>
        <div class="container header-content">
            <div>
                <span class="brand-badge">🚨 Critical Defects Report</span>
                <h1>Eskimo Sale AI Agent — 4 Lỗi Fail Nghiêm Trọng</h1>
                <p class="subtitle">Báo cáo tổng hợp chuyên sâu về lỗi <strong>Lệch ngữ cảnh (Context Drift / Response Desync)</strong> xảy ra trong phiên kiểm thử tự động kênh In-App Chat.</p>
            </div>
            <div class="header-actions">
                <button class="btn btn-outline" onclick="window.print()">🖨️ In ra PDF</button>
                <a href="ai_chat_report.html" class="btn btn-primary">📊 Mở Báo cáo Toàn diện</a>
            </div>
        </div>
    </header>

    <main class="container">
        <!-- Metrics -->
        <section class="metrics-grid">
            <div class="metric-card red">
                <div class="metric-label">Tổng số lỗi phát hiện</div>
                <div class="metric-value">4 Ca Fail</div>
                <div class="metric-sub">100% thuộc mức độ CRITICAL (P1)</div>
            </div>
            <div class="metric-card amber">
                <div class="metric-label">Bản chất lỗi (Root Cause)</div>
                <div class="metric-value">Context Drift</div>
                <div class="metric-sub">Lệch phản hồi 1 nhịp hội thoại (Desync)</div>
            </div>
            <div class="metric-card blue">
                <div class="metric-label">Kênh kiểm thử bị ảnh hưởng</div>
                <div class="metric-value">In-App Chat</div>
                <div class="metric-sub">Eski Sale AI Agent (Android UAT)</div>
            </div>
        </section>

        <!-- Summary Table -->
        <h2 class="section-title">📋 Bảng Đối Chiếu 4 Lỗi Nghiêm Trọng</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Mã Defect</th>
                        <th>AC</th>
                        <th>Hạng mục kiểm thử</th>
                        <th>Câu hỏi của khách (Prompt)</th>
                        <th>Mức độ</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
        </div>

        <!-- Defect Cards Details -->
        <h2 class="section-title">🔍 Chi Tiết Từng Lỗi & Hướng Khắc Phục Kỹ Thuật</h2>
        <div class="defects-list">
            {''.join(cards_html)}
        </div>
    </main>

    <div id="toast" class="toast">Đã copy nội dung Jira Ticket vào Clipboard!</div>

    <script>
        function copyJiraTicket(text, btnElem) {{
            navigator.clipboard.writeText(text).then(() => {{
                const toast = document.getElementById('toast');
                toast.classList.add('show');
                const oldText = btnElem.innerHTML;
                btnElem.innerHTML = '✅ Đã Copy!';
                setTimeout(() => {{
                    toast.classList.remove('show');
                    btnElem.innerHTML = oldText;
                }}, 2500);
            }}).catch(err => {{
                alert('Không thể tự động copy: ' + err);
            }});
        }}
    </script>
</body>
</html>
"""
    return html_template


def export_4_defects_report(output_path: str = OUTPUT_HTML_PATH) -> str:
    content = generate_html_content()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    out_file = export_4_defects_report()
    print(f"4 Defects report successfully generated at: {out_file}")
