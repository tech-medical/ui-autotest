"""
pytest 全局配置文件
负责：
  1. 浏览器 / Context / Page fixture
  2. 失败自动截图
  3. 日志与用例开始/结束打印
  4. 数据库操作 fixture
"""
import pytest
import subprocess
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from config.config import config
from utils.logger import get_logger
from db.portal_db import PortalDB

log = get_logger("conftest")


# ──────────────────────────────────────────────
# 强制 Allure 结果目录指向项目根目录
# 解决 PyCharm 中 CWD 为 tests/ 导致路径偏移的问题
# ──────────────────────────────────────────────
def pytest_configure(config):
    allure_dir = Path(config.rootdir) / "reports" / "allure-results"
    allure_dir.mkdir(parents=True, exist_ok=True)
    if hasattr(config.option, "allure_report_dir"):
        config.option.allure_report_dir = str(allure_dir)


# ──────────────────────────────────────────────
# 会话级 Browser（整个测试会话只启动一次）
# ──────────────────────────────────────────────
@pytest.fixture(scope="session")
def browser_instance():
    """启动浏览器实例（会话级，整个测试过程共享）"""
    with sync_playwright() as pw:
        browser_type = getattr(pw, config.BROWSER)
        log.info(
            f"启动浏览器: {config.BROWSER}  headless={config.HEADLESS}  slow_mo={config.SLOW_MO}ms"
        )
        browser: Browser = browser_type.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO,
            args=[
                "--disable-blink-features=AutomationControlled",  # 去除 navigator.webdriver 标记，防止网站识别为自动化
            ],
        )
        yield browser
        log.info("关闭浏览器")
        browser.close()


# ──────────────────────────────────────────────
# 函数级 Context + Page（每个用例独立上下文）
# ──────────────────────────────────────────────
@pytest.fixture(scope="function")
def context(browser_instance: Browser):
    """每个用例创建独立的浏览器上下文（隔离 Cookie/Storage）"""
    ctx: BrowserContext = browser_instance.new_context(
        base_url=config.BASE_URL,
        viewport={"width": 1440, "height": 900},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )
    # 覆盖 navigator.webdriver，防止网站通过该属性检测自动化浏览器
    ctx.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)
    ctx.set_default_timeout(config.TIMEOUT)
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """每个用例获取一个新 Page"""
    p: Page = context.new_page()
    yield p
    p.close()


# ──────────────────────────────────────────────
# 数据库操作实例（会话级共享连接池）
# ──────────────────────────────────────────────
@pytest.fixture(scope="session")
def db() -> PortalDB:
    """数据库操作实例（session 级共享连接池）"""
    db_instance = PortalDB()
    log.info("数据库 fixture 已就绪")
    yield db_instance
    # session 结束时连接池自动回收，无需显式关闭


# ──────────────────────────────────────────────
# 失败自动截图 hook
# ──────────────────────────────────────────────
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed and config.SCREENSHOT_ON_FAILURE:
        page_fixture: Page | None = item.funcargs.get("page")
        if page_fixture is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_name = item.name.replace("/", "_").replace(" ", "_")
            screenshot_path = config.SCREENSHOTS_DIR / f"FAIL_{test_name}_{timestamp}.png"
            try:
                page_fixture.screenshot(path=str(screenshot_path), full_page=True)
                log.error(f"[失败截图] {screenshot_path}")
            except Exception as e:
                log.warning(f"截图失败: {e}")


# ──────────────────────────────────────────────
# 用例开始/结束日志
# ──────────────────────────────────────────────
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    log.info(f"▶ 开始执行: {item.nodeid}")
    yield
    log.info(f"◀ 执行完毕: {item.nodeid}")


# ──────────────────────────────────────────────
# 测试结束后自动生成 Allure 单文件报告
# ──────────────────────────────────────────────
def pytest_sessionfinish(session, exitstatus):
    """生成单文件 Allure HTML 报告，剔除 GA 追踪代码"""
    results_dir = config.REPORTS_DIR / "allure-results"
    report_dir = config.REPORTS_DIR / "allure-report"

    try:
        subprocess.run(
            [
                "/usr/local/bin/allure", "generate",
                str(results_dir), "-o", str(report_dir),
                "--single-file", "--clean",
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
        # 移除 Google Analytics 追踪代码（无网络环境会报错）
        index_html = report_dir / "index.html"
        if index_html.exists():
            content = index_html.read_text(encoding="utf-8")
            content = re.sub(
                r'<script async src="https://www\.googletagmanager\.com/.*?</script>',
                "",
                content,
            )
            index_html.write_text(content, encoding="utf-8")
        log.info(f"📊 Allure 单文件报告已生成: {index_html}")
    except Exception as e:
        log.warning(f"Allure 报告生成失败: {e}")
