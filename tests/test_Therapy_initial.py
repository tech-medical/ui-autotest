"""
测试套件：Therapy Initial Session 流程
"""
import pytest
from playwright.sync_api import Page

from pages.portal_home_page import PortalHomePage
from utils.logger import get_logger
from utils.helpers import take_screenshot

log = get_logger(__name__)


class TestTherapyInitial:
    """Therapy Initial 预约测试"""

    def test_therapy_initial_flow(self, page: Page):
        """
        用例 TC-005: 登录后预约 Therapy Initial Session
        步骤:
            1. 登录成功
            2. 点击 Therapy 按钮
            3. 点击 Book Your I initial Session 按钮
            4. 点击任意 AM 或 PM 时间按钮
            5. 断言页面存在 "Confirm"
            6. 验证指定元素文本为 $89
            7. 断言页面存在 "Therapy Initial Session"
        """
        log.info("TC-005 | 开始预约 Therapy Initial Session 流程")

        home = PortalHomePage(page)
        home.open()
        home.click_sign_in()
        home.login("marry999@gmail.com", "12345678")

        # ── Step 2: 点击 Therapy 按钮 ──
        log.info("查找 Therapy 按钮...")
        therapy_btn = page.locator('button:has-text("Therapy")')
        therapy_btn.wait_for(state="visible", timeout=15000)
        therapy_btn.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        log.info(f"点击 Therapy 后 URL: {page.url}")

        # ── Step 3: 点击 Book Your I initial Session 按钮 ──
        log.info("查找 Book Your I initial Session 按钮...")
        log.info(f"Step3 前 URL: {page.url}")

        # 兼容文案差异（避免因按钮文案轻微变化导致定位失败）
        session_btn = page.locator('button:has-text("Book Your I initial Session")')
        if session_btn.count() == 0:
            session_btn = page.locator('button:has-text("Book Your Initial Session")')
        if session_btn.count() == 0:
            session_btn = page.locator('button:has-text("Initial Session")')
        if session_btn.count() == 0:
            session_btn = page.locator("text=/Book\\s+Your.*Initial\\s+Session/i").first

        session_btn.wait_for(state="visible", timeout=15000)
        try:
            session_btn.click(force=False, timeout=5000)
        except Exception:
            log.warning("Book Your Initial Session 按钮不可用，尝试强制点击")
            session_btn.click(force=True)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        log.info(f"点击 Book Your Initial Session 后 URL: {page.url}")

        # ── Step 4: 点击任意 AM 或 PM 时间按钮 ──
        log.info("查找 AM/PM 时间按钮...")
        am_pm_btn = page.locator(
            'button:has-text("AM"), button:has-text("PM"), button:has-text("am"), button:has-text("pm")'
        ).first
        if am_pm_btn.count() == 0:
            am_pm_btn = page.locator("text=/\\b(AM|PM|am|pm)\\b/").first

        am_pm_btn.wait_for(state="visible", timeout=10000)
        selected_time = am_pm_btn.inner_text()
        log.info(f"点击时间按钮: {selected_time}")
        am_pm_btn.click()
        page.wait_for_timeout(2000)

        # ── Step 5: 断言页面存在 "Confirm" ──
        body_text = page.inner_text("body")
        assert "Confirm" in body_text, "页面未包含 'Confirm' 文本"
        log.info("断言通过：页面包含 'Confirm'")

        # ── Step 6: 验证指定元素文本为 $89 ──
        log.info("验证 $89 元素...")
        price_locator = page.locator(
            '//*[@id="app_container"]/div/div/div[1]/div[2]/div[4]/p/span/span'
        )
        price_locator.wait_for(state="visible", timeout=10000)
        price_text = price_locator.inner_text().strip()
        log.info(f"价格元素文本: {price_text}")
        assert "$89" in price_text, f"价格元素文本为 {price_text!r}，期望包含 '$89'"
        log.info("断言通过：价格元素显示 $89")

        # ── Step 7: 断言页面存在 "Therapy Follow-Up Session" ──
        log.info("验证页面包含 'Therapy Initial Session'...")
        body_text = page.inner_text("body")
        assert "Therapy Initial Session" in body_text, (
            "页面未包含 'Therapy Initial Session' 文本"
        )
        log.info("断言通过：页面包含 'Therapy Initial Session'")

        # 截图留档
        take_screenshot(page, name="TC005_therapy_initial")
        log.info("TC-005 | 测试通过 ✅")
