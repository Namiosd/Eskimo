import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
import allure
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from core.step_tracker import Step
from core.logger import logger
from pages.base_page import wait_for_element_with_anr_handling


# ============================================================
# LOCATORS: Home Entry & Bottom Sheet Modal
# ============================================================
HOME_HELP_CARD_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/help_card']"
HOME_HELP_TEXT_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/txt_help']"
HOME_HELP_IMG_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/img_help']"

# Modal: "Ask Eski!"
SHEET_TITLE_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/tvTitle']"
SHEET_SUBTITLE_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/tvSubtitle']"
BTN_CHAT_IN_APP_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/btnChatInApp']"
TXT_IN_APP_CHAT_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/txt_in_app_chat']"
BTN_CHAT_WHATSAPP_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/btnChatWhatsApp']"
TXT_WHATSAPP_CHAT_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/whats_app_chat']"
BTN_HELP_CENTER_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/tvHelpCenter']"
BTN_CLOSE_SHEET_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/btnClose']"

# ============================================================
# LOCATORS: In-App Chat Screen
# ============================================================
BTN_BACK_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/btnBack']"
BTN_REFRESH_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/btnRefresh']"
BTN_CLOSE_CHAT_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/btnCloseChat']"

# Reset Confirmation Dialog
BTN_RESET_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/btn_reset']"
BTN_CLEAR_CANCEL_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/btn_clear']"

# Chat Body & Messages
RV_CHAT_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/rvChat']"
USER_NAME_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/user_name']"
ESKI_INTRO_NAME_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/eski_intro_name']"
ESKI_INTRO_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/eski_intro']"
ESKI_MASCOT_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/ivMascot']"
TXT_HOW_TO_HELP_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/txt_hot_to_help']"

# Default Suggestion Chips
CHIP_1_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/chip1']"
CHIP_2_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/chip2']"
CHIP_3_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/chip3']"
CHIP_4_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/chip4']"

# Input Area
ET_INPUT_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/etInput']"
BTN_PLUS_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/btnPlus']"
BTN_ASK_ESKI_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/btnAskEski'] | //*[@resource-id='travel.eskimo.esim.uat:id/txt_ask_eski_btn']"
TXT_ASK_ESKI_BTN_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/txt_ask_eski_btn']"
TV_WHATSAPP_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/tvWhatsApp']"

# Dynamic Message Elements
TV_USER_MESSAGE_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/tvMessage']"
TV_BOT_BODY_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/tvBotBody']"
IMG_SENDING_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/imgSending']"
TXT_ERROR_MSG_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/txt_error_msg']"
TV_RETRY_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/tvRetry']"

# Plan Recommendations
RV_PLANS_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/rvPlans']"
TV_PRICE_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/tvPrice']"
TV_OLD_PRICE_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/tvOldPrice']"

# Suggestion Chips under Bot Message
LL_SUGGESTIONS_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/llSuggestions']"
DYNAMIC_SUGGESTION_CHIPS_XPATH = "//*[@resource-id='travel.eskimo.esim.uat:id/llSuggestions']//android.widget.TextView"


# ============================================================
# HELPER FUNCTIONS & SESSION RECOVERY
# ============================================================

LOGOUT_INDICATOR_XPATH = (
    "//*[@resource-id='travel.eskimo.esim.uat:id/btn_claim_offer'] | "
    "//*[@resource-id='travel.eskimo.esim.uat:id/tv_explore_plans'] | "
    "//*[@resource-id='travel.eskimo.esim.uat:id/txt_login'] | "
    "//*[@resource-id='travel.eskimo.esim.uat:id/lbl_sign_up'] | "
    "//android.widget.TextView[@text='Continue with Mobile Number'] | "
    "//android.widget.TextView[@text='Welcome back']"
)


def is_logged_out(driver: webdriver.Remote) -> bool:
    """Detect if the user session was logged out or redirected to Welcome/Sign up gate (e.g. 401 Unauthorized)."""
    try:
        activity = getattr(driver, "current_activity", "") or ""
        if any(act in activity for act in ["NewIntroActivity", "PreLoaderActivity"]):
            return True
    except Exception:
        pass

    try:
        elements = driver.find_elements(AppiumBy.XPATH, LOGOUT_INDICATOR_XPATH)
        if any(e.is_displayed() for e in elements):
            return True
    except Exception:
        pass

    return False


