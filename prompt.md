# UI 自动化脚本编写规范

> 适用项目：`ui-automation`（Python + Playwright + pytest + Allure）
> 目标站点：https://test.portal.fastreat.com（Vue 3 + Naive UI SPA）

---

## 一、工程结构规范

```
ui-automation/
├── config/config.py        # 全局配置，从 .env 读取，禁止在测试代码中硬编码配置项
├── pages/
│   ├── base_page.py        # BasePage 基类，所有 Page Object 必须继承
│   └── <模块>_page.py      # 每个功能模块对应一个 Page Object 文件
├── tests/
│   └── test_<模块>.py      # 测试用例文件，一个模块一个文件
├── utils/logger.py         # 日志系统，使用 get_logger(__name__) 获取 logger
├── db/                     # 数据库操作封装
├── fixtures/               # 测试用到的静态资源（图片、文件等）
├── conftest.py             # pytest 全局 fixture 和 hook，不要在这里写业务逻辑
└── .env                    # 本地环境变量，不提交 git
```

**规则：**
- 所有测试数据（URL、账号、超时时间等）通过 `config.py` + `.env` 管理，不硬编码在测试代码中
- `fixtures/` 目录存放测试用到的上传文件、图片等静态资源
- Page Object 文件名格式：`<功能模块>_page.py`；测试文件名格式：`test_<模块>.py`

---

## 二、页面等待规范（最重要）

### 核心原则
**每一步操作前，必须等待当前页面完全加载，确认目标元素可见后再执行操作。**
禁止使用 `sleep()` 固定等待，应使用显式等待。

### SPA 页面等待策略

本项目为 Vue 3 SPA，页面切换时 URL 可能不变，需组合使用以下策略：

```python
# ✅ 正确：操作前等待目标元素可见
home.wait_for_visible_button("Next Step")
home.click_button_by_text("Next Step")

# ✅ 正确：点击后等待下一页的标志性元素出现
page.wait_for_selector("button:visible", timeout=15000)

# ❌ 错误：固定 sleep
import time; time.sleep(3)

# ❌ 错误：依赖 networkidle（SPA 会超时）
page.wait_for_load_state("networkidle")
```

### SPA 残留元素问题与解决方案

**问题**：SPA 切换页面时，上一页的 DOM 元素可能仍以 `hidden` 状态残留，导致定位器误匹配旧元素。

**解决方案（三步走）**：
1. 先等旧页面残留的同名隐藏元素消失
2. 用 `locator('button:visible')` 过滤，只匹配当前可见的按钮
3. 点击后调用 `_wait_for_page_stable()` 等页面稳定

```python
# ✅ 使用封装好的方法，已内置三步等待策略
home.wait_for_visible_button("No")   # 先等页面稳定
home.click_button_by_text("No")      # 点击时自动等待页面跳转完成
```

### 常用等待方式汇总

| 场景 | 推荐写法 |
|------|---------|
| 等待按钮可点击 | `home.wait_for_visible_button("按钮文字")` |
| 等待任意按钮出现（页面加载完成标志） | `page.wait_for_selector("button:visible", timeout=15000)` |
| 等待特定输入框出现 | `page.locator('input[placeholder="xxx"]').wait_for(state="visible", timeout=15000)` |
| 等待 URL 跳转 | `page.wait_for_url("**/target-path**", timeout=20000)` |
| 等待文字出现（断言前） | `page.get_by_text("xxx").wait_for(state="visible", timeout=15000)` |
| 等待 Vue 动画完成 | `page.wait_for_timeout(1500)`（仅用于动画，不得替代显式等待） |

---

## 三、Page Object 规范

### 基本结构

```python
from pages.base_page import BasePage
from playwright.sync_api import Page

class XxxPage(BasePage):
    # 1. 类常量：定位器（只放稳定的、复用率高的）
    SUBMIT_BUTTON = 'button:has-text("Submit")'

    def __init__(self, page: Page):
        super().__init__(page)

    # 2. 方法：每个方法封装一个原子操作，返回 self 支持链式调用
    def click_submit(self) -> "XxxPage":
        self._log.info("点击提交按钮")
        btn = self._page.locator(self.SUBMIT_BUTTON)
        btn.wait_for(state="visible", timeout=10000)
        btn.click()
        return self
```

### 方法设计原则

