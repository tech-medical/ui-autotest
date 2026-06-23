"""
日志系统模块
支持控制台彩色输出 + 按日期分割的纯文本文件日志
（报告由 Allure 统一管理）
"""
import logging
import sys
from datetime import datetime

import colorlog

from config.config import config


def get_logger(name: str) -> logging.Logger:
    """
    获取带有彩色控制台输出和文件输出的 logger

    Args:
        name: logger 名称，通常传入 __name__

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # -------- 控制台 handler（彩色）--------
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = colorlog.ColoredFormatter(
        fmt="%(log_color)s%(asctime)s [%(levelname)-8s] %(name)s%(reset)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # -------- 文件 handler（按日期）--------
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = config.LOGS_DIR / f"{today}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 阻止日志向上层 logger 传播（避免重复打印）
    logger.propagate = False

    return logger


# 导出一个默认 logger 方便直接使用
logger = get_logger("ui-auto")
