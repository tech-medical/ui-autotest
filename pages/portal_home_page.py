"""
Portal 首页 Page Object
URL: https://test.portal.fastreat.com
"""
from playwright.sync_api import Page

from pages.base_page import BasePage
from config.config import config


class PortalHomePage(BasePage):
    """test.portal.fastreat.com 首页"""

    # ── 首页元素定位器 ───────────────────────
    SIGN_IN_BUTTON = 'button:has-text("Sign in")'
    GET_STARTED_BUTTON = '.n-button:has-text("Get Started")'

    def __init__(self, page: Page):
        super().__init__(page)

    def open(self) -> "PortalHomePage":
        """打开 Portal 首页"""
        self.navigate(config.BASE_URL)
        return self

    def click_get_started(self) -> "PortalHomePage":
        """点击 Get Started 按钮进入注册流程"""
        self._log.info("点击 Get Started 按钮")
        btn = self._page.locator('button.n-button--info-type.n-button--large-type')
        btn.wait_for(state="visible", timeout=15000)
        try:
            btn.click(timeout=5000)
        except Exception:
            self._log.warning("普通点击失败，尝试 force click")
            btn.click(force=True)
        # 等待页面跳转（不再用 networkidle，SPA 会导致超时）
        self._page.wait_for_timeout(2000)
        self._log.info(f"已点击 Get Started: {self._page.url}")
        return self

    def click_button_by_text(self, text: str, wait_for_next_page: bool = True) -> "PortalHomePage":
        """
        点击包含指定文本的可见按钮（兼容 Naive UI 组件库）

        定位策略（三步走，解决 SPA 残留元素问题）：
          Step 1 - 先等旧页面中包含该文本的隐藏元素消失
                  （SPA 切换时，上一页 DOM 可能仍残留 hidden 元素）
          Step 2 - 用 locator('button:visible') 精确匹配可见的 <button> 元素
                  再通过 .get_by_text() 过滤文本，确保只点新页面的按钮
          Step 3 - 点击后等待页面稳定

        Args:
            text: 按钮文字（子串匹配，如 "No" 可匹配包含 No 的按钮）
            wait_for_next_page: 是否等待页面切换到下一页（默认 True）
        """
        self._log.info(f"点击按钮: [{text}]")
        old_url = self._page.url

        # Step 1: 等待旧页面残留的同名隐藏元素消失
        try:
            old_el = self._page.get_by_text(text, exact=False).first
            if old_el.is_hidden():
                self._log.debug(f"检测到旧页面残留的隐藏元素 [{text}]，等待其消失...")
                old_el.wait_for(state="hidden", timeout=3000)
        except Exception:
            pass  # 没有残留元素，正常

        # Step 2: 精确定位可见 <button> 中包含目标文本的那个
        btn = self._page.locator('button:visible').get_by_text(text, exact=False).first
        btn.wait_for(state="visible", timeout=15000)
        try:
            btn.click(timeout=5000)
        except Exception:
            self._log.warning(f"普通点击失败，尝试 force click: {text}")
            btn.click(force=True)

        # Step 3: 等待页面完全加载
        if wait_for_next_page:
            self._wait_for_page_stable(old_url)

        self._log.info(f"已点击按钮 [{text}]  当前 URL: {self._page.url}")
        return self

    def wait_for_visible_button(self, text: str, timeout: int = 15000) -> "PortalHomePage":
        """
        等待页面上出现包含指定文本的可见按钮（用于 test 步骤间等待）

        定位策略：先等旧页面残留元素消失，再等新按钮出现。
        解决 SPA 页面切换时，上一页 DOM 残留 hidden 元素导致误匹配的问题。

        Args:
            text: 按钮文字（子串匹配）
            timeout: 最长等待时间(ms)
        """
        self._log.info(f"等待可见按钮: [{text}]")

        # 先等旧页面残留的同名隐藏元素消失
        try:
            old_el = self._page.get_by_text(text, exact=False).first
            if old_el.is_hidden():
                self._log.debug(f"检测到旧页面残留隐藏元素 [{text}]，等待其消失...")
                old_el.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

        # 再等新页面的可见按钮出现
        btn = self._page.locator('button:visible').get_by_text(text, exact=False).first
        btn.wait_for(state="visible", timeout=timeout)
        self._log.info(f"已检测到可见按钮 [{text}]")
        return self

    def _wait_for_page_stable(self, old_url: str, timeout: int = 15000) -> None:
        """
        等待页面稳定（SPA 兼容）
        策略：
          1. 先等 URL 变化（最多等 5 秒）
          2. 如果 URL 没变，说明是 SPA 前端路由（hash 或 history.pushState）
             则等待页面出现新的 button 元素（表示新页面已渲染）
          3. 最后等 1 秒让动画完成
        """
        try:
            # 策略1：等待 URL 变化
            self._page.wait_for_url(f"*{old_url}*", timeout=5000)
        except Exception:
            pass  # URL 没变，正常，SPA 前端路由不刷新页面

        try:
            # 策略2：等待页面上出现 button 元素（新页面已渲染）
            self._page.wait_for_selector("button", timeout=10000)
        except Exception:
            pass

        # 策略3：等待 Vue 渲染完成（SPA 通常有短暂动画）
        self._page.wait_for_timeout(1500)
        self._log.debug(f"页面已稳定: {self._page.url}")

    def click_sign_in(self) -> "PortalHomePage":
        """点击 Sign in 按钮跳转到登录页"""
        self._log.info("点击 Sign in 按钮")
        self._page.click(self.SIGN_IN_BUTTON)
        # 等待登录页的邮箱输入框出现
        self._page.wait_for_selector('input[placeholder="Email address"]', timeout=15000)
        self._log.info(f"已跳转到登录页: {self._page.url}")
        return self

    def login(self, email: str, password: str) -> "PortalHomePage":
        """
        在登录页输入邮箱和密码并提交

        Args:
            email: 邮箱地址
            password: 密码
        """
        # 填写邮箱
        email_input = self._page.locator('input[placeholder="Email address"]')
        email_input.fill(email)
        self._log.info(f"已输入邮箱: {email}")

        # 填写密码
        pwd_input = self._page.locator('input[placeholder="Password"]')
        pwd_input.fill(password)
        self._log.info("已输入密码")

        # 点击 Continue 提交
        self._page.click('button:has-text("Continue")')
        # 精确等待 URL 跳转到主页
        self._page.wait_for_url("**/appointmented/home**", timeout=20000)
        self._log.info(f"登录跳转完成: {self._page.url}")

        return self

    def is_login_success(self) -> bool:
        """
        判断是否登录成功
        策略：等待页面渲染出 "Hi," 问候语（login() 已确保 URL 跳转）
        """
        try:
            self._page.wait_for_selector("text=Hi,", timeout=10000)
            self._log.info(f"登录成功 ✅  URL={self._page.url}")
            return True
        except Exception:
            self._log.warning(f"登录后未检测到用户标识，当前 URL: {self._page.url}")
            return False

    def select_date(self, date_str: str, placeholder: str = "Select Date") -> "PortalHomePage":
        """
        在 Naive UI 日期选择器中通过键盘输入选择指定日期

        适用场景：birthday 等需要选择多年前日期的情况。
        对于远年份日期，键盘输入比在日历面板中逐月翻页更高效。

        Naive UI n-date-picker 特点：
          - 渲染为 <input class="n-input__input-el" placeholder="Select Date">
          - 组件内部管理 value，fill() 替换整个值可能不触发 Vue 的 onInput
          - type() 逐字符触发 keydown/input/keyup 事件，Vue 组件能正确接收
          - 日期格式 YYYY/MM/DD，如 "2008/06/04"

        操作流程：
          1. 定位日期输入框（通过 placeholder）
          2. 点击 input 获取焦点
          3. 清空现有值（Ctrl+A → Delete）
          4. 逐字符输入新日期
          5. 按 Enter 确认并关闭日期面板
          6. 验证输入结果

        Args:
            date_str: 日期字符串，格式 YYYY/MM/DD，如 "2008/06/04"
            placeholder: 输入框 placeholder，用于定位（默认 "Select Date"）
        """
        self._log.info(f"选择日期: {date_str}")

        # 1. 定位日期输入框
        date_input = self._page.locator(f'input.n-input__input-el[placeholder="{placeholder}"]')
        date_input.wait_for(state="visible", timeout=10000)

        # 2. 点击获取焦点
        date_input.click()
        self._page.wait_for_timeout(500)

        # 3. 清空现有值（三击选中全部文本，再删除）
        date_input.click(click_count=3)
        self._page.wait_for_timeout(200)
        self._page.keyboard.press("Backspace")
        self._page.wait_for_timeout(300)

        # 4. 逐字符输入日期（type() 触发逐字符 keydown/input 事件，Vue 能正确接收）
        date_input.type(date_str, delay=80)
        self._page.wait_for_timeout(500)

        # 5. 按 Enter 确认选择（关闭日期面板）
        self._page.keyboard.press("Enter")
        self._page.wait_for_timeout(1000)

        # 6. 验证输入结果
        actual_value = date_input.input_value()
        self._log.info(f"日期选择完成，输入框值: {actual_value}")

        return self

    def upload_file(self, file_path: str, selector: str = 'input.van-uploader__input[type="file"]',
                    nth: int = 0, timeout: int = 15000) -> "PortalHomePage":
        """
        上传文件（兼容 Vant UI van-uploader / Naive UI n-upload 组件）

        Vue 组件库的文件上传组件特点：
          - <input type="file"> 元素通常隐藏（display:none / visibility:hidden）
          - 用户看到的是美化后的上传区域/按钮，点击后触发隐藏的 file input
          - Playwright 的 set_input_files() 可直接操作隐藏的 file input，无需触发 filechooser

        操作流程：
          1. 定位隐藏的 <input type="file"> 元素
          2. 调用 set_input_files() 设置文件路径（Playwright 内部模拟用户选择文件）
          3. 等待上传完成（等待页面出现上传成功的标识或新元素）

        Args:
            file_path: 文件绝对路径，如 "/Users/caoyx/test.pdf"
            selector:  file input 的 CSS 选择器（默认 Vant UI 的 van-uploader）
                       若为 Naive UI n-upload，使用 'input[type="file"]'
            nth:       页面上有多个 file input 时，指定第几个（从 0 开始）
            timeout:   等待上传完成的超时时间(ms)
        """
        import os

        self._log.info(f"上传文件: {file_path}")

        # 检查文件是否存在
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 1. 定位隐藏的 file input
        file_input = self._page.locator(selector).nth(nth)
        # set_input_files 无需 input 可见，可直接操作隐藏元素

        # 2. 设置文件（Playwright 内部模拟用户选择文件）
        file_input.set_input_files(file_path)
        self._log.info(f"已选择文件: {os.path.basename(file_path)}")

        # 3. 等待上传完成（等待页面出现新元素，表示上传已处理）
        try:
            self._page.wait_for_selector("button:visible", timeout=timeout)
        except Exception:
            # 某些页面上传后不一定出现新按钮，等待 2 秒即可
            self._page.wait_for_timeout(2000)

        self._log.info(f"文件上传完成: {os.path.basename(file_path)}")
        return self

    def fill_by_label(self, label_text: str, value: str, timeout: int = 10000) -> "PortalHomePage":
        """
        通过 Naive UI 表单 label 文字定位输入框并填值

        Naive UI 表单项 DOM 结构：
          div.n-form-item
            ├── label.n-form-item-label
            │     └── span.n-form-item-label__text  ← 字段名（如 "Address Line 1"）
            └── div.n-form-item-blank
                  └── div.n-input
                        └── input.n-input__input-el  ← 目标 input

        定位策略：.n-form-item:has(.n-form-item-label__text:text-is("xxx")) input
        优势：不依赖 placeholder、不依赖 index、精确匹配 label 文字

        Args:
            label_text: 表单 label 文字（精确匹配），如 "Address Line 1"
            value: 要输入的值
            timeout: 等待输入框可见的超时时间(ms)
        """
        self._log.info(f"通过 label [{label_text}] 输入值: {value}")
        selector = f'.n-form-item:has(.n-form-item-label__text:text-is("{label_text}")) input.n-input__input-el'
        input_el = self._page.locator(selector).first
        input_el.wait_for(state="visible", timeout=timeout)
        input_el.fill(value)
        self._log.info(f"已通过 label [{label_text}] 输入: {value}")
        return self

    def select_first_option_by_label(self, label_text: str, timeout: int = 10000) -> "PortalHomePage":
        """
        通过 Naive UI 表单 label 文字定位下拉选择框，点击并选择第一个选项

        适用场景：n-select 的 label 是 n-form-item-label（如 "City"、"Zip / Postal code"）

        Naive UI n-select 组件交互流程：
          1. 定位 .n-select 触发器（在对应 label 的表单项内）
          2. 点击触发器打开下拉面板
          3. 等待下拉选项出现
          4. 点击第一个选项

        Args:
            label_text: 表单 label 文字（精确匹配），如 "City"、"Zip / Postal code"
            timeout: 等待选择框可见的超时时间(ms)
        """
        self._log.info(f"通过 label [{label_text}] 选择第一个选项")

        # 1. 定位并点击 n-select 触发器
        select_selector = f'.n-form-item:has(.n-form-item-label__text:text-is("{label_text}")) .n-select'
        select_trigger = self._page.locator(select_selector).first
        select_trigger.wait_for(state="visible", timeout=timeout)
        select_trigger.click()
        self._log.debug(f"已点击 [{label_text}] 下拉框")

        # 2. 等待下拉选项出现，点击第一个
        option = self._page.locator('.n-base-select-option:visible, .n-select-option:visible').first
        option.wait_for(state="visible", timeout=5000)
        option_text = option.inner_text()
        option.click()
        self._log.info(f"已选择 [{label_text}] 的第一个选项: {option_text}")

        # 等待下拉面板关闭
        self._page.wait_for_timeout(500)
        return self

    def select_first_option_by_placeholder(self, placeholder_text: str, timeout: int = 10000) -> "PortalHomePage":
        """
        通过 n-select 的 placeholder 文字定位下拉选择框，点击并选择第一个选项

        适用场景：n-select 没有 form-item-label，placeholder 直接显示在选中区域
        （如 "Feet"、"Inches"，DOM 为 <div class="n-base-selection-placeholder__inner">Feet</div>）

        定位策略：.n-select:has(.n-base-selection-placeholder__inner:text-is("xxx"))

        Args:
            placeholder_text: 选择框的 placeholder 文字（精确匹配），如 "Feet"、"Inches"
            timeout: 等待选择框可见的超时时间(ms)
        """
        self._log.info(f"通过 placeholder [{placeholder_text}] 选择第一个选项")

        # 1. 定位并点击 n-select 触发器（通过 placeholder 文字匹配）
        select_selector = f'.n-select:has(.n-base-selection-placeholder__inner:text-is("{placeholder_text}"))'
        select_trigger = self._page.locator(select_selector).first
        select_trigger.wait_for(state="visible", timeout=timeout)
        select_trigger.click()
        self._log.debug(f"已点击 [{placeholder_text}] 下拉框")

        # 2. 等待下拉选项出现，点击第一个
        option = self._page.locator('.n-base-select-option:visible, .n-select-option:visible').first
        option.wait_for(state="visible", timeout=5000)
        option_text = option.inner_text()
        option.click()
        self._log.info(f"已选择 [{placeholder_text}] 的第一个选项: {option_text}")

        # 等待下拉面板关闭
        self._page.wait_for_timeout(500)
        return self

    def check_checkbox_by_label(self, label_text: str, timeout: int = 10000) -> "PortalHomePage":
        """
        勾选/取消勾选 Naive UI Checkbox（通过 label 文字定位）

        Naive UI n-checkbox DOM 结构：
          div.n-checkbox
            ├── div.n-checkbox-box-wrapper
            │     └── div.n-checkbox-box      ← 勾选框图标
            └── span.n-checkbox__label
                  └── div
                        └── p                  ← label 文字（如 "None"）

        定位策略：.n-checkbox.filter(has_text="xxx")
        说明：label 文字在 <p> 标签内嵌套，:text-is() 可能因空白字符不匹配，
             改用 filter(has_text=) 子串匹配，配合 .n-checkbox 约束已足够精确。
        点击整个 .n-checkbox 即可切换勾选状态。

        Args:
            label_text: checkbox 的 label 文字（子串匹配），如 "None"
            timeout: 等待 checkbox 可见的超时时间(ms)
        """
        self._log.info(f"勾选 checkbox [{label_text}]")
        checkbox = self._page.locator('.n-checkbox').filter(has_text=label_text).first
        checkbox.wait_for(state="visible", timeout=timeout)
        checkbox.click()
        self._log.info(f"已勾选 checkbox [{label_text}]")
        return self

    def fill_by_placeholder(self, placeholder: str, value: str, timeout: int = 10000) -> "PortalHomePage":
        """
        通过 placeholder 定位 Naive UI 输入框并填值

        适用场景：输入框没有 form-item-label，但有明确的 placeholder 文字

        Args:
            placeholder: 输入框 placeholder 文字（精确匹配）
            value: 要输入的值
            timeout: 等待输入框可见的超时时间(ms)
        """
        self._log.info(f"通过 placeholder [{placeholder}] 输入值: {value}")
        input_el = self._page.locator(f'input.n-input__input-el[placeholder="{placeholder}"]').first
        input_el.wait_for(state="visible", timeout=timeout)
        input_el.fill(value)
        self._log.info(f"已通过 placeholder [{placeholder}] 输入: {value}")
        return self

    def is_loaded(self) -> bool:
        """判断页面是否正常加载"""
        current_url = self.url
        loaded = "fastreat.com" in current_url
        self._log.info(f"页面加载状态: {'✅ 已加载' if loaded else '❌ 异常'}  URL={current_url}")
        return loaded
