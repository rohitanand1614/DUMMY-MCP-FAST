from pydantic import BaseModel, Field
from fastmcp import FastMCP
from mcp_selenium.browser_manager import BrowserManager
from mcp_selenium.element_actions import ElementActions
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
app = FastMCP()
browser_manager = BrowserManager()
import traceback

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

class CaptureHTMLInput(BaseModel):
    by: str | None = Field(default=None, description="Locator strategy (id, css, xpath, etc.)")
    value: str | None = Field(default=None, description="Locator value (optional)")
    full_page: bool = Field(default=False, description="If True, capture full page HTML")

'''
@app.tool("capture_html")
async def capture_html(input: CaptureHTMLInput, ctx: Context):
    """Capture HTML for a given element or full page."""
    driver = browser_manager.get_active_driver()

    if input.full_page:
        html_content = driver.page_source
        await ctx.info("Captured full-page HTML")
    else:
        element = ElementActions(driver).find_element(input.by, input.value)
        html_content = element.get_attribute("outerHTML")

    return {
        "html": html_content,
        "url": driver.current_url
    }
'''

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

#script generation tool 
class TestGenerationInput(BaseModel):
    user_prompt: str = Field(..., description="User’s natural-language instruction")
    html_snapshot: str = Field(..., description="HTML content from capture_html")

@app.tool("generate_test_script")
async def generate_test_script(input: TestGenerationInput, ctx: Context):
    """
    Generate Selenium Python test case code based on user instruction and HTML.
    Uses the LLM through FastMCP's ctx.sample().
    """
    system_prompt = """
    You are an expert Selenium test engineer. 
    Given an HTML snapshot and user intent, write a runnable Python Selenium test.
    Use locators that match the HTML (ids, names, or CSS).
    Include setup, teardown, and meaningful assertions.
    """

    response = await ctx.sample(
        f"{system_prompt}\n\nUser Instruction:\n{input.user_prompt}\n\nHTML Snapshot:\n{input.html_snapshot[:2000]}"
    )

    script = response.text
    return {"generated_code": script}

#self healing tool 
class SelfHealInput(BaseModel):
    test_script: str = Field(..., description="Python Selenium test script as string")
    url: str = Field(..., description="Target URL for context")

@app.tool("self_heal_test")
async def self_heal_test(input: SelfHealInput, ctx: Context):
    """
    Runs a given Selenium test, detects failure points, compares DOM, and suggests fixes.
    """
    driver = browser_manager.get_active_driver()
    driver.get(input.url)
    result = {"status": "success", "suggestions": []}

    try:
        # Execute test in isolated namespace
        exec(input.test_script, {"driver": driver})
        await ctx.info("Test executed successfully.")
    except Exception as e:
        tb = traceback.format_exc()
        await ctx.error(f"Test failed: {str(e)}")
        result["status"] = "failed"
        result["error"] = str(e)
        result["traceback"] = tb

        # Capture new HTML snapshot
        new_html = driver.page_source
        # Ask LLM to heal the selector
        heal_prompt = f"""
        The following Selenium test failed:\n{input.test_script}
        Error:\n{str(e)}\n\n
        Current page HTML:\n{new_html[:2000]}
        Suggest updated locators or code fixes for self-healing.
        """
        heal_suggestion = await ctx.sample(heal_prompt)
        result["suggestions"].append(heal_suggestion.text)

    return result

@app.tool("close_session")
def close_session():
    """Close the active browser"""
    browser_manager.close_active_session()
    return {"message": "Session closed"}


if __name__ == "__main__":
    app.run()

