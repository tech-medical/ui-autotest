"""
配置管理模块
从 .env 文件或环境变量中读取配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)


class Config:
    """全局配置类"""

    # 基础 URL
    BASE_URL: str = os.getenv("BASE_URL", "https://test.portal.fastreat.com")

    # 浏览器配置
    BROWSER: str = os.getenv("BROWSER", "chromium")
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))
    TIMEOUT: int = int(os.getenv("TIMEOUT", "30000"))

    # 截图配置
    SCREENSHOT_ON_FAILURE: bool = (
        os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    )

    # 路径配置
    ROOT_DIR: Path = Path(__file__).parent.parent
    LOGS_DIR: Path = ROOT_DIR / "logs"
    SCREENSHOTS_DIR: Path = ROOT_DIR / "screenshots"
    REPORTS_DIR: Path = ROOT_DIR / "reports"
    ALLURE_RESULTS_DIR: Path = ROOT_DIR / "reports" / "allure-results"

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # 数据库配置（MySQL）
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "tech_dev")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))

    def __init__(self):
        # 确保目录存在
        self.LOGS_DIR.mkdir(exist_ok=True)
        self.SCREENSHOTS_DIR.mkdir(exist_ok=True)
        self.REPORTS_DIR.mkdir(exist_ok=True)


config = Config()
