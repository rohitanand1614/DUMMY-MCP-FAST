from pydantic import BaseModel, Field
from fastmcp import FastMCP
from mcp_selenium.browser_manager import BrowserManager
from mcp_selenium.element_actions import ElementActions
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
app = FastMCP()
browser_manager = BrowserManager()

# ✅ Define a schema for structured input
class StartBrowserInput(BaseModel):
    browser: str = Field(default="chrome", description="Browser name (e.g. 'chrome')")
    headless: bool = Field(default=False, description="Launch browser in headless mode")
    args: list[str] | None = Field(default_factory=list, description="Extra command-line args")

@app.tool("start_browser")
def start_browser(input: StartBrowserInput):
    """Launch a Chrome browser session."""
    try:
        data = input.model_dump()  # Changed from dict() to model_dump()
        session_id = browser_manager.start_browser(
            browser=data["browser"],
            headless=data["headless"],
            args=data.get("args") or []
        )
        return {"session_id": session_id}
    except Exception as e:
        return {"error": str(e)}


@app.tool("navigate")
def navigate(url: str):
    """Navigate to a URL"""
    driver = browser_manager.get_active_driver()
    driver.get(url)
    return {"message": f"Navigated to {url}"}


@app.tool("click_element")
def click_element(by: str, value: str):
    """Click an element by selector"""
    driver = browser_manager.get_active_driver()
    ElementActions(driver).click(by, value)
    return {"message": f"Clicked element '{value}'"}


@app.tool("send_keys")
def send_keys(by: str, value: str, text: str):
    """Type text into an element"""
    driver = browser_manager.get_active_driver()
    ElementActions(driver).send_keys(by, value, text)
    return {"message": f"Sent keys '{text}'"}

# ✅ New input schema for HTML capture
class CaptureHTMLInput(BaseModel):
    by: str = Field(..., description="Locator strategy (e.g., 'id', 'xpath', 'css selector')")
    value: str = Field(..., description="Locator value for the element")



@app.tool("capture_html")
def capture_html(input: CaptureHTMLInput):
    """
    Capture and return the outer HTML, tag name, and attributes
    of an element located by the given selector.
    Useful for generating automation scripts based on actual page structure.
    """
    try:
        data = input.model_dump()
        driver = browser_manager.get_active_driver()
        element = ElementActions(driver).find_element(data["by"], data["value"])
        html_content = element.get_attribute("outerHTML")

        # Extract element attributes using JS
        attributes = driver.execute_script(
            """
            var items = {};
            for (var i = 0; i < arguments[0].attributes.length; ++i) {
                items[arguments[0].attributes[i].name] = arguments[0].attributes[i].value;
            }
            return items;
            """,
            element
        )

        return {
            "locator": data,
            "tag": element.tag_name,
            "attributes": attributes,
            "html": html_content.strip() if html_content else "",
            "message": "Captured HTML and attributes successfully"
        }

    except Exception as e:
        logger.error(f"Failed to capture HTML: {e}")
        return {"error": str(e)}

@app.tool("close_session")
def close_session():
    """Close the active browser"""
    browser_manager.close_active_session()
    return {"message": "Session closed"}


if __name__ == "__main__":
    app.run()

