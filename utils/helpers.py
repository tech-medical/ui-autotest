"""
工具函数模块：截图辅助等
"""
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page

from config.config import config
from utils.logger import get_logger

log = get_logger(__name__)


def take_screenshot(page: Page, name: str = "") -> Path:
    """
    截图并保存到 screenshots 目录

    Args:
        page: Playwright Page 对象
        name: 截图文件名前缀

    Returns:
        截图文件路径
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{name}_" if name else ""
    filename = f"{prefix}{timestamp}.png"
    filepath = config.SCREENSHOTS_DIR / filename

    page.screenshot(path=str(filepath), full_page=True)
    log.info(f"截图已保存：{filepath}")
    return filepath
