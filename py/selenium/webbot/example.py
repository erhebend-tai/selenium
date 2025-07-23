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
Comprehensive Web Bot Example

This example demonstrates all the features of the WebBot including:
- Selenium WebDriver automation with Chromium
- Full-screen screenshots
- OCR text extraction
- Page depth analysis
- robots.txt checking
- Playwright integration
- Performance monitoring
"""

import asyncio
import json
import os
import tempfile
from typing import Dict, List

from selenium.webbot.bot import WebBot
from selenium.webbot.ocr import OCRProcessor
from selenium.webbot.playwright_integration import PlaywrightIntegration, PlaywrightUtilities


class ComprehensiveWebBot:
    """
    A comprehensive web bot that demonstrates all available features.
    """

    def __init__(self, headless: bool = True, output_dir: str = None):
        """
        Initialize the comprehensive web bot.
        
        Args:
            headless: Whether to run browsers in headless mode
            output_dir: Directory to save outputs (screenshots, reports, etc.)
        """
        self.headless = headless
        self.output_dir = output_dir or tempfile.mkdtemp(prefix="webbot_")
        self.selenium_bot = WebBot(headless=headless)
        self.ocr_processor = None
        self.playwright_integration = None
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize OCR if available
        if OCRProcessor.is_ocr_available():
            try:
                self.ocr_processor = OCRProcessor()
            except Exception as e:
                print(f"OCR initialization failed: {e}")
        
        # Initialize Playwright if available
        if PlaywrightUtilities.is_playwright_available():
            try:
                self.playwright_integration = PlaywrightIntegration(headless=headless)
            except Exception as e:
                print(f"Playwright initialization failed: {e}")

    def analyze_website(self, url: str) -> Dict:
        """
        Perform comprehensive analysis of a website.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary containing all analysis results
        """
        results = {
            "url": url,
            "timestamp": None,
            "robots_txt_check": None,
            "page_loaded": False,
            "screenshot_path": None,
            "text_content": None,
            "ocr_text": None,
            "depth_analysis": None,
            "performance_metrics": None,
            "playwright_results": None,
            "errors": []
        }
        
        try:
            # 1. Check robots.txt
            print(f"Checking robots.txt for {url}...")
            results["robots_txt_check"] = self.selenium_bot.check_robots_txt(url)
            
            if not results["robots_txt_check"]:
                print("robots.txt disallows access, proceeding anyway for demonstration...")
            
            # 2. Start selenium driver and navigate
            print("Starting Selenium WebDriver...")
            with self.selenium_bot as bot:
                print(f"Navigating to {url}...")
                results["page_loaded"] = bot.navigate_to(url, check_robots=False)
                
                if results["page_loaded"]:
                    import time
                    results["timestamp"] = time.time()
                    
                    # 3. Take full-screen screenshot
                    print("Taking full-screen screenshot...")
                    screenshot_filename = os.path.join(self.output_dir, "selenium_screenshot.png")
                    results["screenshot_path"] = bot.take_screenshot(screenshot_filename, full_page=True)
                    
                    # 4. Extract text content
                    print("Extracting text content...")
                    results["text_content"] = bot.extract_text_content()
                    
                    # 5. Perform OCR on screenshot
                    if self.ocr_processor and results["screenshot_path"]:
                        print("Performing OCR on screenshot...")
                        try:
                            results["ocr_text"] = self.ocr_processor.extract_text_from_image(
                                results["screenshot_path"]
                            )
                        except Exception as e:
                            results["errors"].append(f"OCR failed: {e}")
                    
                    # 6. Analyze page depth
                    print("Analyzing page depth and structure...")
                    results["depth_analysis"] = bot.get_page_depth_info()
                    
                    # 7. Get performance metrics
                    print("Collecting performance metrics...")
                    results["performance_metrics"] = bot.get_page_performance_metrics()
                    
                    # 8. Simulate human behavior
                    print("Simulating human behavior...")
                    bot.simulate_human_behavior()
                    
        except Exception as e:
            results["errors"].append(f"Selenium analysis failed: {e}")
        
        # 9. Playwright analysis (if available)
        if self.playwright_integration:
            print("Running Playwright analysis...")
            try:
                playwright_results = asyncio.run(self._run_playwright_analysis(url))
                results["playwright_results"] = playwright_results
            except Exception as e:
                results["errors"].append(f"Playwright analysis failed: {e}")
        
        return results

    async def _run_playwright_analysis(self, url: str) -> Dict:
        """
        Run Playwright analysis asynchronously.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary containing Playwright analysis results
        """
        playwright_results = {
            "page_content": None,
            "accessibility_tree": None,
            "network_requests": [],
            "responses": [],
            "screenshot_path": None
        }
        
        async with self.playwright_integration as pw:
            await pw.navigate_to(url)
            
            # Get page content
            playwright_results["page_content"] = await pw.get_page_content()
            
            # Get accessibility tree
            playwright_results["accessibility_tree"] = await pw.get_accessibility_tree()
            
            # Setup network monitoring
            requests = await pw.get_network_requests()
            responses = await pw.intercept_responses()
            
            # Take Playwright screenshot
            pw_screenshot_path = os.path.join(self.output_dir, "playwright_screenshot.png")
            await pw.take_screenshot(pw_screenshot_path, full_page=True)
            playwright_results["screenshot_path"] = pw_screenshot_path
            
            # Wait a bit to capture network activity
            await asyncio.sleep(2)
            
            playwright_results["network_requests"] = requests
            playwright_results["responses"] = responses
        
        return playwright_results

    def generate_report(self, analysis_results: Dict) -> str:
        """
        Generate a comprehensive analysis report.
        
        Args:
            analysis_results: Results from analyze_website()
            
        Returns:
            Path to the generated report file
        """
        report_path = os.path.join(self.output_dir, "analysis_report.json")
        
        # Create a clean version for JSON serialization
        clean_results = {}
        for key, value in analysis_results.items():
            if key == "accessibility_tree" and value:
                # Accessibility tree can be very large, summarize it
                clean_results[key] = {"node_count": self._count_accessibility_nodes(value)}
            else:
                clean_results[key] = value
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
        
        # Also create a human-readable summary
        summary_path = os.path.join(self.output_dir, "analysis_summary.txt")
        self._create_summary_report(clean_results, summary_path)
        
        print(f"Analysis report saved to: {report_path}")
        print(f"Summary report saved to: {summary_path}")
        
        return report_path

    def _count_accessibility_nodes(self, tree: Dict) -> int:
        """Count nodes in accessibility tree."""
        count = 1  # Current node
        if 'children' in tree:
            for child in tree['children']:
                count += self._count_accessibility_nodes(child)
        return count

    def _create_summary_report(self, results: Dict, summary_path: str) -> None:
        """Create a human-readable summary report."""
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=== WEB BOT ANALYSIS SUMMARY ===\n\n")
            f.write(f"URL: {results.get('url', 'N/A')}\n")
            f.write(f"Timestamp: {results.get('timestamp', 'N/A')}\n")
            f.write(f"Page Loaded: {results.get('page_loaded', False)}\n")
            f.write(f"Robots.txt Allows: {results.get('robots_txt_check', 'N/A')}\n\n")
            
            # Screenshots
            f.write("=== SCREENSHOTS ===\n")
            if results.get('screenshot_path'):
                f.write(f"Selenium Screenshot: {results['screenshot_path']}\n")
            if results.get('playwright_results', {}).get('screenshot_path'):
                f.write(f"Playwright Screenshot: {results['playwright_results']['screenshot_path']}\n")
            f.write("\n")
            
            # Text Analysis
            f.write("=== TEXT ANALYSIS ===\n")
            text_content = results.get('text_content', '')
            if text_content:
                f.write(f"Text Content Length: {len(text_content)} characters\n")
                f.write(f"Text Preview: {text_content[:200]}...\n")
            
            ocr_text = results.get('ocr_text', '')
            if ocr_text:
                f.write(f"OCR Text Length: {len(ocr_text)} characters\n")
                f.write(f"OCR Preview: {ocr_text[:200]}...\n")
            f.write("\n")
            
            # Page Structure
            f.write("=== PAGE STRUCTURE ===\n")
            depth_analysis = results.get('depth_analysis', {})
            if depth_analysis:
                f.write(f"DOM Depth: {depth_analysis.get('dom_depth', 'N/A')}\n")
                f.write(f"Page Height: {depth_analysis.get('page_height', 'N/A')}px\n")
                f.write(f"Total Links: {depth_analysis.get('total_links', 'N/A')}\n")
                f.write(f"Internal Links: {depth_analysis.get('internal_links', 'N/A')}\n")
                f.write(f"External Links: {depth_analysis.get('external_links', 'N/A')}\n")
                f.write(f"Images: {depth_analysis.get('images_count', 'N/A')}\n")
                f.write(f"Forms: {depth_analysis.get('forms_count', 'N/A')}\n")
                f.write(f"Headings: {depth_analysis.get('headings_count', 'N/A')}\n")
            f.write("\n")
            
            # Performance
            f.write("=== PERFORMANCE METRICS ===\n")
            performance = results.get('performance_metrics', {})
            if performance:
                for metric, value in performance.items():
                    f.write(f"{metric}: {value}ms\n")
            f.write("\n")
            
            # Playwright Results
            f.write("=== PLAYWRIGHT ANALYSIS ===\n")
            pw_results = results.get('playwright_results', {})
            if pw_results:
                f.write(f"Page Content Length: {len(pw_results.get('page_content', ''))} characters\n")
                f.write(f"Network Requests: {len(pw_results.get('network_requests', []))}\n")
                f.write(f"Responses: {len(pw_results.get('responses', []))}\n")
                accessibility = pw_results.get('accessibility_tree', {})
                if accessibility:
                    f.write(f"Accessibility Nodes: {accessibility.get('node_count', 'N/A')}\n")
            f.write("\n")
            
            # Errors
            errors = results.get('errors', [])
            if errors:
                f.write("=== ERRORS ===\n")
                for error in errors:
                    f.write(f"- {error}\n")


def main():
    """
    Main function to demonstrate the comprehensive web bot.
    """
    # Example URLs to test
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://quotes.toscrape.com/"
    ]
    
    print("=== COMPREHENSIVE WEB BOT DEMONSTRATION ===\n")
    
    # Create bot instance
    bot = ComprehensiveWebBot(headless=True)
    print(f"Output directory: {bot.output_dir}\n")
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"ANALYZING: {url}")
        print(f"{'='*60}")
        
        try:
            # Analyze the website
            results = bot.analyze_website(url)
            
            # Generate report
            report_path = bot.generate_report(results)
            
            print(f"\nAnalysis completed for {url}")
            print(f"Check {bot.output_dir} for outputs")
            
        except Exception as e:
            print(f"Error analyzing {url}: {e}")
        
        print("\n" + "-" * 60)
    
    print(f"\nAll analyses completed. Check {bot.output_dir} for all outputs.")


if __name__ == "__main__":
    main()