"""
测试套件：Portal 首页
"""
import pytest
from playwright.sync_api import Page

from pages.portal_home_page import PortalHomePage
from utils.logger import get_logger
from utils.helpers import take_screenshot

log = get_logger(__name__)


class TestPortalHome:
    """Portal 首页功能测试_验证portal首页能够打开"""

    def test_open_homepage(self, page: Page):
        """
        用例 TC-001: 打开 Portal 首页
        步骤:
            1. 访问 https://test.portal.fastreat.com
            2. 等待页面加载完成
        断言:
            - 当前 URL 包含 fastreat.com
            - 页面 title 不为空
        """
        log.info("TC-001 | 打开 Portal 首页")

        home = PortalHomePage(page)
        home.open()

        # 断言 1：URL 正确
        assert home.is_loaded(), f"页面加载失败，当前 URL: {home.url}"

        # 断言 2：title 不为空
        title = home.title
        log.info(f"页面 title: {title!r}")
        assert title, "页面 title 为空，可能未正常渲染"

        # 截图留档
        take_screenshot(page, name="TC001_homepage")
        log.info("TC-001 | 测试通过 ✅")

    def test_login(self, page: Page):
        """
        用例 TC-002: 登录 Portal
        步骤:
            1. 访问 https://test.portal.fastreat.com
            2. 点击 Sign in 进入登录页
            3. 输入邮箱 ray123@gmail.com 和密码 12345678
            4. 提交登录
        断言:
            - 登录成功，页面出现用户头像或用户标识元素
        """
        log.info("TC-002 | 登录 Portal")

        home = PortalHomePage(page)
        home.open()
        log.info("已打开首页，准备点击 Sign in")
        home.click_sign_in()
        log.info("已进入登录页，输入账号密码")
        home.login("ray123@gmail.com", "12345678")
        log.info("已提交登录表单，等待登录结果")

        # 断言：登录成功
        assert home.is_login_success(), "登录失败，未检测到用户头像或标识元素"

        # 截图留档
        take_screenshot(page, name="TC002_login")
        log.info("TC-002 | 测试通过 ✅")