def recover_session_if_logged_out(driver: webdriver.Remote) -> bool:
    """
    Check if the app is in logged-out state (e.g. after HTTP 401 session expiration).
    If logged out, automatically perform login sequence to re-authenticate.
    Returns True if recovery was performed, False if session was already active.
    """
    if is_logged_out(driver):
        logger.warning("⚠️ DETECTED LOGGED-OUT STATE (Session expired / HTTP 401)! Automatically recovering session via login()...")
        from pages.login_page import login
        try:
            login(driver)
            logger.info("✅ Session successfully re-authenticated via login().")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to auto-recover session via login(): {e}")
            raise e
    return False


def wait_for_home_loaded(driver: webdriver.Remote, timeout: int = 30) -> None:
    """
    Wait for skeleton loading layout on Home screen to disappear.
    If stuck in shimmer/skeleton, switches tabs to force-refresh the dashboard.
    """
    try:
        skeleton_id = "travel.eskimo.esim.uat:id/skeleton_loading_layout"
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((AppiumBy.ID, skeleton_id))
        )
        logger.info("Skeleton loading detected. Waiting for Home content to load...")
        try:
            WebDriverWait(driver, 15).until_not(
                EC.presence_of_element_located((AppiumBy.ID, skeleton_id))
            )
        except TimeoutException:
            logger.warning("Skeleton shimmer stuck. Switching tabs to force-refresh Home dashboard...")
            try:
                rewards_tab = driver.find_element(AppiumBy.XPATH, "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_cash_back']")
                rewards_tab.click()
                time.sleep(1)
                home_tab = driver.find_element(AppiumBy.XPATH, "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_home']")
                home_tab.click()
                time.sleep(2)
            except Exception:
                pass

        logger.info("Home dashboard content fully loaded.")
        time.sleep(1)
    except Exception:
        pass


def ensure_home_screen(driver: webdriver.Remote) -> None:
    """Ensure app is cleanly at the Home screen dashboard, dismissing any open chat or modal."""
    logger.info("Ensuring app state is at Home screen dashboard...")
    if recover_session_if_logged_out(driver):
        return

    for _ in range(3):
        if is_logged_out(driver):
            recover_session_if_logged_out(driver)
            return

        # 1. Check if inside In-App Chat
        try:
            close_chat = driver.find_element(AppiumBy.XPATH, BTN_CLOSE_CHAT_XPATH)
            if close_chat.is_displayed():
                logger.info("Chat screen open. Closing chat...")
                close_chat.click()
                time.sleep(2)
                continue
        except Exception:
            pass

        # 2. Check if inside Ask Eski Bottom Sheet
        try:
            close_sheet = driver.find_element(AppiumBy.XPATH, BTN_CLOSE_SHEET_XPATH)
            if close_sheet.is_displayed():
                logger.info("Bottom sheet open. Dismissing sheet...")
                close_sheet.click()
                time.sleep(1)
                continue
        except Exception:
            pass

        # 3. Check if Home navigation tab is available
        try:
            home_tab = driver.find_element(AppiumBy.XPATH, "//*[@resource-id='travel.eskimo.esim.uat:id/navigation_home']")
            if home_tab.is_displayed():
                home_tab.click()
                time.sleep(1)
                break
        except Exception:
            try:
                driver.back()
                time.sleep(1)
            except Exception:
                break

    wait_for_home_loaded(driver, timeout=60)


