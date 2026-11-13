import json
import urllib.parse
import urllib.request
import urllib.error
from typing import Any, Dict, Optional

import allure
from config.config import TestConfig
from core.logger import logger
from core.step_tracker import Step


class ApiHelper:
    """
    Helper class for interacting with Eskimo UAT/Stage backend APIs
    (https://stage-api.eskimo.travel) to reset mobile and email accounts for repeatable E2E tests.
    """

    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = (base_url or getattr(TestConfig, "API_BASE_URL", "https://stage-api.eskimo.travel")).rstrip("/")

    @staticmethod
    def _normalize_mobile(mobile_no: str, country_code: str = "84") -> tuple[str, str]:
        """Normalize mobileNo (e.g., '372217263') and countryCode (e.g., '84')."""
        clean_cc = str(country_code).strip().lstrip("+")
        clean_mobile = str(mobile_no).strip().replace(" ", "").replace("-", "")
        if clean_mobile.startswith(f"+{clean_cc}"):
            clean_mobile = clean_mobile[len(clean_cc) + 1 :]
        elif clean_mobile.startswith(clean_cc) and len(clean_mobile) > 9:
            clean_mobile = clean_mobile[len(clean_cc) :]
        if clean_mobile.startswith("0") and len(clean_mobile) >= 10:
            clean_mobile = clean_mobile.lstrip("0")
        return clean_mobile, clean_cc

    def reset_mobile_account(
        self,
        mobile_no: str = TestConfig.SIGNUP_TEST_MOBILE,
        country_code: str = TestConfig.COUNTRY_CODE,
        assert_success: bool = False,
    ) -> Dict[str, Any]:
        """
        Call GET /api/v2.0/Customer/reset-mobile-account?mobileNo=<mobileNo>&countryCode=<countryCode>
        to reset a mobile account on Eskimo Stage/UAT so the phone number can be reused for Sign Up.
        """
        clean_mobile, clean_cc = self._normalize_mobile(mobile_no, country_code)
        query = urllib.parse.urlencode({"mobileNo": clean_mobile, "countryCode": clean_cc})
        url = f"{self.base_url}/api/v2.0/Customer/reset-mobile-account?{query}"

        with allure.step(f"API Reset Mobile Account: +{clean_cc}{clean_mobile}"), Step(
            f"API Reset Mobile Account: +{clean_cc}{clean_mobile}"
        ):
            logger.info(
                "Calling reset-mobile-account API",
                kv={"mobileNo": clean_mobile, "countryCode": clean_cc, "url": url},
            )
            req = urllib.request.Request(url, method="GET", headers={"accept": "*/*"})
            try:
                with urllib.request.urlopen(req, timeout=20) as response:
                    status_code = response.getcode()
                    raw_body = response.read().decode("utf-8", errors="replace")
                    try:
                        data = json.loads(raw_body) if raw_body else {}
                    except json.JSONDecodeError:
                        data = {"raw": raw_body}

                    logger.info(
                        "Reset mobile account API response",
                        kv={
                            "status": status_code,
                            "mobileNo": clean_mobile,
                            "countryCode": clean_cc,
                            "isSuccess": data.get("isSuccess"),
                            "detail": data.get("detail"),
                        },
                    )
                    if assert_success:
                        assert status_code == 200, f"Expected HTTP 200 from reset-mobile-account, got {status_code}"
                    return {"status_code": status_code, **data}
            except urllib.error.HTTPError as http_err:
                err_body = ""
                try:
                    err_body = http_err.read().decode("utf-8", errors="replace")
                except Exception:
                    pass
                logger.warning(
                    "Reset mobile account API returned HTTP error (account may not exist yet)",
                    kv={"status": http_err.code, "mobileNo": clean_mobile, "body": err_body},
                )
                if assert_success:
                    raise AssertionError(
                        f"reset-mobile-account failed with HTTP {http_err.code}: {err_body}"
                    ) from http_err
                return {"status_code": http_err.code, "isSuccess": False, "detail": err_body}
            except Exception as exc:
                logger.warning(
                    "Reset mobile account API request failed",
                    kv={"mobileNo": clean_mobile, "error": str(exc)},
                )
                if assert_success:
                    raise
                return {"status_code": 0, "isSuccess": False, "detail": str(exc)}

    def reset_email_account(
        self,
        email: str = TestConfig.SIGNUP_TEST_EMAIL,
        assert_success: bool = False,
    ) -> Dict[str, Any]:
        """
        Call GET /api/v2.0/Customer/reset-email-account?email=<email>
        to reset an email account on Eskimo Stage/UAT so the email can be reused for Sign Up.
        """
        clean_email = str(email).strip()
        query = urllib.parse.urlencode({"email": clean_email})
        url = f"{self.base_url}/api/v2.0/Customer/reset-email-account?{query}"

        with allure.step(f"API Reset Email Account: {clean_email}"), Step(
            f"API Reset Email Account: {clean_email}"
        ):
            logger.info("Calling reset-email-account API", kv={"email": clean_email, "url": url})
            req = urllib.request.Request(url, method="GET", headers={"accept": "*/*"})
            try:
                with urllib.request.urlopen(req, timeout=20) as response:
                    status_code = response.getcode()
                    raw_body = response.read().decode("utf-8", errors="replace")
                    try:
                        data = json.loads(raw_body) if raw_body else {}
                    except json.JSONDecodeError:
                        data = {"raw": raw_body}

                    logger.info(
                        "Reset email account API response",
                        kv={
                            "status": status_code,
                            "email": clean_email,
                            "isSuccess": data.get("isSuccess"),
                            "detail": data.get("detail"),
                        },
                    )
                    if assert_success:
                        assert status_code == 200, f"Expected HTTP 200 from reset-email-account, got {status_code}"
                    return {"status_code": status_code, **data}
            except urllib.error.HTTPError as http_err:
                err_body = ""
                try:
                    err_body = http_err.read().decode("utf-8", errors="replace")
                except Exception:
                    pass
                logger.warning(
                    "Reset email account API returned HTTP error (account may not exist yet)",
                    kv={"status": http_err.code, "email": clean_email, "body": err_body},
                )
                if assert_success:
                    raise AssertionError(
                        f"reset-email-account failed with HTTP {http_err.code}: {err_body}"
                    ) from http_err
                return {"status_code": http_err.code, "isSuccess": False, "detail": err_body}
            except Exception as exc:
                logger.warning(
                    "Reset email account API request failed",
                    kv={"email": clean_email, "error": str(exc)},
                )
                if assert_success:
                    raise
                return {"status_code": 0, "isSuccess": False, "detail": str(exc)}

