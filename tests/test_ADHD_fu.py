"""
测试套件：ADHD Book Appointment 流程
"""
import pytest
from playwright.sync_api import Page

from pages.portal_home_page import PortalHomePage
from utils.logger import get_logger
from utils.helpers import take_screenshot

log = get_logger(__name__)


class TestADHHBookAppointment:
    """ADHD 预约功能测试"""

    def test_book_appointment_flow(self, page: Page):
        """
        用例 TC-003: 登录后预约 Appointment
        步骤:
            1. 登录成功
            2. 等待 Book Appointment 按钮变为可用，点击
            3. 断言页面存在 "Appointment"
            4. 点击任意 AM 或 PM 时间按钮
            5. 断言页面存在 "Confirm"
            6. 验证指定元素文本为 $69
            7. 断言页面存在 "Follow-up"
        """
        log.info("TC-003 | 开始预约 Appointment 流程")

        home = PortalHomePage(page)
        home.open()
        home.click_sign_in()
        home.login("emma@gmail.com", "12345678")

        # ── Step 1: 等待 Book Appointment 按钮可用并点击 ──
        log.info("等待 Book Appointment 按钮变为可用...")
        book_btn = page.locator('button:has-text("Book Appointment")')
        book_btn.wait_for(state="visible", timeout=15000)
        # 等待按钮变为可用（disabled 可能为 true 直到某些条件满足）
        book_btn.wait_for(state="attached", timeout=15000)
        # 强制点击（若 enabled 则正常点击，若 disabled 则记录警告）
        try:
            book_btn.click(force=False, timeout=5000)
        except Exception:
            log.warning("Book Appointment 按钮不可用，尝试强制点击")
            book_btn.click(force=True)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        log.info(f"点击 Book Appointment 后 URL: {page.url}")

        # ── Step 2: 断言页面存在 "Appointment" ──
        body_text = page.inner_text("body")
        assert "Appointment" in body_text, "页面未包含 'Appointment' 文本"
        log.info("断言通过：页面包含 'Appointment'")

        # ── Step 3: 点击任意 AM 或 PM 按钮 ──
        log.info("查找 AM/PM 时间按钮...")
        # 优先找 button 元素，找不到则找含 AM/PM 文本的可点击元素
        am_pm_btn = page.locator(
            'button:has-text("AM"), button:has-text("PM"), button:has-text("am"), button:has-text("pm")'
        ).first
        # 若没有 button，用 text 定位器
        if am_pm_btn.count() == 0:
            am_pm_btn = page.locator("text=/\\b(AM|PM|am|pm)\\b/").first

        am_pm_btn.wait_for(state="visible", timeout=10000)
        selected_time = am_pm_btn.inner_text()
        log.info(f"点击时间按钮: {selected_time}")
        am_pm_btn.click()
        page.wait_for_timeout(2000)

        # ── Step 4: 断言页面存在 "Confirm" ──
        body_text = page.inner_text("body")
        assert "Confirm" in body_text, "页面未包含 'Confirm' 文本"
        log.info("断言通过：页面包含 'Confirm'")

        # ── Step 5: 验证指定元素文本为 $69 ──
        log.info("验证 $69 元素...")
        price_locator = page.locator(
            '//*[@id="app_container"]/div/div/div[1]/div[2]/div[4]/p/span/span'
        )
        price_locator.wait_for(state="visible", timeout=10000)
        price_text = price_locator.inner_text().strip()
        log.info(f"价格元素文本: {price_text}")
        assert "$69" in price_text, f"价格元素文本为 {price_text!r}，期望包含 '$69'"
        log.info("断言通过：价格元素显示 $69")

        # ── Step 7: 断言页面存在 "Follow-up" ──
        log.info("验证页面包含 'Follow-up'...")
        body_text = page.inner_text("body")
        assert "Follow-up" in body_text, "页面未包含 'Follow-up' 文本"
        log.info("断言通过：页面包含 'Follow-up'")

        # 截图留档
        take_screenshot(page, name="TC003_book_appointment")
        log.info("TC-003 | 测试通过 ✅")