def open_eski_bottom_sheet(driver: webdriver.Remote) -> bool:
    """
    Click the floating pill card on Home.
    If the 'Ask Eski!' bottom sheet modal appears, verifies it and returns True.
    If the app directly navigates to In-App Chat (subsequent opens), returns False.
    """
    ensure_home_screen(driver)

    with allure.step("Verify and click floating prompt card on Home"), Step("Verify and click floating prompt card on Home"):
        help_card = wait_for_element_with_anr_handling(driver, HOME_HELP_CARD_XPATH, timeout=45)
        assert help_card.is_displayed(), "❌ 'I'm new to eSIM' card is not displayed on Home screen!"

        help_text = driver.find_element(AppiumBy.XPATH, HOME_HELP_TEXT_XPATH).text
        logger.info(f"Check UI: Found entry card with rotating text: '{help_text}'")
        assert len(help_text.strip()) > 0, "❌ Entry card text is empty!"

        help_card.click()
        logger.info("Action: Clicked entry card.")
        time.sleep(2)

    # Check which screen appeared: bottom sheet modal or direct in-app chat
    try:
        title_elem = driver.find_element(AppiumBy.XPATH, SHEET_TITLE_XPATH)
        if title_elem.is_displayed():
            with allure.step("Verify 'Ask Eski!' bottom sheet modal layout"), Step("Verify 'Ask Eski!' bottom sheet modal layout"):
                assert "Ask Eski" in title_elem.text, f"Unexpected sheet title: {title_elem.text}"

                chat_in_app = driver.find_element(AppiumBy.XPATH, BTN_CHAT_IN_APP_XPATH)
                assert chat_in_app.is_displayed(), "❌ 'Chat in Eskimo App' option is not displayed!"

                # Optional check for WhatsApp (removed in newer UI versions)
                try:
                    chat_whatsapp = driver.find_element(AppiumBy.XPATH, BTN_CHAT_WHATSAPP_XPATH)
                    if chat_whatsapp.is_displayed():
                        logger.info("Found 'Chat on WhatsApp' option on bottom sheet.")
                except Exception:
                    logger.info("'Chat on WhatsApp' option not present in current UI version.")

                try:
                    help_center = driver.find_element(AppiumBy.XPATH, BTN_HELP_CENTER_XPATH)
                    if help_center.is_displayed():
                        logger.info("Found 'Help Center' option on bottom sheet.")
                except Exception:
                    pass

                logger.info("Verify OK: 'Ask Eski!' bottom sheet modal is displayed.")
                return True
    except Exception as e:
        logger.info(f"Bottom sheet check exception: {e}")

    logger.info("Directly opened In-App Chat (session already active).")
    return False


def open_in_app_chat(driver: webdriver.Remote) -> None:
    """
    Open the In-App Chat screen seamlessly from Home or via 'Ask Eski!' modal.
    """
    # Auto-recover if session expired
    recover_session_if_logged_out(driver)

    # Check if already inside In-App Chat
    try:
        close_btn = driver.find_element(AppiumBy.XPATH, BTN_CLOSE_CHAT_XPATH)
        if close_btn.is_displayed():
            logger.info("Already on In-App Chat screen.")
            return
    except Exception:
        pass

    # Check if bottom sheet is already open
    bottom_sheet_active = False
    try:
        btn_in_app = driver.find_element(AppiumBy.XPATH, BTN_CHAT_IN_APP_XPATH)
        if btn_in_app.is_displayed():
            bottom_sheet_active = True
    except Exception:
        pass

    if not bottom_sheet_active:
        # Otherwise open from Home
        bottom_sheet_active = open_eski_bottom_sheet(driver)

    # Click 'Chat in Eskimo App' if bottom sheet is active
    try:
        btn_in_app = wait_for_element_with_anr_handling(driver, BTN_CHAT_IN_APP_XPATH, timeout=10)
        if btn_in_app.is_displayed():
            with allure.step("Click 'Chat in Eskimo App'"), Step("Click 'Chat in Eskimo App'"):
                btn_in_app.click()
                logger.info("Action: Clicked 'Chat in Eskimo App'.")
                time.sleep(2)
    except Exception as e:
        logger.info(f"Chat in Eskimo App button click skipped (already transitioned): {e}")

    with allure.step("Verify In-App Chat screen loaded"), Step("Verify In-App Chat screen loaded"):
        close_btn = wait_for_element_with_anr_handling(driver, BTN_CLOSE_CHAT_XPATH, timeout=20)
        assert close_btn.is_displayed(), "❌ Close button on Chat screen not found!"

        et_input = driver.find_element(AppiumBy.XPATH, ET_INPUT_XPATH)
        assert et_input.is_displayed(), "❌ Chat input field (etInput) not displayed!"

        btn_ask = driver.find_element(AppiumBy.XPATH, BTN_ASK_ESKI_XPATH)
        assert btn_ask.is_displayed(), "❌ 'Ask Eski' submit button not displayed!"
        logger.info("Verify OK: In-App Chat screen loaded successfully.")


