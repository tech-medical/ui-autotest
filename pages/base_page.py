"""
Page Object Base：所有 Page Object 的基类
"""
import time
from playwright.sync_api import Page

from utils.logger import get_logger


class BasePage:
    """
    所有页面对象的基类，封装常用操作并注入日志
    """

    # 页面空白重试相关配置
    _BLANK_RETRY_COUNT = 3       # 空白页重试次数
    _BLANK_RETRY_INTERVAL = 3    # 重试间隔(秒)
    _BLANK_CHECK_SELECTOR = "body"  # 空白页检测的选择器

    def __init__(self, page: Page):
        self._page = page
        self._log = get_logger(self.__class__.__name__)

    # ── 导航 ──────────────────────────────────
    def navigate(self, url: str, retry_on_blank: bool = True) -> None:
        """
        跳转到指定 URL，自动检测并重试空白页

        Args:
            url: 目标 URL
            retry_on_blank: 是否在页面空白时自动重试（默认 True）
        """
        self._log.info(f"导航至: {url}")

        for attempt in range(1, self._BLANK_RETRY_COUNT + 1):
            try:
                self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                self._log.warning(f"第 {attempt} 次 goto 异常: {e}")
                if attempt == self._BLANK_RETRY_COUNT:
                    raise
                time.sleep(self._BLANK_RETRY_INTERVAL)
                continue

            # 等待 JS 执行 & SPA 渲染
            self._page.wait_for_timeout(2000)

            # 检测页面是否空白
            if not retry_on_blank:
                self._log.info(f"页面加载完成，当前 URL: {self._page.url}")
                return

            if self._is_page_blank():
                self._log.warning(
                    f"第 {attempt} 次导航后页面空白，"
                    f"{'重试中...' if attempt < self._BLANK_RETRY_COUNT else '已达最大重试次数'}"
                )
                if attempt < self._BLANK_RETRY_COUNT:
                    time.sleep(self._BLANK_RETRY_INTERVAL)
                    continue
            else:
                self._log.info(f"页面加载完成，当前 URL: {self._page.url}")
                return

        self._log.warning(f"经过 {self._BLANK_RETRY_COUNT} 次重试，页面仍可能空白")
        self._log.info(f"当前 URL: {self._page.url}")

    def _is_page_blank(self) -> bool:
        """
        检测页面是否为空白

        判断逻辑：
          1. body 内无可见文本内容（去空白后长度 < 10）
          2. 或 body 内子元素数量极少（< 3）
        """
        try:
            body = self._page.locator("body")
            if body.count() == 0:
                return True

            # 检查 body 内文本内容
            inner_text = body.inner_text(timeout=3000).strip()
            if len(inner_text) < 10:
                self._log.debug(f"页面文本内容过少({len(inner_text)}字符)，判定为空白")
                return True

            # 检查 body 直接子元素数量
            child_count = self._page.evaluate(
                "() => document.body ? document.body.children.length : 0"
            )
            if child_count < 2:
                self._log.debug(f"body 子元素过少({child_count}个)，判定为空白")
                return True

            return False
        except Exception as e:
            self._log.debug(f"空白页检测异常: {e}，保守判定为空白")
            return True

    # ── 基础交互 ──────────────────────────────
    def click(self, selector: str, description: str = "") -> None:
        desc = description or selector
        self._log.info(f"点击: {desc}")
        self._page.click(selector)

    def fill(self, selector: str, value: str, description: str = "") -> None:
        desc = description or selector
        self._log.info(f"输入 [{desc}]: {value}")
        self._page.fill(selector, value)

    def get_text(self, selector: str) -> str:
        text = self._page.inner_text(selector)
        self._log.debug(f"获取文本 [{selector}]: {text!r}")
        return text

    # ── 等待 ──────────────────────────────────
    def wait_for_selector(self, selector: str, timeout: int = 10000) -> None:
        self._log.debug(f"等待元素可见: {selector}")
        self._page.wait_for_selector(selector, timeout=timeout)

    # ── 属性 ──────────────────────────────────
    @property
    def title(self) -> str:
        return self._page.title()

    @property
    def url(self) -> str:
        return self._page.url
