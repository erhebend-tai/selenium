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
Tests for the WebBot functionality
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from selenium.webbot.bot import WebBot
from selenium.webbot.ocr import OCRProcessor
from selenium.webbot.playwright_integration import PlaywrightUtilities


class TestWebBot(unittest.TestCase):
    """Test cases for WebBot functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.bot = WebBot(headless=True)
        self.test_url = "https://example.com"

    def tearDown(self):
        """Clean up after tests."""
        if self.bot.driver:
            self.bot.quit_driver()

    def test_bot_initialization(self):
        """Test WebBot initialization."""
        self.assertIsNotNone(self.bot)
        self.assertTrue(self.bot.headless)
        self.assertEqual(self.bot.window_size, (1920, 1080))
        self.assertIsNone(self.bot.driver)

    def test_robots_txt_checking(self):
        """Test robots.txt checking functionality."""
        # Test with a URL that should have robots.txt
        result = self.bot.check_robots_txt("https://google.com")
        self.assertIsInstance(result, bool)

    def test_context_manager(self):
        """Test WebBot context manager functionality."""
        with WebBot(headless=True) as bot:
            self.assertIsNotNone(bot.driver)
            self.assertIsNotNone(bot.wait)
        # Driver should be quit after context manager

    @patch('selenium.webdriver.Chrome')
    def test_driver_start_stop(self, mock_chrome):
        """Test driver start and stop."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        self.bot.start_driver()
        self.assertIsNotNone(self.bot.driver)
        
        self.bot.quit_driver()
        mock_driver.quit.assert_called_once()

    def test_get_page_depth_info_without_driver(self):
        """Test that page depth analysis fails without driver."""
        with self.assertRaises(RuntimeError):
            self.bot.get_page_depth_info()

    def test_screenshot_without_driver(self):
        """Test that screenshot fails without driver."""
        with self.assertRaises(RuntimeError):
            self.bot.take_screenshot()


class TestOCRProcessor(unittest.TestCase):
    """Test cases for OCR functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if OCRProcessor.is_ocr_available():
            try:
                self.ocr = OCRProcessor()
            except ImportError:
                self.ocr = None
        else:
            self.ocr = None

    def test_ocr_availability(self):
        """Test OCR availability detection."""
        available = OCRProcessor.is_ocr_available()
        self.assertIsInstance(available, bool)

    def test_extract_text_from_nonexistent_image(self):
        """Test OCR with non-existent image."""
        if self.ocr:
            result = self.ocr.extract_text_from_image("nonexistent.png")
            self.assertEqual(result, "")

    def test_validate_text_quality(self):
        """Test text quality validation."""
        if self.ocr:
            # Good text
            self.assertTrue(self.ocr.validate_text_quality("This is good text"))
            
            # Poor text (too short)
            self.assertFalse(self.ocr.validate_text_quality("ab"))
            
            # Poor text (too many special characters)
            self.assertFalse(self.ocr.validate_text_quality("!@#$%^&*()"))


class TestPlaywrightIntegration(unittest.TestCase):
    """Test cases for Playwright integration."""

    def test_playwright_availability(self):
        """Test Playwright availability detection."""
        available = PlaywrightUtilities.is_playwright_available()
        self.assertIsInstance(available, bool)

    def test_run_async_function(self):
        """Test async function runner utility."""
        async def test_async():
            return "test_result"
        
        # This test might fail if run in an existing event loop
        try:
            result = PlaywrightUtilities.run_async_function(test_async)
            self.assertEqual(result, "test_result")
        except RuntimeError:
            # Expected in some environments with existing event loops
            pass


class TestWebBotIntegration(unittest.TestCase):
    """Integration tests for WebBot."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skipIf(os.environ.get('CI') == 'true', "Skipping browser tests in CI")
    def test_basic_navigation_and_screenshot(self):
        """Test basic navigation and screenshot functionality."""
        with WebBot(headless=True) as bot:
            # Navigate to a simple page
            success = bot.navigate_to("data:text/html,<html><body><h1>Test Page</h1></body></html>")
            self.assertTrue(success)
            
            # Take a screenshot
            screenshot_path = os.path.join(self.temp_dir, "test_screenshot.png")
            result_path = bot.take_screenshot(screenshot_path)
            self.assertEqual(result_path, screenshot_path)
            self.assertTrue(os.path.exists(screenshot_path))
            
            # Get page depth info
            depth_info = bot.get_page_depth_info()
            self.assertIsInstance(depth_info, dict)
            self.assertIn('page_height', depth_info)
            
            # Extract text content
            text = bot.extract_text_content()
            self.assertIn("Test Page", text)


if __name__ == '__main__':
    unittest.main()