def reset_chat_history(driver: webdriver.Remote) -> None:
    """Reset the chat history via the header refresh button and confirm dialog."""
    with allure.step("Reset chat conversation history"), Step("Reset chat conversation history"):
        try:
            refresh_btn = wait_for_element_with_anr_handling(driver, BTN_REFRESH_XPATH, timeout=10)
            refresh_btn.click()
            time.sleep(1)

            reset_confirm = wait_for_element_with_anr_handling(driver, "//*[@resource-id='travel.eskimo.esim.uat:id/btn_reset']", timeout=10)
            reset_confirm.click()
            time.sleep(2)
            logger.info("Chat conversation successfully reset to fresh state.")
        except Exception as e:
            logger.warning(f"Could not reset chat history: {e}")


def verify_initial_chat_ui(driver: webdriver.Remote) -> Dict[str, str]:
    """
    Verify the initial greeting, mascot, quick chips, and WhatsApp banner.
    Returns a dictionary of detected initial texts.
    """
    info = {}
    with allure.step("Verify initial Chat UI layout and quick chips"), Step("Verify initial Chat UI layout and quick chips"):
        try:
            user_name_elem = driver.find_element(AppiumBy.XPATH, USER_NAME_XPATH)
            info["user_name"] = user_name_elem.text
            logger.info(f"UI Info: User greeting: {info['user_name']}")
        except Exception:
            pass

        try:
            intro_elem = driver.find_element(AppiumBy.XPATH, ESKI_INTRO_XPATH)
            info["eski_intro"] = intro_elem.text
            logger.info(f"UI Info: Assistant intro: {info['eski_intro']}")
        except Exception:
            pass

        chips = []
        for i in range(1, 5):
            try:
                chip = driver.find_element(AppiumBy.XPATH, f"//*[@resource-id='travel.eskimo.esim.uat:id/chip{i}']")
                if chip.is_displayed():
                    chips.append(chip.text)
            except Exception:
                pass
        info["chips"] = chips
        logger.info(f"UI Info: Quick suggestion chips detected: {chips}")
        assert len(chips) > 0, "❌ No initial suggestion chips found!"

        try:
            whatsapp_btn = driver.find_element(AppiumBy.XPATH, TV_WHATSAPP_XPATH)
            if whatsapp_btn.is_displayed():
                info["whatsapp_text"] = whatsapp_btn.text
                logger.info(f"UI Info: WhatsApp channel footer detected: {whatsapp_btn.text}")
        except Exception:
            logger.info("WhatsApp channel footer not present in current UI version.")

    return info


def ensure_in_app_chat_open(driver: webdriver.Remote) -> None:
    """Ensure the In-App Chat screen is currently open. If not, reopen it immediately."""
    if recover_session_if_logged_out(driver):
        open_in_app_chat(driver)
        return

    try:
        et = driver.find_element(AppiumBy.XPATH, ET_INPUT_XPATH)
        if et.is_displayed():
            return
    except Exception:
        pass
    logger.info("In-App Chat is not currently open. Reopening chat...")
    open_in_app_chat(driver)


def send_chat_message(driver: webdriver.Remote, message: str) -> None:
    """
    Type a message into the input field and click 'Ask Eski'.
    """
    with allure.step(f"Send chat message: '{message}'"), Step(f"Send chat message: '{message}'"):
        et_input = wait_for_element_with_anr_handling(driver, ET_INPUT_XPATH, timeout=15)
        et_input.click()
        time.sleep(1)
        et_input.clear()
        et_input.send_keys(message)
        logger.info(f"Entered chat text: {message}")
        time.sleep(1)

        btn_ask = wait_for_element_with_anr_handling(driver, BTN_ASK_ESKI_XPATH, timeout=15)
        btn_ask.click()
        logger.info("Action: Clicked 'Ask Eski' button.")
        time.sleep(1)

        # Safeguard: if input field still contains the message, re-click submit
        try:
            val = et_input.text
            if val and val.strip() == message.strip():
                logger.info("Text still in input field. Retrying click on 'Ask Eski' button...")
                btn_ask.click()
                time.sleep(1)
        except Exception:
            pass


