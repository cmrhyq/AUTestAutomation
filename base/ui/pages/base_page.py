"""
UI 测试基础页面类

该模块实现 Page Object Model (POM) 模式的基础页面类，提供所有页面对象的通用功能。
包括页面导航、元素等待、常用操作、截图和日志记录等功能。
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

from config.settings import Settings
from core.log.logger import TestLogger
from core.allure.allure_helper import AllureHelper


class BasePage:
    """
    基础页面类
    
    实现 Page Object Model 模式，提供所有页面对象的通用功能：
    - 页面导航
    - 智能元素等待机制
    - 常用页面操作（点击、填充、获取文本等）
    - 自动截图功能
    - 集成日志记录
    
    所有具体的页面对象类都应该继承此类。
    """
    
    def __init__(self, page: Page, logger: Optional[logging.Logger] = None):
        """
        初始化基础页面对象
        
        Args:
            page: Playwright Page 对象
            logger: 日志记录器，如果为 None 则创建默认日志记录器
        """
        self.page = page
        self.logger = logger or TestLogger.get_logger(self.__class__.__name__)
        
        # 设置默认超时时间
        self.page.set_default_timeout(Settings.BROWSER_TIMEOUT)
        
        self.logger.debug(f"Initialized {self.__class__.__name__}")
    
    def navigate(self, url: str, wait_until: str = "domcontentloaded") -> None:
        """
        导航到指定 URL
        
        Args:
            url: 目标 URL
            wait_until: 等待条件，可选值：
                - 'load': 等待 load 事件触发
                - 'domcontentloaded': 等待 DOMContentLoaded 事件触发（默认）
                - 'networkidle': 等待网络空闲
                - 'commit': 等待网络响应接收完成
        
        使用示例:
            page.navigate("https://example.com")
            page.navigate("https://example.com/login", wait_until="load")
        """
        try:
            self.logger.info(f"Navigating to URL: {url}")
            
            with AllureHelper.step(f"Navigate to {url}"):
                self.page.goto(url, wait_until=wait_until, timeout=Settings.PAGE_LOAD_TIMEOUT)
            
            self.logger.info(f"Successfully navigated to: {url}")
            
        except PlaywrightTimeoutError as e:
            self.logger.error(f"Timeout while navigating to {url}: {e}")
            self._capture_failure_screenshot(f"navigation_timeout_{self._get_timestamp()}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            self._capture_failure_screenshot(f"navigation_error_{self._get_timestamp()}")
            raise
    
    def wait_for_element(
        self, 
        selector: str, 
        timeout: Optional[int] = None,
        state: str = "visible"
    ) -> Locator:
        """
        等待元素出现并返回定位器
        
        实现智能等待机制，在元素可用之前自动等待。
        
        Args:
            selector: 元素选择器（CSS、XPath 等）
            timeout: 超时时间（毫秒），如果为 None 则使用默认超时
            state: 元素状态，可选值：
                - 'attached': 元素已附加到 DOM
                - 'detached': 元素已从 DOM 分离
                - 'visible': 元素可见（默认）
                - 'hidden': 元素隐藏
        
        Returns:
            Locator: Playwright 定位器对象
        
        使用示例:
            element = page.wait_for_element("#login-button")
            element = page.wait_for_element("//button[@id='submit']", timeout=5000)
        """
        if timeout is None:
            timeout = Settings.BROWSER_TIMEOUT
        
        try:
            self.logger.debug(f"Waiting for element: {selector} (state: {state}, timeout: {timeout}ms)")
            
            locator = self.page.locator(selector)
            locator.wait_for(state=state, timeout=timeout)
            
            self.logger.debug(f"Element found: {selector}")
            return locator
            
        except PlaywrightTimeoutError as e:
            self.logger.error(f"Timeout waiting for element: {selector} (state: {state})")
            self._capture_failure_screenshot(f"element_timeout_{self._get_timestamp()}")
            raise
        except Exception as e:
            self.logger.error(f"Error waiting for element {selector}: {e}")
            self._capture_failure_screenshot(f"element_error_{self._get_timestamp()}")
            raise
    
    def click(
        self, 
        selector: str, 
        timeout: Optional[int] = None,
        force: bool = False,
        wait_before_click: bool = True
    ) -> None:
        """
        点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            force: 是否强制点击（跳过可操作性检查）
            wait_before_click: 是否在点击前等待元素可见
        
        使用示例:
            page.click("#submit-button")
            page.click("button.primary", force=True)
        """
        try:
            self.logger.info(f"Clicking element: {selector}")
            
            with AllureHelper.step(f"Click element: {selector}"):
                if wait_before_click:
                    locator = self.wait_for_element(selector, timeout=timeout)
                else:
                    locator = self.page.locator(selector)
                
                locator.click(force=force, timeout=timeout or Settings.BROWSER_TIMEOUT)
            
            self.logger.info(f"Successfully clicked: {selector}")
            
        except PlaywrightTimeoutError as e:
            self.logger.error(f"Timeout while clicking element: {selector}")
            self._capture_failure_screenshot(f"click_timeout_{self._get_timestamp()}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to click element {selector}: {e}")
            self._capture_failure_screenshot(f"click_error_{self._get_timestamp()}")
            raise
    
    def fill(
        self, 
        selector: str, 
        text: str, 
        timeout: Optional[int] = None,
        clear_first: bool = True
    ) -> None:
        """
        填充文本到输入框
        
        Args:
            selector: 元素选择器
            text: 要填充的文本
            timeout: 超时时间（毫秒）
            clear_first: 是否先清空输入框
        
        使用示例:
            page.fill("#username", "testuser")
            page.fill("input[name='email']", "test@example.com", clear_first=False)
        """
        try:
            self.logger.info(f"Filling element {selector} with text: {text}")
            
            with AllureHelper.step(f"Fill '{selector}' with '{text}'"):
                locator = self.wait_for_element(selector, timeout=timeout)
                
                if clear_first:
                    locator.clear(timeout=timeout or Settings.BROWSER_TIMEOUT)
                
                locator.fill(text, timeout=timeout or Settings.BROWSER_TIMEOUT)
            
            self.logger.info(f"Successfully filled {selector}")
            
        except PlaywrightTimeoutError as e:
            self.logger.error(f"Timeout while filling element: {selector}")
            self._capture_failure_screenshot(f"fill_timeout_{self._get_timestamp()}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to fill element {selector}: {e}")
            self._capture_failure_screenshot(f"fill_error_{self._get_timestamp()}")
            raise
    
    def get_text(
        self, 
        selector: str, 
        timeout: Optional[int] = None
    ) -> str:
        """
        获取元素的文本内容
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            str: 元素的文本内容
        
        使用示例:
            text = page.get_text("#welcome-message")
            error_msg = page.get_text(".error-message")
        """
        try:
            self.logger.debug(f"Getting text from element: {selector}")
            
            locator = self.wait_for_element(selector, timeout=timeout)
            text = locator.inner_text(timeout=timeout or Settings.BROWSER_TIMEOUT)
            
            self.logger.debug(f"Got text from {selector}: {text}")
            return text
            
        except PlaywrightTimeoutError as e:
            self.logger.error(f"Timeout while getting text from element: {selector}")
            self._capture_failure_screenshot(f"get_text_timeout_{self._get_timestamp()}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get text from element {selector}: {e}")
            self._capture_failure_screenshot(f"get_text_error_{self._get_timestamp()}")
            raise
    
    def get_attribute(
        self, 
        selector: str, 
        attribute: str,
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """
        获取元素的属性值
        
        Args:
            selector: 元素选择器
            attribute: 属性名称
            timeout: 超时时间（毫秒）
            
        Returns:
            Optional[str]: 属性值，如果属性不存在则返回 None
            
        使用示例:
            href = page.get_attribute("a.link", "href")
            value = page.get_attribute("input#email", "value")
        """
        try:
            self.logger.debug(f"Getting attribute '{attribute}' from element: {selector}")
            
            locator = self.wait_for_element(selector, timeout=timeout)
            value = locator.get_attribute(attribute, timeout=timeout or Settings.BROWSER_TIMEOUT)
            
            self.logger.debug(f"Got attribute '{attribute}' from {selector}: {value}")
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to get attribute '{attribute}' from {selector}: {e}")
            self._capture_failure_screenshot(f"get_attribute_error_{self._get_timestamp()}")
            raise
    
    def is_visible(self, selector: str, timeout: int = 1000) -> bool:
        """
        检查元素是否可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒），默认 1 秒
            
        Returns:
            bool: 元素是否可见
            
        使用示例:
            if page.is_visible("#error-message"):
                print("Error message is displayed")
        """
        try:
            locator = self.page.locator(selector)
            return locator.is_visible(timeout=timeout)
        except Exception:
            return False
    
    def is_enabled(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        检查元素是否启用
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 元素是否启用
            
        使用示例:
            if page.is_enabled("#submit-button"):
                page.click("#submit-button")
        """
        try:
            locator = self.wait_for_element(selector, timeout=timeout)
            return locator.is_enabled(timeout=timeout or Settings.BROWSER_TIMEOUT)
        except Exception:
            return False
    
    def wait_for_url(
        self, 
        url_pattern: Union[str, object], 
        timeout: Optional[int] = None
    ) -> None:
        """
        等待 URL 匹配指定模式
        
        Args:
            url_pattern: URL 模式（字符串或正则表达式）
            timeout: 超时时间（毫秒）
            
        使用示例:
            page.wait_for_url("**/dashboard")
            page.wait_for_url(re.compile(r".*/profile/\d+"))
        """
        try:
            self.logger.info(f"Waiting for URL pattern: {url_pattern}")
            self.page.wait_for_url(url_pattern, timeout=timeout or Settings.BROWSER_TIMEOUT)
            self.logger.info(f"URL matched pattern: {url_pattern}")
        except PlaywrightTimeoutError as e:
            self.logger.error(f"Timeout waiting for URL pattern: {url_pattern}")
            self._capture_failure_screenshot(f"url_timeout_{self._get_timestamp()}")
            raise
    
    def take_screenshot(
        self, 
        name: Optional[str] = None,
        full_page: bool = False,
        attach_to_allure: bool = True
    ) -> bytes:
        """
        截取当前页面的截图
        
        Args:
            name: 截图名称，如果为 None 则自动生成
            full_page: 是否截取整个页面（包括滚动区域）
            attach_to_allure: 是否附加到 Allure 报告
            
        Returns:
            bytes: 截图的字节数据
        
        使用示例:
            screenshot = page.take_screenshot("login_page")
            screenshot = page.take_screenshot(full_page=True)
        """
        try:
            # 生成截图名称
            if name is None:
                name = f"screenshot_{self._get_timestamp()}"
            
            self.logger.info(f"Taking screenshot: {name}")
            
            # 截取截图
            screenshot_bytes = self.page.screenshot(
                full_page=full_page,
                type=Settings.SCREENSHOT_FORMAT
            )
            
            # 保存到文件
            screenshot_dir = Path(Settings.SCREENSHOT_DIR)
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            screenshot_filename = f"{name}.{Settings.SCREENSHOT_FORMAT}"
            screenshot_path = screenshot_dir / screenshot_filename
            
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_bytes)
            
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            
            # 附加到 Allure 报告
            if attach_to_allure:
                AllureHelper.attach_screenshot(screenshot_bytes, name)
            
            return screenshot_bytes
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            raise
    
    def scroll_to_element(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        滚动到指定元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        使用示例:
            page.scroll_to_element("#footer")
        """
        try:
            self.logger.debug(f"Scrolling to element: {selector}")
            locator = self.wait_for_element(selector, timeout=timeout)
            locator.scroll_into_view_if_needed(timeout=timeout or Settings.BROWSER_TIMEOUT)
            self.logger.debug(f"Scrolled to element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to scroll to element {selector}: {e}")
            raise
    
    def select_option(
        self, 
        selector: str, 
        value: Optional[str] = None,
        label: Optional[str] = None,
        index: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> None:
        """
        从下拉列表中选择选项
        
        Args:
            selector: 下拉列表选择器
            value: 选项的 value 属性
            label: 选项的文本内容
            index: 选项的索引
            timeout: 超时时间（毫秒）
            
        注意：value、label、index 三者至少提供一个
        
        使用示例:
            page.select_option("#country", value="US")
            page.select_option("#country", label="United States")
            page.select_option("#country", index=0)
        """
        try:
            self.logger.info(f"Selecting option from {selector}")
            locator = self.wait_for_element(selector, timeout=timeout)
            
            if value is not None:
                locator.select_option(value=value, timeout=timeout or Settings.BROWSER_TIMEOUT)
            elif label is not None:
                locator.select_option(label=label, timeout=timeout or Settings.BROWSER_TIMEOUT)
            elif index is not None:
                locator.select_option(index=index, timeout=timeout or Settings.BROWSER_TIMEOUT)
            else:
                raise ValueError("Must provide value, label, or index")
            
            self.logger.info(f"Successfully selected option from {selector}")
        except Exception as e:
            self.logger.error(f"Failed to select option from {selector}: {e}")
            self._capture_failure_screenshot(f"select_error_{self._get_timestamp()}")
            raise
    
    def check(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        勾选复选框或单选按钮
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        使用示例:
            page.check("#agree-terms")
        """
        try:
            self.logger.info(f"Checking element: {selector}")
            locator = self.wait_for_element(selector, timeout=timeout)
            locator.check(timeout=timeout or Settings.BROWSER_TIMEOUT)
            self.logger.info(f"Successfully checked: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to check element {selector}: {e}")
            self._capture_failure_screenshot(f"check_error_{self._get_timestamp()}")
            raise
    
    def uncheck(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        取消勾选复选框
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        使用示例:
            page.uncheck("#newsletter")
        """
        try:
            self.logger.info(f"Unchecking element: {selector}")
            locator = self.wait_for_element(selector, timeout=timeout)
            locator.uncheck(timeout=timeout or Settings.BROWSER_TIMEOUT)
            self.logger.info(f"Successfully unchecked: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to uncheck element {selector}: {e}")
            self._capture_failure_screenshot(f"uncheck_error_{self._get_timestamp()}")
            raise
    
    def get_current_url(self) -> str:
        """
        获取当前页面 URL
        
        Returns:
            str: 当前页面的 URL
            
        使用示例:
            current_url = page.get_current_url()
        """
        url = self.page.url
        self.logger.debug(f"Current URL: {url}")
        return url
    
    def get_title(self) -> str:
        """
        获取当前页面标题
        
        Returns:
            str: 页面标题
            
        使用示例:
            title = page.get_title()
        """
        title = self.page.title()
        self.logger.debug(f"Page title: {title}")
        return title
    
    def reload(self, timeout: Optional[int] = None) -> None:
        """
        重新加载当前页面
        
        Args:
            timeout: 超时时间（毫秒）
            
        使用示例:
            page.reload()
        """
        try:
            self.logger.info("Reloading page")
            self.page.reload(timeout=timeout or Settings.PAGE_LOAD_TIMEOUT)
            self.logger.info("Page reloaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to reload page: {e}")
            raise
    
    def go_back(self, timeout: Optional[int] = None) -> None:
        """
        返回上一页
        
        Args:
            timeout: 超时时间（毫秒）
            
        使用示例:
            page.go_back()
        """
        try:
            self.logger.info("Going back to previous page")
            self.page.go_back(timeout=timeout or Settings.PAGE_LOAD_TIMEOUT)
            self.logger.info("Navigated back successfully")
        except Exception as e:
            self.logger.error(f"Failed to go back: {e}")
            raise
    
    def go_forward(self, timeout: Optional[int] = None) -> None:
        """
        前进到下一页
        
        Args:
            timeout: 超时时间（毫秒）
            
        使用示例:
            page.go_forward()
        """
        try:
            self.logger.info("Going forward to next page")
            self.page.go_forward(timeout=timeout or Settings.PAGE_LOAD_TIMEOUT)
            self.logger.info("Navigated forward successfully")
        except Exception as e:
            self.logger.error(f"Failed to go forward: {e}")
            raise
    
    def wait_for_load_state(
        self, 
        state: str = "load",
        timeout: Optional[int] = None
    ) -> None:
        """
        等待页面加载到指定状态
        
        Args:
            state: 加载状态，可选值：
                - 'load': 等待 load 事件
                - 'domcontentloaded': 等待 DOMContentLoaded 事件
                - 'networkidle': 等待网络空闲
            timeout: 超时时间（毫秒）
            
        使用示例:
            page.wait_for_load_state("networkidle")
        """
        try:
            self.logger.debug(f"Waiting for load state: {state}")
            self.page.wait_for_load_state(state, timeout=timeout or Settings.PAGE_LOAD_TIMEOUT)
            self.logger.debug(f"Page reached load state: {state}")
        except Exception as e:
            self.logger.error(f"Timeout waiting for load state {state}: {e}")
            raise
    
    def execute_script(self, script: str, *args) -> any:
        """
        执行 JavaScript 代码
        
        Args:
            script: JavaScript 代码
            *args: 传递给脚本的参数
            
        Returns:
            any: 脚本执行结果
            
        使用示例:
            result = page.execute_script("return document.title")
            page.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        """
        try:
            self.logger.debug(f"Executing script: {script[:50]}...")
            result = self.page.evaluate(script, *args)
            self.logger.debug("Script executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Failed to execute script: {e}")
            raise
    
    def _capture_failure_screenshot(self, name: str) -> None:
        """
        捕获失败时的截图（内部方法）
        
        Args:
            name: 截图名称
        """
        try:
            self.take_screenshot(name, full_page=False, attach_to_allure=True)
        except Exception as e:
            self.logger.warning(f"Failed to capture failure screenshot: {e}")
    
    @staticmethod
    def _get_timestamp() -> str:
        """
        获取当前时间戳字符串（内部方法）
        
        Returns:
            str: 格式化的时间戳
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
