import argparse
import html
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


LOG_LINE_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*(?P<level>[A-Z]+)\s*\|\s*(?P<logger>[^|]+?)\s*\|\s*(?P<msg>.*)$"
)
TARGET_RE = re.compile(
    r"^Target\s*\|\s*summary=(?P<summary>.*)$"
)
APPIUM_START_RE = re.compile(
    r"^Appium server started successfully\s*\|\s*(?P<kv>.*)$"
)
TEST_START_RE = re.compile(
    r"^TEST START\s*\|\s*test=(?P<test>\S+)\s+module=(?P<module>\S+)\s+platform=(?P<platform>\S+)"
)
VIDEO_START_RE = re.compile(
    r"^Video recording started\s*\|\s*video=(?P<video>.+)$"
)
ERROR_CAPTURED_RE = re.compile(
    r"^Error Captured:\s*(?P<error>.+)$"
)
SCREENSHOT_RE = re.compile(
    r"^Screenshot saved\s*\|\s*path=(?P<path>.+)$"
)
PAGESOURCE_RE = re.compile(
    r"^Page source saved\s*\|\s*path=(?P<path>.+)$"
)
TEST_FINISH_RE = re.compile(
    r"^TEST FINISH\s*\|\s*test=(?P<test>\S+)\s+outcome=(?P<outcome>\S+)\s+duration_s=(?P<duration>[\d.]+)"
)
SESSION_FINISH_RE = re.compile(
    r"^Test session finished\s*\|\s*exitstatus=(?P<exitstatus>-?\d+)\s+passed=(?P<passed>\d+)\s+failed=(?P<failed>\d+)\s+skipped=(?P<skipped>\d+)\s+error=(?P<error>\d+)\s+suite_log=(?P<suite_log>.+)$"
)


def _extract_kv(text: str, key: str, default: str = "") -> str:
    m = re.search(rf"{re.escape(key)}=(?:'([^']*)'|\"([^\"]*)\"|(\S+))", text)
    if not m:
        return default
    return m.group(1) or m.group(2) or m.group(3) or default


def _to_relative_href(raw_path: Optional[str], report_dir: Path) -> Optional[str]:
    if not raw_path:
        return None
    cleaned = raw_path.strip().strip("'").strip('"')
    if not cleaned:
        return None
    try:
        p = Path(cleaned)
        if not p.is_absolute():
            p = (report_dir.parent.parent / p).resolve()
        rel = os.path.relpath(p, report_dir)
        return rel.replace("\\", "/")
    except Exception:
        return cleaned.replace("\\", "/")


