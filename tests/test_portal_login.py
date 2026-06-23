"""
测试套件：Portal 登录
"""
import pytest
from playwright.sync_api import Page

from pages.portal_home_page import PortalHomePage
from utils.logger import get_logger
from utils.helpers import take_screenshot

log = get_logger(__name__)


class TestPortalLogin:
    """Portal 登录功能测试"""

    def test_login(self, page: Page):
        """
        用例 TC-002: 登录 Portal
        步骤:
            1. 访问 https://test.portal.fastreat.com
            2. 点击 Sign in 进入登录页
            3. 输入邮箱 emma@gmail.com 和密码 12345678
            4. 点击 Continue 提交
        断言:
            - 跳转到 /appointmented/home
            - 页面出现 "Hi," 问候语
        """
        log.info("TC-002 | 登录 Portal")

        home = PortalHomePage(page)
        home.open()

        # 点击 Sign in 进入登录页
        home.click_sign_in()

        # 输入账号密码并登录
        home.login("emma@gmail.com", "12345678")

        # 断言：登录成功，检测到Hi问候语
        assert home.is_login_success(), "登录失败，未跳转到主页或未检测到用户标识"

        # 截图留档
        take_screenshot(page, name="TC002_login")
        log.info("TC-002 | 测试通过 ✅")
