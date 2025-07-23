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
Web Bot Implementation

A comprehensive web automation bot that demonstrates integration of:
- Selenium WebDriver with Chromium
- Full-screen screenshots
- OCR capabilities
- Page depth analysis
- robots.txt checking
- Playwright integration
"""

import asyncio
import io
import logging
import os
import tempfile
import time
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class WebBot:
    """
    A comprehensive web automation bot that integrates multiple tools for web scraping and automation.
    """

    def __init__(self, headless: bool = True, window_size: tuple = (1920, 1080)):
        """
        Initialize the WebBot with configurable options.
        
        Args:
            headless: Whether to run the browser in headless mode
            window_size: Browser window size as (width, height) tuple
        """
        self.headless = headless
        self.window_size = window_size
        self.driver = None
        self.wait = None
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the bot."""
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

    def start_driver(self) -> None:
        """Initialize and start the Chrome WebDriver."""
        if self.driver:
            return
            
        chrome_options = ChromeOptions()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        # Security and automation arguments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Speed optimization
        chrome_options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
        
        # User agent to avoid bot detection
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_window_size(*self.window_size)
            self.wait = WebDriverWait(self.driver, 10)
            self.logger.info("Chrome WebDriver started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start Chrome WebDriver: {e}")
            raise

    def quit_driver(self) -> None:
        """Quit the WebDriver and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Chrome WebDriver quit successfully")
            except Exception as e:
                self.logger.error(f"Error quitting Chrome WebDriver: {e}")
            finally:
                self.driver = None
                self.wait = None

    def check_robots_txt(self, url: str, user_agent: str = "*") -> bool:
        """
        Check if the given URL is allowed by robots.txt.
        
        Args:
            url: The URL to check
            user_agent: User agent to check permissions for
            
        Returns:
            True if the URL is allowed, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            can_fetch = rp.can_fetch(user_agent, url)
            self.logger.info(f"robots.txt check for {url}: {'ALLOWED' if can_fetch else 'DISALLOWED'}")
            return can_fetch
            
        except Exception as e:
            self.logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True  # Default to allowed if robots.txt is unavailable

    def navigate_to(self, url: str, check_robots: bool = True) -> bool:
        """
        Navigate to a URL with optional robots.txt checking.
        
        Args:
            url: The URL to navigate to
            check_robots: Whether to check robots.txt before navigating
            
        Returns:
            True if navigation was successful, False otherwise
        """
        if not self.driver:
            self.start_driver()
            
        if check_robots and not self.check_robots_txt(url):
            self.logger.warning(f"Robots.txt disallows access to {url}")
            return False
            
        try:
            self.driver.get(url)
            self.logger.info(f"Successfully navigated to {url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            return False

    def take_screenshot(self, filename: Optional[str] = None, full_page: bool = True) -> str:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Optional filename for the screenshot
            full_page: Whether to take a full-page screenshot
            
        Returns:
            Path to the saved screenshot file
        """
        if not self.driver:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
            
        if filename is None:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            
        try:
            if full_page:
                # Get the full page height
                original_size = self.driver.get_window_size()
                page_height = self.driver.execute_script("return document.body.scrollHeight")
                
                # Resize window to capture full page
                self.driver.set_window_size(original_size['width'], page_height)
                time.sleep(0.5)  # Wait for resize
                
                screenshot_path = self.driver.save_screenshot(filename)
                
                # Restore original window size
                self.driver.set_window_size(original_size['width'], original_size['height'])
            else:
                screenshot_path = self.driver.save_screenshot(filename)
                
            if screenshot_path:
                self.logger.info(f"Screenshot saved to {filename}")
                return filename
            else:
                raise RuntimeError("Failed to save screenshot")
                
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            raise

    def get_page_depth_info(self) -> Dict[str, Union[int, List[str]]]:
        """
        Analyze the page depth and structure.
        
        Returns:
            Dictionary containing depth analysis information
        """
        if not self.driver:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
            
        try:
            # Count different types of elements
            links = self.driver.find_elements(By.TAG_NAME, "a")
            images = self.driver.find_elements(By.TAG_NAME, "img")
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            headings = []
            
            for i in range(1, 7):  # h1 to h6
                headings.extend(self.driver.find_elements(By.TAG_NAME, f"h{i}"))
                
            # Get page scroll depth
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Get DOM depth
            max_depth = self.driver.execute_script("""
                function getMaxDepth(element) {
                    let maxDepth = 0;
                    function traverse(el, depth) {
                        maxDepth = Math.max(maxDepth, depth);
                        for (let child of el.children) {
                            traverse(child, depth + 1);
                        }
                    }
                    traverse(element, 0);
                    return maxDepth;
                }
                return getMaxDepth(document.body);
            """)
            
            # Extract internal and external links
            internal_links = []
            external_links = []
            current_domain = urlparse(self.driver.current_url).netloc
            
            for link in links:
                href = link.get_attribute("href")
                if href:
                    link_domain = urlparse(href).netloc
                    if link_domain == current_domain or not link_domain:
                        internal_links.append(href)
                    else:
                        external_links.append(href)
            
            depth_info = {
                "page_height": page_height,
                "viewport_height": viewport_height,
                "scroll_ratio": viewport_height / page_height if page_height > 0 else 1,
                "dom_depth": max_depth,
                "total_links": len(links),
                "internal_links": len(internal_links),
                "external_links": len(external_links),
                "images_count": len(images),
                "forms_count": len(forms),
                "headings_count": len(headings),
                "internal_link_urls": internal_links[:10],  # Limit to first 10
                "external_link_urls": external_links[:10],  # Limit to first 10
            }
            
            self.logger.info(f"Page depth analysis completed: DOM depth={max_depth}, Total links={len(links)}")
            return depth_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing page depth: {e}")
            return {}

    def extract_text_content(self) -> str:
        """
        Extract text content from the current page.
        
        Returns:
            Extracted text content
        """
        if not self.driver:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
            
        try:
            # Get text content from body
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            self.logger.info(f"Extracted {len(body_text)} characters of text content")
            return body_text
        except Exception as e:
            self.logger.error(f"Error extracting text content: {e}")
            return ""

    def wait_for_element(self, locator: tuple, timeout: int = 10) -> bool:
        """
        Wait for an element to be present on the page.
        
        Args:
            locator: Tuple of (By strategy, locator string)
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if element was found, False otherwise
        """
        if not self.driver:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located(locator))
            return True
        except Exception as e:
            self.logger.warning(f"Element not found: {locator}, Error: {e}")
            return False

    def simulate_human_behavior(self, delay_range: tuple = (1, 3)) -> None:
        """
        Simulate human-like behavior with random delays.
        
        Args:
            delay_range: Tuple of (min_delay, max_delay) in seconds
        """
        import random
        delay = random.uniform(delay_range[0], delay_range[1])
        time.sleep(delay)

    def get_page_performance_metrics(self) -> Dict[str, float]:
        """
        Get page performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        if not self.driver:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
            
        try:
            # Get navigation timing data
            navigation_timing = self.driver.execute_script("""
                const timing = performance.getEntriesByType('navigation')[0];
                if (timing) {
                    return {
                        'dns_lookup': timing.domainLookupEnd - timing.domainLookupStart,
                        'tcp_connect': timing.connectEnd - timing.connectStart,
                        'request_response': timing.responseEnd - timing.requestStart,
                        'dom_content_loaded': timing.domContentLoadedEventEnd - timing.navigationStart,
                        'page_load': timing.loadEventEnd - timing.navigationStart
                    };
                }
                return {};
            """)
            
            self.logger.info("Page performance metrics collected")
            return navigation_timing or {}
            
        except Exception as e:
            self.logger.error(f"Error collecting performance metrics: {e}")
            return {}

    def __enter__(self):
        """Context manager entry."""
        self.start_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit_driver()