def click_suggestion_chip(driver: webdriver.Remote, chip_index: int = 2) -> str:
    """
    Click a default suggestion chip (e.g. chip 2: 'How do I install my eSIM?').
    """
    chip_xpath = f"//*[@resource-id='travel.eskimo.esim.uat:id/chip{chip_index}']"
    with allure.step(f"Click suggestion chip #{chip_index}"), Step(f"Click suggestion chip #{chip_index}"):
        chip = wait_for_element_with_anr_handling(driver, chip_xpath, timeout=15)
        chip_text = chip.text
        logger.info(f"Action: Clicking chip #{chip_index}: '{chip_text}'")
        chip.click()
        time.sleep(2)
        return chip_text


def wait_for_ai_response(driver: webdriver.Remote, timeout: int = 40) -> str:
    """
    Wait for AI Assistant (Eski) to generate a response (tvBotBody).
    Handles retry if transient network error occurs ('Message not sent' -> click 'Retry').
    
    Returns:
        The latest bot response text string.
    """
    with allure.step("Wait for AI Agent response"), Step("Wait for AI Agent response"):
        end_time = time.monotonic() + timeout
        last_bot_text = ""

        # Track previous bot message count
        initial_bot_elements = driver.find_elements(AppiumBy.XPATH, TV_BOT_BODY_XPATH)
        initial_count = len(initial_bot_elements)

        logger.info(f"Waiting up to {timeout}s for AI response (currently {initial_count} bot responses)...")

        while time.monotonic() < end_time:
            # Check for error / retry popup
            try:
                error_elem = driver.find_element(AppiumBy.XPATH, TXT_ERROR_MSG_XPATH)
                if error_elem.is_displayed():
                    logger.warning("Detected 'Message not sent' error. Clicking 'Retry'...")
                    retry_btn = driver.find_element(AppiumBy.XPATH, TV_RETRY_XPATH)
                    retry_btn.click()
                    time.sleep(4)
            except Exception:
                pass

            # Check if a new bot response has arrived
            bot_elements = driver.find_elements(AppiumBy.XPATH, TV_BOT_BODY_XPATH)
            if len(bot_elements) > initial_count:
                latest = bot_elements[-1]
                if latest.is_displayed() and len(latest.text.strip()) > 0:
                    last_bot_text = latest.text.strip()
                    logger.info(f"Received AI Response ({len(last_bot_text)} chars):\n{last_bot_text}")
                    return last_bot_text

            time.sleep(3)

        # Fallback: Check if existing bot elements have text
        bot_elements = driver.find_elements(AppiumBy.XPATH, TV_BOT_BODY_XPATH)
        if bot_elements:
            last_bot_text = bot_elements[-1].text.strip()
            if last_bot_text:
                logger.info(f"AI Response retrieved from latest element: {last_bot_text[:100]}...")
                return last_bot_text

        raise TimeoutException(f"Timed out waiting for AI response after {timeout} seconds.")


def get_all_bot_responses(driver: webdriver.Remote) -> List[str]:
    """Retrieve all bot message texts currently present in the chat."""
    elements = driver.find_elements(AppiumBy.XPATH, TV_BOT_BODY_XPATH)
    return [elem.text.strip() for elem in elements if elem.text.strip()]


def get_all_user_messages(driver: webdriver.Remote) -> List[str]:
    """Retrieve all user message texts currently present in the chat."""
    elements = driver.find_elements(AppiumBy.XPATH, TV_USER_MESSAGE_XPATH)
    return [elem.text.strip() for elem in elements if elem.text.strip()]


def get_dynamic_suggestion_chips(driver: webdriver.Remote) -> List[str]:
    """Retrieve text of follow-up suggestion chips presented under AI responses."""
    try:
        chips = driver.find_elements(AppiumBy.XPATH, DYNAMIC_SUGGESTION_CHIPS_XPATH)
        return [c.text.strip() for c in chips if c.text.strip()]
    except Exception:
        return []