def parse_suite_log(log_path: Path) -> Dict[str, Any]:
    """Parse structured `suite.log` into session metadata and per-test execution records."""
    session_info: Dict[str, Any] = {
        "start_time": "",
        "end_time": "",
        "platform": "android",
        "device_name": "emulator-5554",
        "udid": "emulator-5554",
        "appium_version": "2.x",
        "tests": [],
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "error": 0,
        "total_duration_s": 0.0,
    }

    if not log_path.exists():
        return session_info

    current_test: Optional[Dict[str, Any]] = None
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()

    for line in lines:
        m_line = LOG_LINE_RE.match(line)
        if not m_line:
            continue

        ts = m_line.group("ts")
        level = m_line.group("level").strip()
        msg = m_line.group("msg").strip()

        if not session_info["start_time"]:
            session_info["start_time"] = ts
        session_info["end_time"] = ts

        # 1. Target summary
        m_target = TARGET_RE.match(msg)
        if m_target:
            summary = m_target.group("summary")
            session_info["platform"] = _extract_kv(summary, "platform", "android")
            session_info["device_name"] = _extract_kv(summary, "device_name", "emulator-5554")
            session_info["udid"] = _extract_kv(summary, "udid", session_info["device_name"])
            continue

        # 2. Appium server started
        m_appium = APPIUM_START_RE.match(msg)
        if m_appium:
            kv_str = m_appium.group("kv")
            session_info["appium_version"] = _extract_kv(kv_str, "version", "2.x")
            continue

        # 3. TEST START
        m_start = TEST_START_RE.match(msg)
        if m_start:
            if current_test is not None:
                session_info["tests"].append(current_test)
            current_test = {
                "name": m_start.group("test"),
                "module": m_start.group("module"),
                "platform": m_start.group("platform"),
                "start_time": ts,
                "outcome": "running",
                "duration_s": 0.0,
                "video": None,
                "screenshot": None,
                "page_source": None,
                "error": None,
                "logs": [],
            }
            continue

        # 4. Video recording started
        m_video = VIDEO_START_RE.match(msg)
        if m_video and current_test is not None:
            current_test["video"] = m_video.group("video").strip()
            continue

        # 5. Error Captured
        m_err = ERROR_CAPTURED_RE.match(msg)
        if m_err and current_test is not None:
            current_test["error"] = m_err.group("error").strip()
            current_test["logs"].append(f"[{ts}] [{level}] {msg}")
            continue

        # 6. Screenshot saved
        m_shot = SCREENSHOT_RE.match(msg)
        if m_shot and current_test is not None:
            current_test["screenshot"] = m_shot.group("path").strip()
            continue

        # 7. Page source saved
        m_ps = PAGESOURCE_RE.match(msg)
        if m_ps and current_test is not None:
            current_test["page_source"] = m_ps.group("path").strip()
            continue

        # 8. TEST FINISH
        m_finish = TEST_FINISH_RE.match(msg)
        if m_finish:
            finish_name = m_finish.group("test")
            outcome = m_finish.group("outcome").lower()
            dur = float(m_finish.group("duration"))
            if current_test is None or current_test["name"] != finish_name:
                current_test = {
                    "name": finish_name,
                    "module": "tests",
                    "platform": session_info["platform"],
                    "start_time": ts,
                    "outcome": outcome,
                    "duration_s": dur,
                    "video": None,
                    "screenshot": None,
                    "page_source": None,
                    "error": None,
                    "logs": [],
                }
            else:
                current_test["outcome"] = outcome
                current_test["duration_s"] = dur

            session_info["tests"].append(current_test)
            session_info["total_duration_s"] += dur
            current_test = None
            continue

        # 9. Test session finished
        m_sess = SESSION_FINISH_RE.match(msg)
        if m_sess:
            session_info["passed"] = int(m_sess.group("passed"))
            session_info["failed"] = int(m_sess.group("failed"))
            session_info["skipped"] = int(m_sess.group("skipped"))
            session_info["error"] = int(m_sess.group("error"))
            continue

        # Collect test step log lines
        if current_test is not None:
            current_test["logs"].append(f"[{ts}] [{level}] {msg}")

    if current_test is not None:
        session_info["tests"].append(current_test)

    # Recompute counts from test list if needed
    tests_list = session_info["tests"]
    if tests_list:
        passed_cnt = sum(1 for t in tests_list if t["outcome"] == "passed")
        failed_cnt = sum(1 for t in tests_list if t["outcome"] not in ("passed", "skipped"))
        skipped_cnt = sum(1 for t in tests_list if t["outcome"] == "skipped")
        session_info["passed"] = passed_cnt
        session_info["failed"] = failed_cnt
        session_info["skipped"] = skipped_cnt

    return session_info


