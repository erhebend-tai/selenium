# Selenium WebBot

A comprehensive web automation bot that integrates multiple tools for advanced web scraping and automation.

## Features

- **Selenium WebDriver Integration**: Full Chromium browser automation
- **Full-Screen Screenshots**: Capture entire web pages
- **OCR (Optical Character Recognition)**: Extract text from screenshots
- **Page Depth Analysis**: Analyze page structure and content depth
- **robots.txt Checking**: Respect website crawling policies
- **Playwright Integration**: Enhanced browser automation capabilities
- **Performance Monitoring**: Collect page load and performance metrics
- **Human-like Behavior**: Simulate realistic user interactions

## Installation

### Basic Installation
The webbot module is included with selenium but requires additional dependencies for full functionality:

```bash
pip install selenium
```

### Optional Dependencies

For full functionality, install the optional dependencies:

```bash
# For OCR capabilities
pip install pytesseract pillow
sudo apt-get install tesseract-ocr  # On Ubuntu/Debian

# For Playwright integration
pip install playwright
playwright install

# Or install all at once
pip install selenium[webbot]  # If webbot extras are configured
```

## Quick Start

### Basic Usage

```python
from selenium.webbot import WebBot

# Create and use the bot
with WebBot(headless=True) as bot:
    # Navigate to a website
    bot.navigate_to("https://example.com")
    
    # Take a full-screen screenshot
    screenshot_path = bot.take_screenshot("example.png", full_page=True)
    
    # Extract text content
    text = bot.extract_text_content()
    
    # Analyze page structure
    depth_info = bot.get_page_depth_info()
    print(f"Page has {depth_info['total_links']} links")
```

### Comprehensive Analysis

```python
from selenium.webbot.example import ComprehensiveWebBot

# Create comprehensive bot
bot = ComprehensiveWebBot(headless=True)

# Analyze a website
results = bot.analyze_website("https://example.com")

# Generate detailed report
report_path = bot.generate_report(results)
print(f"Report saved to: {report_path}")
```

### OCR Text Extraction

```python
from selenium.webbot.ocr import OCRProcessor

# Initialize OCR processor
ocr = OCRProcessor()

# Extract text from image
text = ocr.extract_text_from_image("screenshot.png")
print(f"Extracted text: {text}")

# Extract with confidence scores
results = ocr.extract_text_with_confidence("screenshot.png")
for result in results:
    print(f"Text: '{result['text']}' (confidence: {result['confidence']})")
```

### Playwright Integration

```python
import asyncio
from selenium.webbot.playwright_integration import PlaywrightIntegration

async def playwright_example():
    async with PlaywrightIntegration(headless=True) as pw:
        await pw.navigate_to("https://example.com")
        await pw.take_screenshot("playwright_screenshot.png", full_page=True)
        content = await pw.get_page_content()
        print(f"Page content length: {len(content)}")

# Run async function
asyncio.run(playwright_example())
```

## API Reference

### WebBot Class

#### Constructor
- `WebBot(headless=True, window_size=(1920, 1080))`

#### Methods
- `start_driver()`: Initialize Chrome WebDriver
- `quit_driver()`: Quit WebDriver and cleanup
- `check_robots_txt(url, user_agent="*")`: Check robots.txt permissions
- `navigate_to(url, check_robots=True)`: Navigate to URL
- `take_screenshot(filename=None, full_page=True)`: Capture screenshot
- `get_page_depth_info()`: Analyze page structure
- `extract_text_content()`: Get page text content
- `get_page_performance_metrics()`: Collect performance data
- `simulate_human_behavior(delay_range=(1, 3))`: Add realistic delays

### OCRProcessor Class

#### Constructor
- `OCRProcessor(tesseract_path=None)`

#### Methods
- `extract_text_from_image(image_path, language="eng")`: Extract text from image
- `extract_text_with_confidence(image_path, language="eng")`: Extract with confidence scores
- `detect_text_regions(image_path)`: Find text regions in image
- `validate_text_quality(text, min_confidence=50)`: Validate extracted text quality

### PlaywrightIntegration Class

#### Constructor
- `PlaywrightIntegration(headless=True)`

#### Methods
- `start_browser(browser_type="chromium")`: Start Playwright browser
- `close_browser()`: Close browser and cleanup
- `navigate_to(url)`: Navigate to URL
- `take_screenshot(path, full_page=True)`: Capture screenshot
- `get_page_content()`: Get HTML content
- `get_accessibility_tree()`: Get accessibility information

## Configuration

### Chrome Options
The WebBot automatically configures Chrome with optimal settings:
- Headless mode support
- Security and sandbox settings
- Window size configuration
- User agent spoofing
- Performance optimizations

### OCR Languages
OCR supports multiple languages. Get available languages:

```python
ocr = OCRProcessor()
languages = ocr.get_supported_languages()
print(f"Supported languages: {languages}")
```

### Playwright Browsers
Playwright supports multiple browser engines:
- Chromium (default)
- Firefox
- WebKit

```python
async with PlaywrightIntegration() as pw:
    await pw.start_browser("firefox")  # Use Firefox instead
```

## Error Handling

The webbot modules include comprehensive error handling and logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Use bot with error handling
try:
    with WebBot() as bot:
        success = bot.navigate_to("https://example.com")
        if not success:
            print("Navigation failed")
except Exception as e:
    print(f"Bot error: {e}")
```

## Examples

### Complete Website Analysis

See `selenium/webbot/example.py` for a comprehensive example that demonstrates:
- Multi-URL analysis
- Screenshot comparison (Selenium vs Playwright)
- OCR text extraction
- Performance monitoring
- Report generation

### Batch Processing

```python
urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
results = []

with WebBot() as bot:
    for url in urls:
        if bot.navigate_to(url):
            results.append({
                "url": url,
                "screenshot": bot.take_screenshot(f"{url.replace('/', '_')}.png"),
                "depth": bot.get_page_depth_info(),
                "text": bot.extract_text_content()
            })
```

## Troubleshooting

### Chrome WebDriver Issues
- Ensure Chrome/Chromium is installed
- Check that chromedriver is in PATH or install via selenium-manager
- Use `--no-sandbox` flag in containerized environments

### OCR Issues
- Install tesseract system package
- Verify tesseract path: `pytesseract.pytesseract.tesseract_cmd`
- Use image preprocessing for better accuracy

### Playwright Issues
- Run `playwright install` after pip install
- Ensure sufficient disk space for browser downloads
- Check permissions for browser installation

## Performance Tips

1. **Use headless mode** for better performance
2. **Disable images** in Chrome options for faster loading
3. **Batch operations** when analyzing multiple URLs
4. **Preprocess images** before OCR for better accuracy
5. **Monitor memory usage** for long-running operations

## Contributing

This module follows Selenium's contribution guidelines. See `CONTRIBUTING.md` for details.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` file for details.