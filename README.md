# UI Automation — test.portal.fastreat.com

基于 **Python + Playwright + pytest** 的 UI 自动化测试框架。

## 目录结构

```
ui-automation/
├── config/
│   ├── __init__.py
│   └── config.py          # 配置管理（读取 .env）
├── pages/
│   ├── __init__.py
│   ├── base_page.py       # BasePage 基类（封装通用操作）
│   └── portal_home_page.py# Portal 首页 Page Object
├── tests/
│   ├── __init__.py
│   └── test_portal_home.py# 第一个测试用例
├── utils/
│   ├── __init__.py
│   ├── logger.py          # 日志系统（控制台彩色 + 文件按日期分割）
│   └── helpers.py         # 截图等工具函数
├── logs/                  # 日志输出（按日期命名）
├── reports/               # pytest-html 报告
├── screenshots/           # 截图（含失败自动截图）
├── conftest.py            # pytest 全局 fixture + hook
├── pytest.ini             # pytest 配置
├── requirements.txt       # 依赖清单
├── .env                   # 本地环境变量（不提交 git）
└── .env.example           # 环境变量模板
```

## 快速开始

### 1. 安装依赖

```bash
cd ui-automation
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 按需修改 .env 中的 BASE_URL、HEADLESS 等
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行指定用例
pytest tests/test_portal_home.py::TestPortalHome::test_open_homepage -v

# 有界面运行（方便调试）
# 修改 .env 中 HEADLESS=false，或临时覆盖：
HEADLESS=false pytest

# 慢放 500ms（便于观察操作）
SLOW_MO=500 pytest
```

### 4. 查看报告

```
reports/report.html   # pytest-html 报告
logs/YYYY-MM-DD.log   # 按日期分割的日志
screenshots/          # 截图（失败自动保存，用例中也可手动截图）
```

## 添加新用例

1. 在 `pages/` 下新建对应页面的 Page Object，继承 `BasePage`
2. 在 `tests/` 下新建 `test_<模块>.py`，通过 `page` fixture 获取页面

## 环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| BASE_URL | https://test.portal.fastreat.com | 测试环境基础 URL |
| BROWSER | chromium | 浏览器类型：chromium / firefox / webkit |
| HEADLESS | false | 是否无界面运行 |
| SLOW_MO | 0 | 操作慢放毫秒数 |
| TIMEOUT | 30000 | 默认超时（毫秒） |
| SCREENSHOT_ON_FAILURE | true | 失败时自动截图 |
| LOG_LEVEL | INFO | 日志级别 |