def _collect_run_history(current_log_path: Path, current_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Collect run history across `logs/<YYYYMMDD_HHMMSS>/suite.log` directories (up to 15 recent runs)."""
    history: List[Dict[str, Any]] = []
    logs_root = current_log_path.resolve().parent.parent

    if logs_root.exists() and logs_root.name == "logs":
        run_dirs = sorted(
            [d for d in logs_root.iterdir() if d.is_dir() and (d / "suite.log").exists()],
            key=lambda p: p.name,
            reverse=True,
        )[:15]
        for rdir in run_dirs:
            s_log = rdir / "suite.log"
            data = current_data if s_log.resolve() == current_log_path.resolve() else parse_suite_log(s_log)
            total = len(data["tests"])
            passed = data["passed"]
            failed = data["failed"]
            result = "PASSED" if (total > 0 and failed == 0) else ("FAILED" if failed > 0 else "EMPTY")
            history.append({
                "run_id": rdir.name,
                "start_time": data["start_time"] or rdir.name,
                "platform_device": f"{data['platform']} / {data['device_name']}",
                "passed": passed,
                "failed": failed,
                "total": total,
                "result": result,
                "duration_s": data["total_duration_s"],
                "is_current": s_log.resolve() == current_log_path.resolve(),
            })

    if not history:
        total = len(current_data["tests"])
        failed = current_data["failed"]
        history.append({
            "run_id": current_log_path.parent.name,
            "start_time": current_data["start_time"] or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "platform_device": f"{current_data['platform']} / {current_data['device_name']}",
            "passed": current_data["passed"],
            "failed": failed,
            "total": total,
            "result": "PASSED" if (total > 0 and failed == 0) else "FAILED",
            "duration_s": current_data["total_duration_s"],
            "is_current": True,
        })

    return history


def generate_html_report(log_path: Path, output_path: Path) -> Path:
    """Parse `suite.log` and write standalone `report.html` with interactive Video Side-Panel."""
    log_path = Path(log_path).resolve()
    output_path = Path(output_path).resolve()
    report_dir = output_path.parent
    report_dir.mkdir(parents=True, exist_ok=True)

    data = parse_suite_log(log_path)
    history = _collect_run_history(log_path, data)

    total_tests = len(data["tests"])
    passed_tests = data["passed"]
    failed_tests = data["failed"]
    total_dur = data["total_duration_s"]
    pass_pct = (passed_tests / total_tests * 100.0) if total_tests > 0 else 0.0
    fail_pct = (failed_tests / total_tests * 100.0) if total_tests > 0 else 0.0

    # Build Run History rows
    history_rows_html = []
    for h in history:
        badge_cls = "badge-pass" if h["result"] == "PASSED" else "badge-fail"
        row_cls = "current-run-row" if h["is_current"] else ""
        history_rows_html.append(f"""
        <tr class="{row_cls}">
            <td><code>{html.escape(str(h['start_time']))}</code></td>
            <td>{html.escape(h['platform_device'])}</td>
            <td><span class="text-pass">{h['passed']} Pass</span> / <span class="text-fail">{h['failed']} Fail</span> ({h['total']})</td>
            <td><span class="badge {badge_cls}">{h['result']}</span></td>
            <td>{h['duration_s']:.2f}s</td>
        </tr>
        """)

    # Build Latest Test Details (<details><summary>)
    test_details_html = []
    for idx, t in enumerate(data["tests"], start=1):
        is_pass = t["outcome"] == "passed"
        status_label = "PASSED" if is_pass else ("SKIPPED" if t["outcome"] == "skipped" else "FAILED")
        badge_cls = "badge-pass" if is_pass else "badge-fail"

        video_rel = _to_relative_href(t.get("video"), report_dir)
        shot_rel = _to_relative_href(t.get("screenshot"), report_dir)
        ps_rel = _to_relative_href(t.get("page_source"), report_dir)

        links_html = []
        if shot_rel:
            links_html.append(
                f'<a class="artifact-btn" href="{html.escape(shot_rel)}" target="_blank" rel="noopener">Screenshot</a>'
            )
        if ps_rel:
            links_html.append(
                f'<a class="artifact-btn" href="{html.escape(ps_rel)}" target="_blank" rel="noopener">Page source XML</a>'
            )
        if video_rel:
            safe_title = html.escape(t["name"], quote=True)
            safe_src = html.escape(video_rel, quote=True)
            links_html.append(
                f'<button type="button" class="artifact-btn video-btn" '
                f'onclick="openVideoPanel(\'{safe_src}\', \'{safe_title}\')">Video</button>'
            )

        links_bar = (
            f'<div class="artifact-links">{"".join(links_html)}</div>'
            if links_html
            else '<div class="artifact-links"><span class="muted">No media artifacts recorded</span></div>'
        )

        error_block = ""
        if t.get("error"):
            error_block = f"""
            <div class="error-box">
                <div class="error-title">Error Captured:</div>
                <pre>{html.escape(t['error'])}</pre>
            </div>
            """

        logs_block = ""
        if t.get("logs"):
            joined_logs = "\n".join(t["logs"])
            logs_block = f"""
            <details class="step-logs">
                <summary>Execution Log ({len(t['logs'])} lines)</summary>
                <pre>{html.escape(joined_logs)}</pre>
            </details>
            """

        open_attr = "open" if not is_pass else ""
        test_details_html.append(f"""
        <details class="test-card {'card-fail' if not is_pass else 'card-pass'}" {open_attr}>
            <summary class="test-summary">
                <div class="summary-left">
                    <span class="badge {badge_cls}">{status_label}</span>
                    <span class="test-name">{html.escape(t['name'])}</span>
                    <span class="test-module">({html.escape(t['module'])})</span>
                </div>
                <div class="summary-right">
                    <span class="test-duration">{t['duration_s']:.2f}s</span>
                </div>
            </summary>
            <div class="test-body">
                {error_block}
                {links_bar}
                {logs_block}
            </div>
        </details>
        """)

    if not test_details_html:
        test_details_html.append('<p class="muted">No test executions found in suite.log.</p>')

    html_doc = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Android Automation Test Report — {html.escape(report_dir.name)}</title>
    <style>
        :root[data-theme="dark"] {{
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #263449;
            --border: #334155;
            --text: #f8fafc;
            --muted: #94a3b8;
            --pass: #22c55e;
            --pass-bg: rgba(34, 197, 94, 0.15);
            --fail: #ef4444;
            --fail-bg: rgba(239, 68, 68, 0.15);
            --accent: #38bdf8;
            --code-bg: #0b1120;
        }}
        :root[data-theme="light"] {{
            --bg: #f8fafc;
            --surface: #ffffff;
            --surface-hover: #f1f5f9;
            --border: #e2e8f0;
            --text: #0f172a;
            --muted: #64748b;
            --pass: #16a34a;
            --pass-bg: rgba(22, 163, 74, 0.12);
            --fail: #dc2626;
            --fail-bg: rgba(220, 38, 38, 0.12);
            --accent: #0284c7;
            --code-bg: #f1f5f9;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
        }}
        .layout-wrapper {{
            display: flex;
            min-height: 100vh;
        }}
        .main-content {{
            flex: 1;
            max-width: 1200px;
            margin: 0 auto;
            padding: 28px 24px 64px;
            transition: margin-right 0.25s ease;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }}
        .title-group h1 {{
            margin: 0;
            font-size: 1.5rem;
        }}
        .title-group p {{
            margin: 4px 0 0;
            color: var(--muted);
            font-size: 0.9rem;
        }}
        .theme-btn {{
            background: var(--surface);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 14px;
            cursor: pointer;
            font-weight: 600;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }}
        .stat-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px 20px;
        }}
        .stat-label {{
            color: var(--muted);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            margin-top: 4px;
        }}
        .text-pass {{ color: var(--pass); }}
        .text-fail {{ color: var(--fail); }}
        .status-bar {{
            height: 10px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 999px;
            overflow: hidden;
            display: flex;
            margin-bottom: 32px;
        }}
        .status-bar-pass {{ background: var(--pass); height: 100%; }}
        .status-bar-fail {{ background: var(--fail); height: 100%; }}
        section {{ margin-bottom: 36px; }}
        section h2 {{
            font-size: 1.15rem;
            margin-bottom: 12px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}
        th, td {{
            text-align: left;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            font-size: 0.92rem;
        }}
        th {{
            color: var(--muted);
            font-weight: 600;
            background: rgba(0, 0, 0, 0.08);
        }}
        .current-run-row {{
            outline: 1px solid var(--accent);
        }}
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.03em;
        }}
        .badge-pass {{
            background: var(--pass-bg);
            color: var(--pass);
            border: 1px solid var(--pass);
        }}
        .badge-fail {{
            background: var(--fail-bg);
            color: var(--fail);
            border: 1px solid var(--fail);
        }}
        .test-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-bottom: 12px;
            overflow: hidden;
        }}
        .test-summary {{
            padding: 14px 18px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        }}
        .test-summary:hover {{
            background: var(--surface-hover);
        }}
        .summary-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .test-name {{
            font-weight: 600;
            font-size: 0.98rem;
        }}
        .test-module, .test-duration, .muted {{
            color: var(--muted);
            font-size: 0.88rem;
        }}
        .test-body {{
            padding: 14px 18px 18px;
            border-top: 1px solid var(--border);
        }}
        .error-box {{
            background: var(--fail-bg);
            border-left: 4px solid var(--fail);
            padding: 12px 14px;
            border-radius: 6px;
            margin-bottom: 14px;
        }}
        .error-title {{
            font-weight: 700;
            color: var(--fail);
            margin-bottom: 6px;
        }}
        .error-box pre, .step-logs pre {{
            margin: 0;
            white-space: pre-wrap;
            word-break: break-word;
            font-family: Consolas, Monaco, monospace;
            font-size: 0.84rem;
        }}
        .step-logs {{
            margin-top: 12px;
            background: var(--code-bg);
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid var(--border);
        }}
        .step-logs summary {{
            cursor: pointer;
            color: var(--muted);
            font-size: 0.85rem;
            margin-bottom: 6px;
        }}
        .artifact-links {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .artifact-btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: var(--code-bg);
            color: var(--accent);
            text-decoration: none;
            font-size: 0.86rem;
            font-weight: 600;
            cursor: pointer;
        }}
        .artifact-btn:hover {{
            border-color: var(--accent);
        }}
        /* Side-panel Video Player */
        .video-side-panel {{
            position: fixed;
            top: 0;
            right: -460px;
            width: 440px;
            max-width: 92vw;
            height: 100vh;
            background: var(--surface);
            border-left: 1px solid var(--border);
            box-shadow: -8px 0 24px rgba(0, 0, 0, 0.4);
            padding: 20px;
            display: flex;
            flex-direction: column;
            transition: right 0.25s ease;
            z-index: 1000;
        }}
        .video-side-panel.open {{
            right: 0;
        }}
        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 16px;
        }}
        .panel-title {{
            font-weight: 700;
            font-size: 0.98rem;
            word-break: break-all;
        }}
        .close-panel-btn {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text);
            border-radius: 6px;
            padding: 4px 10px;
            cursor: pointer;
        }}
        .video-side-panel video {{
            width: 100%;
            max-height: 78vh;
            border-radius: 10px;
            background: #000;
        }}
    </style>
</head>
<body>
    <div class="layout-wrapper">
        <div class="main-content">
            <header>
                <div class="title-group">
                    <h1>Android Automation Test Report</h1>
                    <p>Session: <code>{html.escape(report_dir.name)}</code> &bull; Target: <code>{html.escape(data['platform'])} / {html.escape(data['device_name'])}</code> &bull; Appium: <code>v{html.escape(data['appium_version'])}</code></p>
                </div>
                <button class="theme-btn" onclick="toggleTheme()">Light / Dark</button>
            </header>

            <!-- Summary Grid -->
            <div class="summary-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Tests</div>
                    <div class="stat-value">{total_tests}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Passed</div>
                    <div class="stat-value text-pass">{passed_tests}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Failed</div>
                    <div class="stat-value text-fail">{failed_tests}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Duration</div>
                    <div class="stat-value">{total_dur:.2f}s</div>
                </div>
            </div>

            <div class="status-bar" title="Passed: {pass_pct:.1f}% | Failed: {fail_pct:.1f}%">
                <div class="status-bar-pass" style="width: {pass_pct:.2f}%"></div>
                <div class="status-bar-fail" style="width: {fail_pct:.2f}%"></div>
            </div>

            <!-- Run History Table -->
            <section>
                <h2>Run History Table</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Start Time</th>
                            <th>Platform / Device</th>
                            <th>Pass / Fail</th>
                            <th>Result</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(history_rows_html)}
                    </tbody>
                </table>
            </section>

            <!-- Latest Test Details -->
            <section>
                <h2>Latest Test Details</h2>
                {"".join(test_details_html)}
            </section>
        </div>

        <!-- Interactive Side-Panel for Video Playback -->
        <aside id="videoSidePanel" class="video-side-panel">
            <div class="panel-header">
                <div id="videoPanelTitle" class="panel-title">Test Recording</div>
                <button class="close-panel-btn" onclick="closeVideoPanel()">✕ Close</button>
            </div>
            <video id="sidePanelVideoPlayer" controls preload="metadata"></video>
        </aside>
    </div>

    <script>
        function toggleTheme() {{
            const root = document.documentElement;
            const current = root.getAttribute("data-theme") || "dark";
            root.setAttribute("data-theme", current === "dark" ? "light" : "dark");
        }}

        function openVideoPanel(videoSrc, testName) {{
            const panel = document.getElementById("videoSidePanel");
            const player = document.getElementById("sidePanelVideoPlayer");
            const title = document.getElementById("videoPanelTitle");
            title.textContent = "Video: " + testName;
            player.src = videoSrc;
            panel.classList.add("open");
            player.play().catch(() => {{}});
        }}

        function closeVideoPanel() {{
            const panel = document.getElementById("videoSidePanel");
            const player = document.getElementById("sidePanelVideoPlayer");
            player.pause();
            player.removeAttribute("src");
            panel.classList.remove("open");
        }}
    </script>
</body>
</html>
"""
    output_path.write_text(html_doc, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate standalone HTML report from structured suite.log")
    parser.add_argument("--log", required=True, help="Path to logs/<run_stamp>/suite.log")
    parser.add_argument("--output", required=True, help="Path to output logs/<run_stamp>/report.html")
    args = parser.parse_args()

    out = generate_html_report(Path(args.log), Path(args.output))
    print(f"Report generated at {out}")


if __name__ == "__main__":
    main()

