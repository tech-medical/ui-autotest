"""
测试套件：用户注册流程（4个用例）

用例划分：
    一、test_register_questionnaire —— 填写问卷并注册账号
    二、test_register_profile       —— 添加个人信息并预约付款
    三、test_register_survey        —— 添加个人详细信息
    四、test_register_assessment    —— 添加详细问卷
每个用例独立运行，使用 conftest.py 中的函数级 fixture，互不影响。
"""
import os
import time

import pytest
from playwright.sync_api import Page

from pages.portal_home_page import PortalHomePage
from utils.logger import get_logger

log = get_logger(__name__)


class TestRegister:
    """用户注册流程测试"""

    # 类变量：跨用例传递注册凭据（每个用例仍使用独立的浏览器上下文）
    _registered_email: str = ""
    _registered_password: str = "1qaz2wsx"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 一、填写问卷并注册账号
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_register_questionnaire(self, page: Page):
        """
        TC-REG-001-1: 填写问卷并注册账号

        步骤:
            1. 访问 https://test.portal.fastreat.com
            2. 点击 Get Started 按钮
            3. 点击 Yes, I am legally an adult
            4. 点击 No
            5. 连续6次点击 Never
            6. 点击 No, I have never had suicidal thoughts, plans, or attempts
            7. 点击 No
            8. 断言页面存在 Create your account
            9. 输入 Email（时间戳唯一）和 Password（1qaz2wsx），点击 Continue

        每一步都通过 wait_for_visible_button() 等页面完全加载后再执行操作，
        解决 SPA 页面切换时旧 DOM 残留导致元素误匹配的问题。
        """
        log.info("TC-REG-001-1 | 开始填写问卷并注册")

        # ── Step 1: 打开首页，等待页面完全加载 ──
        home = PortalHomePage(page)
        home.open()
        page.locator('button.n-button--info-type.n-button--large-type').wait_for(state="visible", timeout=15000)

        # ── Step 2: 点击 Get Started ──
        log.info("Step 2: 点击 Get Started")
        home.click_get_started()
        home.wait_for_visible_button("Yes")

        # ── Step 3: 点击 "Yes, I am legally an adult" ──
        log.info('Step 3: 点击 "Yes, I am legally an adult"')
        home.click_button_by_text("Yes, I am legally an adult")
        home.wait_for_visible_button("No")

        # ── Step 4: 点击 "No" ──
        log.info('Step 4: 点击 "No"')
        home.click_button_by_text("No")
        home.wait_for_visible_button("Never")

        # ── Step 5: 连续6次点击 "Never" ──
        for i in range(6):
            step = 6 + i
            log.info(f'Step {step}: 点击 "Never"')
            home.click_button_by_text("Never")
            try:
                home.wait_for_visible_button("Never", timeout=10000)
            except Exception:
                page.wait_for_selector("button:visible", timeout=10000)

        # ── Step 6: 点击 "No, I have never had suicidal thoughts, plans, or attempts" ──
        log.info('Step 11: 点击 "No, I have never had suicidal thoughts, plans, or attempts"')
        home.click_button_by_text("No, I have never had suicidal thoughts, plans, or attempts")
        page.wait_for_selector("button:visible", timeout=15000)

        # ── Step 7: 点击 "No" ──
        log.info('Step 12: 点击 "No"')
        home.click_button_by_text("No")
        page.wait_for_selector("button:visible", timeout=15000)

        # ── Step 8: 断言页面存在 "Create your account" ──
        log.info('Step 13: 断言页面存在 "Create your account"')
        heading = page.get_by_text("Create your account", exact=False)
        heading.wait_for(state="visible", timeout=15000)

        # ── Step 9: 输入 Email 和 Password，点击 Continue ──
        timestamp = int(time.time())
        email = f"autotest_{timestamp}@test.com"
        password = "1qaz2wsx"
        TestRegister._registered_email = email
        log.info(f'Step 9: 输入 Email={email}, Password=***')

        email_input = page.locator('input[type="email"], input[placeholder*="mail"], input[placeholder*="Email"]')
        email_input.first.wait_for(state="visible", timeout=10000)
        email_input.first.fill(email)
        log.info(f"已输入 Email: {email}")
        print(f"[REGISTER_EMAIL] {email}")

        pwd_input = page.locator('input[type="password"]')
        pwd_input.first.wait_for(state="visible", timeout=10000)
        pwd_input.first.fill(password)
        log.info("已输入 Password")

        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)

        log.info("TC-REG-001-1 | 填写问卷并注册 ✅")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 二、添加个人信息并预约付款
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_register_profile(self, page: Page):
        """
        TC-REG-001-2: 添加个人信息并预约付款
        步骤:
            1. 登录（使用用例一注册的账号密码）
            2. 等待 Book An Appointment 按钮变为可用，点击
            3. 填写两个 As on your ID，点击 ON 上方图片，点击 Continue
            4.点击任意 AM 或 PM 时间按钮跳转到下一页
            5.点击“Confirm&Save”按钮跳转到下一页
            6.等待页面完全加载后，在1234 1234 1234 1234输入框中输入 4242 4242 4242 4242，在MM/YY输入框中输入 01/33，在CVC输入框中输入 123，点击 Confirm&Pay
            7.等待页面完全加载后，在1234567891的输入框中输入 2开头的10位数字，点击 Start Your Service

        """
        log.info("TC-REG-001-2 | 添加个人信息并预约付款")

        # ── Step 1: 登录 ──

        email = TestRegister._registered_email
        password = TestRegister._registered_password
        assert email, "未获取到注册邮箱，请先运行 test_register_questionnaire"
        log.info(f"Step 1: 使用注册账号登录, Email={email}")

        """email="autotest0615@gmail.com"
        password="1qaz2wsx"""""
        home = PortalHomePage(page)
        home.open()
        home.click_sign_in()

        # 手动填写登录表单（新账号登录后跳转 /profile，不能用 home.login()）
        page.locator('input[placeholder="Email address"]').fill(email)
        log.info(f"已输入邮箱: {email}")
        page.locator('input[placeholder="Password"]').fill(password)
        log.info("已输入密码")
        page.click('button:has-text("Continue")')
        page.wait_for_url("**/profile**", timeout=20000)
        log.info(f"登录成功，已跳转到: {page.url}")

        """
        # ── Step 2: 等待 Book An Appointment 按钮可用并点击 ──
        log.info("Step 2: 等待 Book An Appointment 按钮可用并点击")
        book_btn = page.locator('button:has-text("Book An Appointment")')
        book_btn.wait_for(state="visible", timeout=15000)
        try:
            book_btn.click(timeout=5000)
        except Exception:
            log.warning("普通点击失败，尝试 force click")
            book_btn.click(force=True)
        page.wait_for_timeout(2000)
        log.info(f"已点击 Book An Appointment, URL: {page.url}")
 """
        # ── Step 3: 两个 "As on your ID" 输入框输入 autotest+时间戳，点击 ON 上方图片，点击 Continue ──
        log.info("Step 3: 填写 As on your ID，点击 ON 上方图片，点击 Continue")
        timestamp = int(time.time())
        name_value = f"autotest{timestamp}"

        # 填写两个 "As on your ID" 输入框
        id_inputs = page.locator('input.n-input__input-el[placeholder="As on your ID"]')
        id_inputs.nth(0).wait_for(state="visible", timeout=10000)
        id_inputs.nth(0).fill(name_value)
        log.info(f"已输入第1个 As on your ID: {name_value}")
        id_inputs.nth(1).fill(name_value)
        log.info(f"已输入第2个 As on your ID: {name_value}")

        # 点击 ON 上方的图片（ON 按钮的前一个兄弟 img 元素）
        on_btn = page.locator('button:has-text("ON")')
        on_btn.wait_for(state="visible", timeout=10000)
        # 定位 ON 按钮上方最近的图片并点击
        on_image = on_btn.locator("xpath=preceding-sibling::img[1] | preceding::img[1]")
        try:
            on_image.wait_for(state="visible", timeout=5000)
            on_image.click()
            log.info("已点击 ON 上方的图片")
        except Exception:
            # 兜底：尝试点击 ON 按钮所在容器中上方的图片
            parent_img = on_btn.locator("xpath=ancestor::*[.//img][1]//img")
            parent_img.first.click()
            log.info("已点击 ON 上方的图片（兜底定位）")

        # 点击 Continue
        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Continue")

        # ── Step 4: 点击任意 AM 或 PM 时间按钮 ──
        log.info("Step 4: 点击任意 AM/PM 时间按钮")
        am_pm_btn = page.locator(
            'button:has-text("AM"), button:has-text("PM"), button:has-text("am"), button:has-text("pm")'
        ).first
        if am_pm_btn.count() == 0:
            am_pm_btn = page.locator("text=/\\b(AM|PM|am|pm)\\b/").first
        am_pm_btn.wait_for(state="visible", timeout=15000)
        selected_time = am_pm_btn.inner_text()
        log.info(f"点击时间按钮: {selected_time}")
        am_pm_btn.click()
        page.wait_for_timeout(2000)
        log.info("已点击 AM/PM 时间按钮")

        # ── Step 5: 点击 "Confirm&Save" 按钮 ──
        log.info('Step 5: 点击 "Confirm&Save" 按钮')
        confirm_save_btn = page.locator('button:visible').filter(has_text="Confirm").filter(has_text="Save").first
        confirm_save_btn.wait_for(state="visible", timeout=15000)
        confirm_save_btn.click()
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Confirm&Save")

        # ── Step 6: 填写支付信息并点击 Confirm&Pay ──
        log.info("Step 6: 填写支付信息")

        # Stripe 支付表单通常在 iframe 中
        stripe_frame = page.frame_locator('iframe[name*="stripe"], iframe[src*="stripe"]').first
        try:
            # 卡号输入框（placeholder: 1234 1234 1234 1234）
            card_input = stripe_frame.locator('input[placeholder="1234 1234 1234 1234"], input[name="cardnumber"]')
            card_input.wait_for(state="visible", timeout=15000)
            card_input.fill("4242 4242 4242 4242")
            log.info("已输入卡号: 4242 4242 4242 4242")

            # MM/YY 输入框
            expiry_input = stripe_frame.locator('input[placeholder="MM / YY"], input[name="exp-date"]')
            expiry_input.fill("01/33")
            log.info("已输入有效期: 01/33")

            # CVC 输入框
            cvc_input = stripe_frame.locator('input[placeholder="CVC"], input[name="cvc"]')
            cvc_input.fill("123")
            log.info("已输入 CVC: 123")
        except Exception:
            # 兜底：支付表单不在 iframe 中，直接在页面上定位
            log.warning("Stripe iframe 未找到，尝试直接在页面定位支付输入框")
            card_input = page.locator('input[placeholder="1234 1234 1234 1234"]')
            card_input.wait_for(state="visible", timeout=15000)
            card_input.fill("4242 4242 4242 4242")
            log.info("已输入卡号: 4242 4242 4242 4242")

            expiry_input = page.locator('input[placeholder="MM/YY"], input[placeholder="MM / YY"]')
            expiry_input.fill("01/33")
            log.info("已输入有效期: 01/33")

            cvc_input = page.locator('input[placeholder="CVC"]')
            cvc_input.fill("123")
            log.info("已输入 CVC: 123")

        # 点击 Confirm&Pay
        confirm_pay_btn = page.locator('button:visible').filter(has_text="Confirm").filter(has_text="Pay").first
        confirm_pay_btn.wait_for(state="visible", timeout=15000)
        confirm_pay_btn.click()
        page.wait_for_timeout(3000)
        log.info("已点击 Confirm&Pay")

        # ── Step 7: 输入手机号并点击 Start Your Service ──
        log.info("Step 7: 输入手机号，点击 Start Your Service")
        phone_input = page.locator('input.n-input__input-el[placeholder="1234567891"]')
        phone_input.wait_for(state="visible", timeout=15000)
        phone_number = f"2{int(time.time())}"[:10].ljust(10, "0")
        phone_input.fill(phone_number)
        log.info(f"已输入手机号: {phone_number}")

        start_btn = page.locator('button:visible').filter(has_text="Start Your Service").first
        start_btn.wait_for(state="visible", timeout=15000)
        start_btn.click()
        page.wait_for_timeout(3000)
        log.info("已点击 Start Your Service")

        log.info("TC-REG-001-2 | 添加个人信息并预约付款 ✅")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 三、填写问卷
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_register_survey(self, page: Page):
        """
        TC-REG-001-3: 填写问卷

        步骤:
            1. 登录（使用用例一注册的账号密码），点击 Okay 按钮
            2. 点击 She/her → 点击 Female
            3. 选择生日 2008/06/04，点击 Continue
            4、在HCN输入框中输入任意10位数字，点击 Continue跳转到下一页
            5、点击 I don`t have one，跳转到下一页
            6、点击页面上传照片按钮，上传任意模拟图片，点击 Continue 跳转到下一页
            7、在Feet选择框中任意选择一项，在Inches选择框中任意选择一项，在Enter your weight中输入123，点击 Continue 跳转到下一页
            8、在Enter your upper blood pressure中输入100，在Enter your lower blood pressure中输入80，在Enter the heart rate中输入80，点击 Continue 跳转到下一页
            9、在Address Line 1下方的输入框中输入10位数字，在包含Address Line 2下方的输入框中输入10位数字，在City下方的选择框中任意选择一个，在Zip / Postal code下方的选择框中任意选择一个，点击 Continue 跳转到下一页
            10、点击No按钮，跳转到下一页；这个操作循环5次，在最后一次点击No后，跳转到下一页
            11、在包含None所属的checkbox中点击勾选框，点击 Continue 跳转到下一页
            12、点击No, I do not have any heart conditions or high blood pressure按钮，跳转到下一页
            13、在I am not currently taking any of the above所属的checkbox中点击勾选框，点击 Continue 跳转到下一页
            14、点击No按钮，跳转到下一页；这个操作循环3次，在最后一次点击No后，跳转到下一页
            15、点击No, I have never had a seizure按钮，跳转到下一页
            16、点击No, I have never had an eating disorder按钮，跳转到下一页
            17、点击Search by Postal Code or Name输入框（使用placeholder定位）跳转到下一页，点击药房卡片，跳转到下一页，点击Choose，跳转到下一页，点击Confirm，跳转到下一页
            18、在Full name输入框中输入autotest+时间戳，在Phone number输入框中输入1 2334534454，在Email输入框中输入autotest@gmail.com，在Relationship中输入mother，点击 Continue 跳转到下一页
            19、点击Start the Assessment按钮，跳转到下一页
        每一步都通过 wait_for_visible_button() 等页面完全加载后再执行操作。
        """
        log.info("TC-REG-001-3 | 开始填写问卷")

        # ── Step 1: 登录，点击 Okay ──
        email = TestRegister._registered_email
        password = TestRegister._registered_password
        assert email, "未获取到注册邮箱，请先运行 test_register_questionnaire"
        log.info(f"Step 1: 使用注册账号登录, Email={email}")
        #email="autotest06162@gmail.com"
        #password="1qaz2wsx"
        home = PortalHomePage(page)
        home.open()
        home.click_sign_in()

        # 填写登录表单
        page.locator('input[placeholder="Email address"]').fill(email)
        log.info(f"已输入邮箱: {email}")
        page.locator('input[placeholder="Password"]').fill(password)
        log.info("已输入密码")
        page.click('button:has-text("Continue")')
        page.wait_for_url("**/pre-intake**", timeout=20000)
        log.info(f"登录成功，已跳转到: {page.url}")

        # 点击 Okay 按钮
        home.wait_for_visible_button("Okay")
        home.click_button_by_text("Okay")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Okay")

        # ── Step 2: 点击 She/her → 点击 Female ──
        log.info("Step 2: 点击 She/her")
        home.wait_for_visible_button("She/her")
        home.click_button_by_text("She/her")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 She/her")

        log.info("Step 2b: 点击 Female")
        home.wait_for_visible_button("Female")
        home.click_button_by_text("Female")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Female")

        # ── Step 3: 选择生日 2008/06/04，点击 Continue ──
        log.info("Step 3: 选择生日 2008/06/04，点击 Continue")
        # 等待日期选择器出现
        page.locator('input.n-input__input-el[placeholder="Select Date"]').wait_for(state="visible", timeout=15000)
        home.select_date("2008/06/04")
        log.info("已选择生日: 2008/06/04")

        # 点击 Continue
        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Continue")

        # ── Step 4: 在 HCN 输入框中输入任意 10 位数字，点击 Continue ──
        log.info("Step 4: 输入 HCN（10位数字），点击 Continue")
        hcn_input = page.locator('input.n-input__input-el[placeholder*="HCN"], input.n-input__input-el[placeholder*="hcn"]')
        hcn_input.first.wait_for(state="visible", timeout=15000)
        hcn_number = f"1234567890"
        hcn_input.first.fill(hcn_number)
        log.info(f"已输入 HCN: {hcn_number}")

        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Continue")

        # ── Step 5: 点击 I don't have one ──
        log.info("Step 5: 点击 I don't have one")
        home.wait_for_visible_button("I don't have one")
        home.click_button_by_text("I don't have one")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 I don't have one")

        # ── Step 6: 上传照片，点击 Continue ──
        log.info("Step 6: 上传照片，点击 Continue")
        # 上传测试 fixture 图片
        fixture_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fixtures")
        photo_path = os.path.join(fixture_dir, "test_photo.png")
        home.upload_file(photo_path)
        log.info(f"已上传照片: {photo_path}")

        # 点击 Continue
        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Continue")

        # ── Step 7: Feet 选择框选一项，Inches 选择框选一项，输入 weight，点击 Continue ──
        log.info("Step 7: 选择 Feet/Inches，输入体重")
        # 等待 Feet 选择框出现（Feet 是 n-select 的 placeholder，不是 form-item-label）
        page.locator('.n-select:has(.n-base-selection-placeholder__inner:text-is("Feet"))').first.wait_for(
            state="visible", timeout=15000
        )
        home.select_first_option_by_placeholder("Feet")
        log.info("已选择 Feet 第一项")

        home.select_first_option_by_placeholder("Inches")
        log.info("已选择 Inches 第一项")

        # 输入体重（placeholder 包含 "Enter your weight"）
        home.fill_by_placeholder("Enter your weight", "123")
        log.info("已输入体重: 123")

        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Continue")

        # ── Step 8: 输入血压和心率，点击 Continue ──
        log.info("Step 8: 输入血压和心率")
        # 等待血压输入框出现
        page.locator('input.n-input__input-el[placeholder="Enter your upper blood pressure"]').first.wait_for(
            state="visible", timeout=15000
        )
        home.fill_by_placeholder("Enter your upper blood pressure", "100")
        log.info("已输入高压: 100")

        home.fill_by_placeholder("Enter your lower blood pressure", "80")
        log.info("已输入低压: 80")

        home.fill_by_placeholder("Enter the heart rate", "80")
        log.info("已输入心率: 80")

        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Continue")

        # ── Step 9: 输入地址信息，选择 City 和 Zip，点击 Continue ──
        log.info("Step 9: 输入地址信息")
        # 等待 Address Line 1 输入框出现
        page.locator(
            '.n-form-item:has(.n-form-item-label__text:text-is("Address Line 1")) input.n-input__input-el'
        ).first.wait_for(state="visible", timeout=15000)

        # 在 Address Line 1 下方输入 10 位数字
        home.fill_by_label("Address Line 1", "1234567890")
        log.info("已输入 Address Line 1: 1234567890")

        # 在 Address Line 2 下方输入 10 位数字
        home.fill_by_label("Address Line 2 (optional)", "1234567890")
        log.info("已输入 Address Line 2: 1234567890")

        # 选择 City 下拉框的第一个选项
        home.select_first_option_by_label("City")
        log.info("已选择 City 第一项")

        # 选择 Zip / Postal code 下拉框的第一个选项
        home.select_first_option_by_label("Zip / Postal code")
        log.info("已选择 Zip / Postal code 第一项")

        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Continue")

        # ── Step 10: 点击 No 按钮，循环5次 ──
        log.info("Step 10: 循环5次点击 No")
        for i in range(5):
            loop_num = i + 1
            log.info(f'  Step 10.{loop_num}: 点击 No')
            home.wait_for_visible_button("No")
            home.click_button_by_text("No")
            try:
                home.wait_for_visible_button("No", timeout=10000)
            except Exception:
                page.wait_for_selector("button:visible", timeout=10000)

        # ── Step 11: 勾选 None checkbox，点击 Continue ──
        log.info("Step 11: 勾选 None checkbox，点击 Continue")
        home.check_checkbox_by_label("None")
        log.info("已勾选 None checkbox")

        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Continue")

        # ── Step 12: 点击 No, I do not have any heart conditions or high blood pressure ──
        log.info('Step 12: 点击 "No, I do not have any heart conditions or high blood pressure"')
        home.wait_for_visible_button("No, I do not have any heart conditions or high blood pressure")
        home.click_button_by_text("No, I do not have any heart conditions or high blood pressure")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 No, I do not have any heart conditions or high blood pressure")

        # ── Step 13: 勾选 I am not currently taking any of the above checkbox，点击 Continue ──
        log.info('Step 13: 勾选 "I am not currently taking any of the above" checkbox')
        home.check_checkbox_by_label("I am not currently taking any of the above")
        log.info("已勾选 I am not currently taking any of the above checkbox")

        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Continue")

        # ── Step 14: 点击 No 按钮，循环3次 ──
        log.info("Step 14: 循环3次点击 No")
        for i in range(3):
            loop_num = i + 1
            log.info(f'  Step 14.{loop_num}: 点击 No')
            home.wait_for_visible_button("No")
            home.click_button_by_text("No")
            try:
                home.wait_for_visible_button("No", timeout=10000)
            except Exception:
                page.wait_for_selector("button:visible", timeout=10000)

        # ── Step 15: 点击 No, I have never had a seizure ──
        log.info('Step 15: 点击 "No, I have never had a seizure"')
        home.wait_for_visible_button("No, I have never had a seizure")
        home.click_button_by_text("No, I have never had a seizure")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 No, I have never had a seizure")

        # ── Step 16: 点击 No, I have never had an eating disorder ──
        log.info('Step 16: 点击 "No, I have never had an eating disorder"')
        home.wait_for_visible_button("No, I have never had an eating disorder")
        home.click_button_by_text("No, I have never had an eating disorder")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 No, I have never had an eating disorder")

        # ── Step 17: 点击 Search by Postal Code or Name 输入框 → 点击药房卡片 → Choose → Confirm ──
        log.info("Step 17: 搜索药房 → 选择药房 → Choose → Confirm")
        # 点击搜索输入框（使用 placeholder 定位）
        search_input = page.locator('input.n-input__input-el[placeholder="Search by Postal Code or Name"]')
        search_input.first.wait_for(state="visible", timeout=15000)
        search_input.first.click()
        log.info("已点击 Search by Postal Code or Name 输入框")

        # 点击第一个药房卡片
        page.locator('div.cursor-pointer.rounded-2xl').first.wait_for(state="visible", timeout=15000)
        page.locator('div.cursor-pointer.rounded-2xl').first.click()
        log.info("已点击第一个药房卡片")
        page.wait_for_selector("button:visible", timeout=15000)

        # 点击 Choose 按钮
        home.wait_for_visible_button("Choose")
        home.click_button_by_text("Choose")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Choose")

        # 点击 Confirm 按钮
        home.wait_for_visible_button("Confirm")
        home.click_button_by_text("Confirm")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Confirm")

        # ── Step 18: 输入 Full name / Phone number / Email / Relationship，点击 Continue ──
        log.info("Step 18: 输入联系人信息")
        timestamp = int(time.time())
        full_name = f"autotest{timestamp}"

        # 等待页面加载完成（Emergency contact 页面）
        page.wait_for_selector('input.n-input__input-el[placeholder="Full name"]', timeout=15000)

        home.fill_by_placeholder("Full name", full_name)
        log.info(f"已输入 Full name: {full_name}")

        home.fill_by_placeholder("Phone number", "1 2334534454")
        log.info("已输入 Phone number: 1 2334534454")

        home.fill_by_placeholder("Email", "autotest@gmail.com")
        log.info("已输入 Email: autotest@gmail.com")

        home.fill_by_placeholder("Relationship", "mother")
        log.info("已输入 Relationship: mother")

        home.click_button_by_text("Continue")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Continue")

        # ── Step 19: 点击 Start the Assessment ──
        log.info('Step 19: 点击 "Start the Assessment"')
        home.wait_for_visible_button("Start the Assessment")
        home.click_button_by_text("Start the Assessment")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Start the Assessment")

        log.info("TC-REG-001-3 | 填写问卷 ✅")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 四、添加详细问卷
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_register_assessment(self, page: Page):
        """
        TC-REG-001-4: 添加详细问卷

        步骤:
            1. 登录（使用用例一注册的账号密码），点击 Okay 按钮
            2. 点击 Start the Assessment 按钮，跳转到下一页
            3. 点击 ASRS-V1.1 卡片 → Start Assessment → Next
            4. 依次点击页面上所有的 Never 按钮，最后点击 Complete
            5. 点击 PHQ-9 卡片 → Start Assessment
            6. 依次点击页面上所有的 Not at all 按钮，最后点击 Complete
            7. 点击 GAD-7 卡片 → Start Assessment
            8. 依次点击页面上所有的 Not at all 按钮，最后点击 Complete
            9. 点击 FUNCTIONAL IMPAIRMENT 卡片
            10. 勾选 Education checkbox，断言页面存在 Please explain 提示文字
            11. 在文本输入框中输入50个字符的英文，点击 Complete
            12. 点击 Start my care 按钮
            13. 登录（使用用例一注册的账号密码），断言登录成功

        """
        log.info("TC-REG-001-4 | 开始添加详细问卷")

        # ── Step 1: 登录，点击 Okay ──
        email = TestRegister._registered_email
        password = TestRegister._registered_password
        home = PortalHomePage(page)
        home.open()
        home.click_sign_in()

        page.locator('input[placeholder="Email address"]').fill(email)
        log.info(f"已输入邮箱: {email}")
        page.locator('input[placeholder="Password"]').fill(password)
        log.info("已输入密码")
        page.click('button:has-text("Continue")')
        # 登录后根据账号状态可能跳转到不同页面，等待任意页面稳定
        page.wait_for_selector("button:visible", timeout=20000)
        log.info(f"登录成功，当前 URL: {page.url}")

        # 点击 Okay 按钮（如果存在）
        try:
            okay_btn = page.locator('button:visible').get_by_text("Okay", exact=False).first
            okay_btn.wait_for(state="visible", timeout=8000)
            okay_btn.click()
            page.wait_for_selector("button:visible", timeout=15000)
            log.info("已点击 Okay")
        except Exception:
            log.info("未检测到 Okay 按钮，跳过")

        # ── Step 2: 点击 Start the Assessment ──
        log.info('Step 2: 点击 "Start the Assessment"')
        home.wait_for_visible_button("Start the Assessment")
        home.click_button_by_text("Start the Assessment")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Start the Assessment")

        # ── Step 3: 点击 ASRS-V1.1 卡片 → Start Assessment → Next ──
        log.info("Step 3: 点击 ASRS-V1.1 卡片")
        asrs_card = page.locator('div.cursor-pointer').filter(has_text="ASRS-V1.1").first
        asrs_card.wait_for(state="visible", timeout=15000)
        asrs_card.click()
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 ASRS-V1.1 卡片")

        log.info('Step 3b: 点击 "Start Assessment"')
        home.wait_for_visible_button("Start Assessment")
        home.click_button_by_text("Start Assessment")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Start Assessment")

        log.info('Step 3c: 点击 "Next"')
        home.wait_for_visible_button("Next")
        home.click_button_by_text("Next")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Next")

        # ── Step 4: 依次点击所有 Never 按钮，最后点击 Complete ──
        log.info("Step 4: 依次点击所有 Never 按钮")
        max_rounds = 30  # 最多处理30题，防止无限循环
        for round_num in range(1, max_rounds + 1):
            # 检查是否已出现 Complete 按钮（题目做完）
            complete_btn = page.locator('button:visible').get_by_text("Complete", exact=False).first
            try:
                complete_btn.wait_for(state="visible", timeout=2000)
                log.info(f"  第 {round_num} 轮：检测到 Complete 按钮，准备点击")
                complete_btn.click()
                page.wait_for_selector("button:visible", timeout=15000)
                log.info("已点击 Complete")
                break
            except Exception:
                pass  # 尚未出现 Complete，继续点击 Never

            # 点击本页所有可见的 Never 按钮
            never_btns = page.locator('button:visible').filter(has_text="Never")
            count = never_btns.count()
            if count == 0:
                # 没有 Never 也没有 Complete，等待页面加载
                log.warning(f"  第 {round_num} 轮：未找到 Never 或 Complete 按钮，等待 2s 后重试")
                page.wait_for_timeout(2000)
                continue

            log.info(f"  第 {round_num} 轮：找到 {count} 个 Never 按钮，依次点击")
            for idx in range(count):
                # 每次重新获取，避免 DOM 更新导致定位失效
                btn = page.locator('button:visible').filter(has_text="Never").nth(idx)
                try:
                    btn.click(timeout=5000)
                    page.wait_for_timeout(300)
                except Exception:
                    log.warning(f"    点击第 {idx + 1} 个 Never 按钮失败，跳过")

            # 点击完所有 Never 后等待页面稳定
            page.wait_for_timeout(500)
        else:
            log.warning("Step 4: 已达到最大轮数限制，未检测到 Complete 按钮")

        log.info("TC-REG-001-4 | 添加详细问卷 ✅")

            # ── Step 5: 点击 PHQ-9 卡片 → Start Assessment ──
        log.info("Step 5: 点击 PHQ-9 卡片")
        phq_card = page.locator('div.cursor-pointer').filter(has_text="PHQ-9").first
        phq_card.wait_for(state="visible", timeout=15000)
        phq_card.click()
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 PHQ-9 卡片")

        log.info('Step 5b: 点击 "Start Assessment"')
        home.wait_for_visible_button("Start Assessment")
        home.click_button_by_text("Start Assessment")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Start Assessment (PHQ-9)")

        # ── Step 6: 依次点击所有 Not at all 按钮，最后点击 Complete ──
        log.info("Step 6: 依次点击所有 Not at all 按钮")
        max_rounds = 30
        for round_num in range(1, max_rounds + 1):
            complete_btn = page.locator('button:visible').get_by_text("Complete", exact=False).first
            try:
                complete_btn.wait_for(state="visible", timeout=2000)
                log.info(f"  第 {round_num} 轮：检测到 Complete 按钮，准备点击")
                complete_btn.click()
                page.wait_for_selector("button:visible", timeout=15000)
                log.info("已点击 Complete (PHQ-9)")
                break
            except Exception:
                pass

            not_at_all_btns = page.locator('button:visible').filter(has_text="Not at all")
            count = not_at_all_btns.count()
            if count == 0:
                log.warning(f"  第 {round_num} 轮：未找到 Not at all 或 Complete 按钮，等待 2s 后重试")
                page.wait_for_timeout(2000)
                continue

            log.info(f"  第 {round_num} 轮：找到 {count} 个 Not at all 按钮，依次点击")
            for idx in range(count):
                btn = page.locator('button:visible').filter(has_text="Not at all").nth(idx)
                try:
                    btn.click(timeout=5000)
                    page.wait_for_timeout(300)
                except Exception:
                    log.warning(f"    点击第 {idx + 1} 个 Not at all 按钮失败，跳过")

            page.wait_for_timeout(500)
        else:
            log.warning("Step 6: 已达到最大轮数限制，未检测到 Complete 按钮")

        # ── Step 7: 点击 GAD-7 卡片 → Start Assessment ──
        log.info("Step 7: 点击 GAD-7 卡片")
        gad_card = page.locator('div.cursor-pointer').filter(has_text="GAD-7").first
        gad_card.wait_for(state="visible", timeout=15000)
        gad_card.click()
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 GAD-7 卡片")

        log.info('Step 7b: 点击 "Start Assessment"')
        home.wait_for_visible_button("Start Assessment")
        home.click_button_by_text("Start Assessment")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Start Assessment (GAD-7)")

        # ── Step 8: 依次点击所有 Not at all 按钮，最后点击 Complete ──
        log.info("Step 8: 依次点击所有 Not at all 按钮")
        for round_num in range(1, max_rounds + 1):
            complete_btn = page.locator('button:visible').get_by_text("Complete", exact=False).first
            try:
                complete_btn.wait_for(state="visible", timeout=2000)
                log.info(f"  第 {round_num} 轮：检测到 Complete 按钮，准备点击")
                complete_btn.click()
                page.wait_for_selector("button:visible", timeout=15000)
                log.info("已点击 Complete (GAD-7)")
                break
            except Exception:
                pass

            not_at_all_btns = page.locator('button:visible').filter(has_text="Not at all")
            count = not_at_all_btns.count()
            if count == 0:
                log.warning(f"  第 {round_num} 轮：未找到 Not at all 或 Complete 按钮，等待 2s 后重试")
                page.wait_for_timeout(2000)
                continue

            log.info(f"  第 {round_num} 轮：找到 {count} 个 Not at all 按钮，依次点击")
            for idx in range(count):
                btn = page.locator('button:visible').filter(has_text="Not at all").nth(idx)
                try:
                    btn.click(timeout=5000)
                    page.wait_for_timeout(300)
                except Exception:
                    log.warning(f"    点击第 {idx + 1} 个 Not at all 按钮失败，跳过")

            page.wait_for_timeout(500)
        else:
            log.warning("Step 8: 已达到最大轮数限制，未检测到 Complete 按钮")

        # ── Step 9: 点击 FUNCTIONAL IMPAIRMENT 卡片 ──
        log.info("Step 9: 点击 FUNCTIONAL IMPAIRMENT 卡片")
        fi_card = page.locator('div.cursor-pointer').filter(has_text="FUNCTIONAL IMPAIRMENT").first
        fi_card.wait_for(state="visible", timeout=15000)
        fi_card.click()
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 FUNCTIONAL IMPAIRMENT 卡片")

        # ── Step 10: 勾选 Education checkbox，断言提示文字 ──
        log.info('Step 10: 勾选 "Education" checkbox')
        home.check_checkbox_by_label("Education")
        log.info("已勾选 Education checkbox")

        # 断言页面存在 Please explain how each area you ticked above is affected by your ADHD symptoms
        assertion_text = "Please explain how each area you ticked above is affected by your ADHD symptoms"
        log.info(f'Step 10b: 断言页面存在 "{assertion_text}"')
        page.get_by_text(assertion_text, exact=False).wait_for(state="visible", timeout=10000)
        log.info(f"断言成功 ✅ 页面存在: {assertion_text}")

        # ── Step 11: 在文本输入框中输入50个字符的英文，点击 Complete ──
        log.info("Step 11: 在文本输入框中输入50个字符的英文")
        # 等待文本输入框出现
        text_input = page.locator('textarea, input[type="text"]').filter(has=page.get_by_text(assertion_text, exact=False)).first
        # 如果 textarea/input 未能通过 filter 定位，尝试直接找页面上唯一的 textarea 或可见的文本输入框
        try:
            text_input.wait_for(state="visible", timeout=5000)
        except Exception:
            # 兜底：定位页面上的 textarea 或长文本输入框
            text_input = page.locator('textarea.n-input__textarea-el, textarea:visible').first
            text_input.wait_for(state="visible", timeout=10000)

        input_text = "a" * 50  # 50个英文字符
        text_input.fill(input_text)
        log.info(f"已输入文本: {input_text}")

        # 点击 Complete
        home.wait_for_visible_button("Complete")
        home.click_button_by_text("Complete")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Complete (FUNCTIONAL IMPAIRMENT)")

        # ── Step 12: 点击 Start my care ──
        log.info('Step 12: 点击 "Start my care"')
        home.wait_for_visible_button("Start my care")
        home.click_button_by_text("Start my care")
        page.wait_for_selector("button:visible", timeout=15000)
        log.info("已点击 Start my care")

        # ── Step 13: 登录（使用用例一注册的账号密码），断言登录成功 ──
        log.info("Step 13: 再次登录，断言登录成功")
        email = TestRegister._registered_email
        password = TestRegister._registered_password
        home = PortalHomePage(page)
        home.open()
        #home.click_sign_in()

        # 断言登录成功：页面出现 "Hi," 问候语
        assert home.is_login_success(), "登录失败，未检测到 Hi, 问候语"
        log.info("断言成功 ✅ 登录成功")

        log.info("TC-REG-001-4 | 添加详细问卷 ✅")