- 每个方法封装**一个原子操作**，不要在一个方法里做太多事
- 方法内部必须有**等待**：操作前 `wait_for(state="visible")`，操作后等页面稳定
- 方法必须有**日志**：`self._log.info(...)` 记录关键步骤
- 方法返回 `self` 以支持链式调用
- 对可能失败的操作用 `try/except` 兜底，记录 warning 后重试或跳过

---

## 四、已封装的公共方法（portal_home_page.py）

### 按钮操作

| 方法 | 适用场景 |
|------|---------|
| `click_button_by_text(text)` | 点击包含指定文字的可见按钮，内置 SPA 残留元素处理和页面稳定等待 |
| `wait_for_visible_button(text, timeout)` | 等待包含指定文字的按钮出现且可见，用于步骤间等待 |

### 表单输入

| 方法 | 适用场景 | 定位策略 |
|------|---------|---------|
| `fill_by_label(label_text, value)` | 通过 Naive UI form-item label 文字定位输入框 | `.n-form-item:has(.n-form-item-label__text:text-is("xxx")) input` |
| `fill_by_placeholder(placeholder, value)` | 通过 placeholder 定位输入框 | `input.n-input__input-el[placeholder="xxx"]` |
| `select_date(date_str, placeholder)` | 选择 Naive UI 日期选择器 | `type()` 逐字符输入触发 Vue onInput 事件 |

### 下拉选择框

| 方法 | 适用场景 | 定位策略 |
|------|---------|---------|
| `select_first_option_by_label(label_text)` | 通过 form-item label 定位 n-select | `.n-form-item:has(.n-form-item-label__text:text-is("xxx")) .n-select` |
| `select_first_option_by_placeholder(placeholder_text)` | 通过 n-select placeholder 定位（如 Feet/Inches） | `.n-select:has(.n-base-selection-placeholder__inner:text-is("xxx"))` |

### Checkbox

| 方法 | 适用场景 | 定位策略 |
|------|---------|---------|
| `check_checkbox_by_label(label_text)` | 勾选 Naive UI Checkbox | `.n-checkbox.filter(has_text="xxx")`（子串匹配，兼容嵌套 DOM 空白字符） |

### 文件上传

| 方法 | 适用场景 |
|------|---------|
| `upload_file(file_path, selector, nth)` | 上传文件，直接操作隐藏的 `<input type="file">`，无需触发 filechooser |

---

## 五、Naive UI 组件定位指南

### 输入框（n-input）

```python
# 有 label 的输入框
'.n-form-item:has(.n-form-item-label__text:text-is("Address Line 1")) input.n-input__input-el'

# 有 placeholder 的输入框
'input.n-input__input-el[placeholder="Enter your weight"]'

# 多行文本框（textarea）
'textarea.n-input__textarea-el'
```

### 下拉框（n-select）

```python
# 通过 form-item label 定位（label 在表单项上方）
'.n-form-item:has(.n-form-item-label__text:text-is("City")) .n-select'

# 通过 placeholder 定位（placeholder 显示在选择框内，如 Feet/Inches）
'.n-select:has(.n-base-selection-placeholder__inner:text-is("Feet"))'

# 下拉选项（面板打开后）
'.n-base-select-option:visible'
```

### Checkbox（n-checkbox）

```python
# 通过 label 文字（子串匹配，兼容嵌套 DOM）
page.locator('.n-checkbox').filter(has_text="None").first

# ⚠️ 不推荐精确匹配，label 文字在 <p> 内嵌套，含空白字符易匹配失败
'.n-checkbox:has(.n-checkbox__label:text-is("None"))'  # 容易超时
```

### 卡片（可点击容器）

```python
# 通过文字过滤可点击卡片
page.locator('div.cursor-pointer').filter(has_text="ASRS-V1.1").first

# 第一个药房卡片
page.locator('div.cursor-pointer.rounded-2xl').first
```

### 文件上传（van-uploader / n-upload）

```python
# Vant UI（默认）
'input.van-uploader__input[type="file"]'

# Naive UI
'input[type="file"]'

# 直接操作隐藏 input，无需 expect_file_chooser
file_input.set_input_files("/path/to/file.png")
```

---

## 六、测试用例规范

### 用例划分原则

- 每个用例应独立可运行，不依赖其他用例的浏览器状态（通过登录 fixture 隔离）
- 跨用例传递数据（如注册邮箱）使用**类变量** `TestXxx._registered_email`
- 每个用例的 docstring 必须包含：用例编号（TC-xxx）、功能描述、完整步骤列表

