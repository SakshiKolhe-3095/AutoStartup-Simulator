"""
Landing page screenshot tool — renders HTML via headless Chromium, saves PNG.
Owner: Sakshi
"""
import os
from playwright.sync_api import sync_playwright
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def screenshot_landing_page(html_path: str, output_path: str = "landing_page_screenshot.png") -> str | None:
    """
    Renders a landing page HTML file and saves a screenshot.
    Returns the output path, or None if rendering fails.
    """
    if not html_path or not os.path.exists(html_path):
        logger.warning(f"screenshot_landing_page: HTML file not found: {html_path}")
        return None

    try:
        abs_path = os.path.abspath(html_path)
        file_url = f"file:///{abs_path.replace(os.sep, '/')}"

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(file_url, wait_until="networkidle", timeout=10000)
            page.screenshot(path=output_path)
            browser.close()

        return output_path
    except Exception as e:
        logger.warning(f"screenshot_landing_page: failed to render/screenshot: {e}")
        return None


if __name__ == "__main__":
    # quick manual test — write a sample HTML file and screenshot it
    test_html = "<html><body style='background:#4caf50;color:white;font-family:sans-serif;padding:50px'><h1>Test Landing Page</h1></body></html>"
    test_path = "test_landing.html"
    with open(test_path, "w") as f:
        f.write(test_html)
    result = screenshot_landing_page(test_path, "test_screenshot.png")
    print(f"Screenshot saved: {result}")