def check_plan_recommendation_carousel(driver: webdriver.Remote) -> List[Dict[str, str]]:
    """
    Check if AI has recommended data plans via the plan carousel (rvPlans).
    Returns list of parsed plans with price information.
    """
    plans = []
    try:
        carousel = driver.find_element(AppiumBy.XPATH, RV_PLANS_XPATH)
        if carousel.is_displayed():
            prices = driver.find_elements(AppiumBy.XPATH, TV_PRICE_XPATH)
            old_prices = driver.find_elements(AppiumBy.XPATH, TV_OLD_PRICE_XPATH)
            for i, p in enumerate(prices):
                old = old_prices[i].text if i < len(old_prices) else ""
                plans.append({"price": p.text, "old_price": old})
            logger.info(f"Found {len(plans)} plan recommendations in carousel: {plans}")
    except Exception as e:
        logger.info(f"No plan recommendation carousel detected: {e}")
    return plans


def close_in_app_chat(driver: webdriver.Remote) -> None:
    """Close In-App Chat and verify return to Home dashboard."""
    with allure.step("Close In-App Chat and return to Home"), Step("Close In-App Chat and return to Home"):
        close_btn = wait_for_element_with_anr_handling(driver, BTN_CLOSE_CHAT_XPATH, timeout=15)
        close_btn.click()
        logger.info("Action: Clicked Close button on Chat screen.")
        time.sleep(2)

        wait_for_home_loaded(driver, timeout=60)

        # Verify back on Home
        help_card = wait_for_element_with_anr_handling(driver, HOME_HELP_CARD_XPATH, timeout=45)
        assert help_card.is_displayed(), "❌ Did not return to Home screen after closing chat!"
        logger.info("Verify OK: Successfully returned to Home screen dashboard.")


# ============================================================
# TRANSCRIPT LOGGER & SEQUENTIAL CHAT RUNNER
# ============================================================

try:
    from scripts.html_report_generator import export_html_report, DEFAULT_HTML_PATH
except ImportError:
    try:
        from html_report_generator import export_html_report, DEFAULT_HTML_PATH
    except ImportError:
        export_html_report = None
        DEFAULT_HTML_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "html", "ai_chat_report.html")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(ROOT_DIR, "reports")
TRANSCRIPT_FILE = os.path.join(REPORTS_DIR, "logs", "ai_chat_transcript.md")
HTML_REPORT_FILE = DEFAULT_HTML_PATH