### 用例结构模板

```python
@allure.story("模块名")
@allure.title("TC-REG-001-1: 用例标题")
def test_xxx(self, page: Page):
    """
    TC-REG-001-1: 用例标题

    步骤:
        1. 步骤描述
        2. 步骤描述
    """
    log.info("TC-REG-001-1 | 开始执行")

    home = PortalHomePage(page)

    # ── Step 1: 步骤描述 ──
    log.info("Step 1: 操作描述")
    # ... 操作代码 ...

    log.info("TC-REG-001-1 | 执行完成 ✅")
```

### 步骤间等待规范

```python
# 每个步骤的标准写法：
# 1. 先等待目标元素/按钮出现
home.wait_for_visible_button("Target Button")
# 2. 执行操作（内部已包含等待）
home.click_button_by_text("Target Button")
# 3. 等待下一步的前置元素出现
page.wait_for_selector("button:visible", timeout=15000)
```

### 动态数据生成

```python
import time

# 唯一邮箱（时间戳）
email = f"autotest_{int(time.time())}@test.com"

# 唯一用户名
name = f"autotest{int(time.time())}"

# 手机号（2开头10位）
phone = f"2{int(time.time())}"[:10].ljust(10, "0")
```

### 断言规范

```python
# ✅ 正确：等待元素可见后再断言
element = page.get_by_text("Create your account", exact=False)
element.wait_for(state="visible", timeout=15000)
# 如有必要再加 assert

# ❌ 错误：直接断言，不等待
assert page.is_visible("text=Create your account")
```

---

## 七、日志规范

```python
from utils.logger import get_logger
log = get_logger(__name__)

# 用例开始/结束
log.info("TC-REG-001-1 | 开始执行")
log.info("TC-REG-001-1 | 执行完成 ✅")

# 步骤日志（带 Step 编号）
log.info("Step 3: 选择生日 2008/06/04，点击 Continue")

# 输入数据日志（敏感数据脱敏）
log.info(f"已输入邮箱: {email}")
log.info("已输入密码")        # 密码不打印具体值

# 警告（可恢复的异常）
log.warning("普通点击失败，尝试 force click")

# 错误（需要关注的问题）
log.error(f"断言失败: {actual} != {expected}")
```

---

## 八、错误处理规范

```python
# ✅ 可选步骤（如页面不一定出现的弹窗）
try:
    okay_btn = page.locator('button:visible').get_by_text("Okay").first
    okay_btn.wait_for(state="visible", timeout=5000)
    okay_btn.click()
    log.info("已点击 Okay")
except Exception:
    log.info("未检测到 Okay 按钮，跳过")

# ✅ 点击兜底（force click）
try:
    btn.click(timeout=5000)
except Exception:
    log.warning("普通点击失败，尝试 force click")
    btn.click(force=True)

# ✅ 循环操作（有明确退出条件，设置最大轮数防止死循环）
for round_num in range(1, 31):  # 最多30轮
    if 退出条件满足:
        break
    # 执行操作
else:
    log.warning("已达到最大轮数，未满足退出条件")
```

---

## 九、已知坑和解决方案速查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `button:has-text("No")` 超时或误匹配 | SPA 旧页面残留隐藏按钮 | 使用 `locator('button:visible').get_by_text("No")` |
| Checkbox `:text-is()` 精确匹配失败 | label 文字嵌套在 `<p>` 内含空白字符 | 改用 `.n-checkbox.filter(has_text="xxx")` 子串匹配 |
| 日期输入 `fill()` 不生效 | Vue 组件内部状态管理，fill 不触发 onInput | 改用 `type(date_str, delay=80)` 逐字符输入 |
| 文件上传无法操作 | `<input type="file">` 被 CSS 隐藏 | 直接用 `set_input_files()` 操作隐藏 input |
| 登录后跳转路径不固定 | 不同账号状态跳转到不同页面 | 改用 `page.wait_for_selector("button:visible")` 等任意按钮出现 |
| n-select 用 label 定位失败 | 该选择框没有 n-form-item-label，placeholder 在选框内 | 改用 `select_first_option_by_placeholder()` |
| `networkidle` 超时 | Vue SPA 始终有后台请求 | 禁止使用 `networkidle`，改用元素可见性等待 |
