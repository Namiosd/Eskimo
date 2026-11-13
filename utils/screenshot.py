import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from utils.logger import get_logger, get_run_log_dir

logger = get_logger("appium_framework.screenshot")


def _sanitize_filename(name: str) -> str:
    """Sanitize test name for safe filesystem usage."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")


def capture_failure_artifacts(
    driver,
    test_name: str,
    platform: str = "android",
    locale: str = "en",
    run_dir: Optional[Path] = None,
) -> Tuple[Optional[Path], Optional[Path]]:
    """
    Best-effort capture of PNG screenshot and XML UI hierarchy on test failure.
    Saves files to:
      - logs/<run_stamp>/screenshots/<test>_<platform>_<locale>_<timestamp>.png
      - logs/<run_stamp>/page_source/<test>_<platform>_<locale>_<timestamp>.xml
    Logs structured events for `generate_report.py`:
      - Screenshot saved | path=<path_png>
      - Page source saved | path=<path_xml>
    """
    if driver is None:
        return None, None

    target_run_dir = Path(run_dir) if run_dir else get_run_log_dir()
    screenshots_dir = target_run_dir / "screenshots"
    page_source_dir = target_run_dir / "page_source"

    try:
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        page_source_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_test = _sanitize_filename(test_name)
    base_name = f"{safe_test}_{platform.lower()}_{locale.lower()}_{ts}"

    screenshot_path: Optional[Path] = None
    page_source_path: Optional[Path] = None

    # 1. Capture Screenshot (PNG)
    try:
        png_bytes = driver.get_screenshot_as_png()
        screenshot_path = screenshots_dir / f"{base_name}.png"
        screenshot_path.write_bytes(png_bytes)
        logger.info("Screenshot saved", kv={"path": str(screenshot_path)})

        # Also update legacy reports/screenshots/debug_failure.png (best-effort)
        try:
            legacy_dir = target_run_dir.parent.parent / "reports" / "screenshots"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            (legacy_dir / "debug_failure.png").write_bytes(png_bytes)
        except Exception:
            pass
    except Exception as exc:
        logger.warning(f"Failed to capture failure screenshot (session may be closed): {exc}")

    # 2. Capture UI Hierarchy Page Source (XML)
    try:
        xml_content = driver.page_source
        page_source_path = page_source_dir / f"{base_name}.xml"
        page_source_path.write_text(xml_content, encoding="utf-8")
        logger.info("Page source saved", kv={"path": str(page_source_path)})

        # Also update legacy reports/screenshots/debug_page_source.xml (best-effort)
        try:
            legacy_dir = target_run_dir.parent.parent / "reports" / "screenshots"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            (legacy_dir / "debug_page_source.xml").write_text(xml_content, encoding="utf-8")
        except Exception:
            pass
    except Exception as exc:
        logger.warning(f"Failed to capture failure page source XML (session may be closed): {exc}")

    return screenshot_path, page_source_path

