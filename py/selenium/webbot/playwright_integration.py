# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Playwright Integration Module

Provides additional browser automation capabilities using Playwright
alongside Selenium for enhanced functionality.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class PlaywrightIntegration:
    """
    Playwright integration for enhanced browser automation capabilities.
    """

    def __init__(self, headless: bool = True):
        """
        Initialize Playwright integration.
        
        Args:
            headless: Whether to run browsers in headless mode
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is not installed. Install it with: pip install playwright && playwright install"
            )
        
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Playwright integration."""
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    async def start_browser(self, browser_type: str = "chromium") -> None:
        """
        Start a Playwright browser.
        
        Args:
            browser_type: Type of browser to start ("chromium", "firefox", "webkit")
        """
        self.playwright = await async_playwright().start()
        
        browser_options = {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--allow-running-insecure-content"
            ]
        }
        
        if browser_type == "chromium":
            self.browser = await self.playwright.chromium.launch(**browser_options)
        elif browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(**browser_options)
        elif browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(**browser_options)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
        
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        self.logger.info(f"Playwright {browser_type} browser started")

    async def close_browser(self) -> None:
        """Close the Playwright browser and clean up resources."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        self.logger.info("Playwright browser closed")

    async def navigate_to(self, url: str) -> None:
        """
        Navigate to a URL using Playwright.
        
        Args:
            url: The URL to navigate to
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        await self.page.goto(url)
        self.logger.info(f"Navigated to {url}")

    async def take_screenshot(self, path: str, full_page: bool = True) -> None:
        """
        Take a screenshot using Playwright.
        
        Args:
            path: Path to save the screenshot
            full_page: Whether to capture the full page
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        await self.page.screenshot(path=path, full_page=full_page)
        self.logger.info(f"Screenshot saved to {path}")

    async def get_page_content(self) -> str:
        """
        Get the page content.
        
        Returns:
            The page HTML content
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        content = await self.page.content()
        self.logger.info(f"Retrieved page content ({len(content)} characters)")
        return content

    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> bool:
        """
        Wait for a selector to be available.
        
        Args:
            selector: CSS selector to wait for
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            True if selector was found, False otherwise
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            self.logger.warning(f"Selector not found: {selector}, Error: {e}")
            return False

    async def get_network_requests(self) -> List[Dict]:
        """
        Get network requests made by the page.
        
        Returns:
            List of network request information
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        requests = []
        
        def handle_request(request):
            requests.append({
                "url": request.url,
                "method": request.method,
                "headers": request.headers,
                "resource_type": request.resource_type
            })
        
        self.page.on("request", handle_request)
        return requests

    async def intercept_responses(self) -> List[Dict]:
        """
        Intercept and analyze HTTP responses.
        
        Returns:
            List of response information
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        responses = []
        
        def handle_response(response):
            responses.append({
                "url": response.url,
                "status": response.status,
                "headers": response.headers,
                "content_type": response.headers.get("content-type", "")
            })
        
        self.page.on("response", handle_response)
        return responses

    async def evaluate_javascript(self, script: str) -> Union[str, int, float, bool, None]:
        """
        Execute JavaScript in the page context.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Result of the JavaScript execution
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        result = await self.page.evaluate(script)
        self.logger.info("JavaScript executed successfully")
        return result

    async def get_accessibility_tree(self) -> Dict:
        """
        Get the accessibility tree of the page.
        
        Returns:
            Accessibility tree information
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        try:
            accessibility_tree = await self.page.accessibility.snapshot()
            self.logger.info("Accessibility tree captured")
            return accessibility_tree or {}
        except Exception as e:
            self.logger.error(f"Error capturing accessibility tree: {e}")
            return {}

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_browser()


class PlaywrightUtilities:
    """
    Utility functions for Playwright operations.
    """

    @staticmethod
    async def run_async_function(func, *args, **kwargs):
        """
        Run an async function in a new event loop if needed.
        
        Args:
            func: Async function to run
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return await func(*args, **kwargs)

    @staticmethod
    def is_playwright_available() -> bool:
        """
        Check if Playwright is available.
        
        Returns:
            True if Playwright is available, False otherwise
        """
        return PLAYWRIGHT_AVAILABLE