class ChatTranscript:
    """
    Manages exporting of question-and-answer pairs to a Markdown transcript file,
    Allure report attachments, and console logs without resetting conversation state.
    """
    _entries: List[Dict[str, Any]] = []

    @classmethod
    def start_new_session(cls) -> None:
        """Ghi nhận một phiên chạy mới vào file transcript mà KHÔNG xóa lịch sử các lần chạy trước."""
        cls._entries = []
        os.makedirs(os.path.dirname(TRANSCRIPT_FILE), exist_ok=True)
        header_exists = os.path.exists(TRANSCRIPT_FILE) and os.path.getsize(TRANSCRIPT_FILE) > 0
        with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as f:
            if not header_exists:
                f.write("# 📋 SALE AI AGENT — IN-APP CHAT TRANSCRIPT\n\n")
                f.write("> **Ghi chú:** Toàn bộ lịch sử các cuộc hội thoại được lưu giữ liên tục tại đây để đối chiếu.\n\n")

            f.write(f"\n\n{'='*80}\n")
            f.write(f"## 🚀 PHIÊN KIỂM THỬ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
        logger.info(f"Đã bắt đầu phiên ghi nhận transcript mới tại: {TRANSCRIPT_FILE}")

    @classmethod
    def clear(cls) -> None:
        """Alias tương thích ngược."""
        cls.start_new_session()

    @classmethod
    def record(
        cls,
        ac_tag: str,
        query: str,
        response: str,
        plans: Optional[List[Dict[str, str]]] = None,
        chips: Optional[List[str]] = None
    ) -> None:
        """Record a single Q&A exchange to markdown, Allure, and log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {
            "time": timestamp,
            "ac_tag": ac_tag,
            "query": query,
            "response": response,
            "plans": plans or [],
            "chips": chips or []
        }
        cls._entries.append(entry)

        # 1. Append to Markdown file
        with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as f:
            f.write(f"### 🎯 [{ac_tag}] — *{timestamp}*\n\n")
            f.write(f"- 👤 **User Question:**\n")
            f.write(f"  > **\"{query}\"**\n\n")
            f.write(f"- 🤖 **AI Response (Eski):**\n")
            formatted_resp = response.replace("\n", "\n  > ")
            f.write(f"  > {formatted_resp}\n\n")

            if plans:
                f.write(f"- 📦 **Plan Carousel Detected (`rvPlans`):** {len(plans)} gói cước\n")
                for idx, p in enumerate(plans, 1):
                    old_text = f" ~~{p['old_price']}~~" if p.get("old_price") else ""
                    f.write(f"  - **Gói #{idx}:** `{p['price']}`{old_text}\n")
                f.write("\n")

            if chips:
                f.write(f"- 💡 **Follow-up Suggestion Chips:** {', '.join([f'`{c}`' for c in chips])}\n\n")

            f.write("---\n\n")

        # 2. Attach to Allure Report
        try:
            summary_text = (
                f"=== [{ac_tag}] ({timestamp}) ===\n"
                f"QUESTION:\n{query}\n\n"
                f"ANSWER:\n{response}\n"
            )
            if plans:
                summary_text += f"\nCAROUSEL PLANS: {plans}"
            allure.attach(
                summary_text,
                name=f"Chat: {ac_tag}",
                attachment_type=allure.attachment_type.TEXT
            )
        except Exception:
            pass

        # 3. Formatted Console Log
        border = "=" * 70
        logger.info(
            f"\n{border}\n"
            f"💬 [CHAT TRANSCRIPT] [{ac_tag}] at {timestamp}\n"
            f"👤 USER: {query}\n"
            f"🤖 ESKI: {response}\n"
            f"{border}"
        )

        # 4. Auto-update HTML Report
        try:
            cls.export_html_report()
        except Exception as e:
            logger.warning(f"Lỗi khi tự động cập nhật báo cáo HTML: {e}")

    @classmethod
    def export_html_report(cls, output_path: Optional[str] = None) -> str:
        """
        Xuất toàn bộ biên bản hội thoại các phiên kiểm thử ra file HTML trực quan.
        Returns đường dẫn tuyệt đối tới file HTML vừa tạo.
        """
        target = output_path or HTML_REPORT_FILE
        try:
            export_html_report(md_path=TRANSCRIPT_FILE, output_html_path=target)
            logger.info(f"✅ Đã xuất báo cáo HTML trực quan tại: {target}")
            return target
        except Exception as e:
            logger.error(f"❌ Không thể xuất báo cáo HTML: {e}")
            return target



# Session-level tracker of bot responses seen/recorded to prevent picking up previous bubbles
_known_bot_responses = set()


def init_chat_session_state(driver: webdriver.Remote) -> None:
    """Snapshot existing bot texts in chat so they are never treated as new responses."""
    global _known_bot_responses
    _known_bot_responses = set()
    time.sleep(3)  # Wait for chat history to fully populate in RecyclerView
    try:
        existing = driver.find_elements(AppiumBy.XPATH, TV_BOT_BODY_XPATH)
        for e in existing:
            t = e.text.strip()
            if t:
                _known_bot_responses.add(t)
        logger.info(f"Initialized chat session: {len(_known_bot_responses)} existing bot messages recognized and excluded.")
    except Exception as e:
        logger.warning(f"Could not snapshot initial bot messages: {e}")


def ask_and_record(
    driver: webdriver.Remote,
    prompt: str,
    ac_tag: str,
    timeout: int = 120,
    max_retries: int = 1
) -> Dict[str, Any]:
    """
    Send a question into In-App Chat, wait for the corresponding NEW response,
    extract rich elements, and record to transcript.
    """
    global _known_bot_responses

    for attempt in range(max_retries + 1):
        ensure_in_app_chat_open(driver)
        # 1. Snapshot all currently visible bot responses and the last bot text BEFORE sending
        prior_last_text = ""
        try:
            prior_bot_elements = driver.find_elements(AppiumBy.XPATH, TV_BOT_BODY_XPATH)
            prior_texts = set([b.text.strip() for b in prior_bot_elements if b.text.strip()])
            prior_last_text = prior_bot_elements[-1].text.strip() if prior_bot_elements else ""
            for t in prior_texts:
                _known_bot_responses.add(t)
            logger.info(f"[{ac_tag}] Prior bot elements count: {len(prior_bot_elements)}, last text: '{prior_last_text[:60]}...'")
        except Exception:
            pass

        logger.info(f"[{ac_tag}] Sending prompt (attempt {attempt + 1}/{max_retries + 1}): '{prompt}'")

        # 2. Send message
        send_chat_message(driver, prompt)

        # 3. Wait for new bot response
        end_time = time.monotonic() + timeout
        new_bot_text = ""
        logged_out_during_wait = False

        # Pause 3 seconds to allow AI backend to start generating
        time.sleep(3)

        while time.monotonic() < end_time:
            # Check if app unexpectedly got kicked out to login screen (e.g. 401 Unauthorized)
            if is_logged_out(driver):
                logger.error(f"[{ac_tag}] ❌ App was logged out while waiting for AI response (HTTP 401 / session revoked)!")
                logged_out_during_wait = True
                recover_session_if_logged_out(driver)
                open_in_app_chat(driver)
                break

            # Check for 'Message not sent' retry
            try:
                error_elem = driver.find_element(AppiumBy.XPATH, TXT_ERROR_MSG_XPATH)
                if error_elem.is_displayed():
                    logger.warning("Detected 'Message not sent' error. Clicking 'Retry'...")
                    retry_btn = driver.find_element(AppiumBy.XPATH, TV_RETRY_XPATH)
                    retry_btn.click()
                    time.sleep(4)
            except Exception:
                pass

            # Check latest bot message safely
            try:
                bot_elements = driver.find_elements(AppiumBy.XPATH, TV_BOT_BODY_XPATH)
                if bot_elements:
                    latest_elem = bot_elements[-1]
                    latest_text = latest_elem.text.strip()

                    # A response is NEW if:
                    # - non-empty
                    # - different from the last bot message before sending
                    # - not in _known_bot_responses (never seen/recorded in this session)
                    if latest_text and latest_text != prior_last_text and latest_text not in _known_bot_responses:
                        # Stabilize: wait for text streaming to fully complete
                        stable_text = latest_text
                        for _ in range(6):
                            time.sleep(2)
                            refreshed_bots = driver.find_elements(AppiumBy.XPATH, TV_BOT_BODY_XPATH)
                            if refreshed_bots:
                                try:
                                    sample = refreshed_bots[-1].text.strip()
                                    if sample == stable_text and len(sample) > 0:
                                        break
                                    stable_text = sample
                                except Exception:
                                    pass

                        new_bot_text = stable_text
                        _known_bot_responses.add(new_bot_text)
                        logger.info(f"Detected stabilized NEW AI response ({len(new_bot_text)} chars):\n{new_bot_text[:150]}...")
                        break
            except Exception:
                pass

            time.sleep(2)

        if logged_out_during_wait and attempt < max_retries:
            logger.info(f"[{ac_tag}] Session re-established after logout. Retrying prompt on attempt {attempt + 2}...")
            time.sleep(2)
            continue

        # If bot returned server error "something went wrong", retry once
        if new_bot_text and "something went wrong" in new_bot_text.lower() and attempt < max_retries:
            logger.warning(f"AI backend returned temporary error: '{new_bot_text}'. Retrying prompt in 3s...")
            time.sleep(3)
            continue

        if not new_bot_text:
            if attempt == max_retries:
                ChatTranscript.record(
                    ac_tag=ac_tag,
                    query=prompt,
                    response="[TIMEOUT: No new AI response received within timeout period]",
                    plans=[],
                    chips=[]
                )
                raise TimeoutException(f"Timed out waiting for new AI response to prompt '{prompt}' after {timeout}s")
            time.sleep(2)
            continue

        # Extract rich elements
        plans = check_plan_recommendation_carousel(driver)
        chips = get_dynamic_suggestion_chips(driver)

        # Record to transcript
        ChatTranscript.record(
            ac_tag=ac_tag,
            query=prompt,
            response=new_bot_text,
            plans=plans,
            chips=chips
        )

        # Pause briefly between turns
        time.sleep(2)

        return {
            "query": prompt,
            "response": new_bot_text,
            "plans": plans,
            "chips": chips
        }


