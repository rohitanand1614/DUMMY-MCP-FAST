# 🚀 MCP Selenium Server — FastMCP Integration

## 📘 Overview
This repository implements a **Model Context Protocol (MCP) server** that integrates **Selenium WebDriver** with **FastMCP**, enabling automated browser interactions through a structured, tool-based API.  
It allows you to **launch browsers**, **navigate**, **interact with elements**, and **close sessions** — all accessible via the **MCP Inspector**.

---

## 🧩 Repository Structure

```
DUMMY-MCP-FAST/
├── run_mcp_selenium.py            # Entry point to start MCP Selenium server
├── manifest.json                  # Defines environment paths and entry script
├── requirements.txt               # Required dependencies
├── browsers/                      # Browser binaries (e.g., chrome.exe)
├── drivers/                       # WebDriver executables (e.g., chromedriver.exe)
└── mcp_selenium/                  # Main MCP Selenium package
    ├── __init__.py                # Initializes logging and package metadata
    ├── browser_manager.py         # Manages Selenium sessions (start/stop)
    ├── element_actions.py         # Encapsulates element-level actions (click, send_keys, etc.)
    ├── schemas.py                 # Pydantic schemas for structured tool inputs/outputs
    ├── server.py                  # FastMCP app defining available tools and handlers
    ├── utils.py                   # Helper functions (timestamp, screenshots, encoding)
```

---

## ⚙️ Installation & Setup

### 1️⃣ Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Mac/Linux
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Verify Chrome & WebDriver Paths
Ensure paths in `manifest.json` are correct:
```json
{
  "SELENIUM_DRIVER_PATH": "./drivers/chromedriver.exe",
  "SELENIUM_BINARY_PATH": "./browsers/chrome.exe"
}
```

---

## 🧠 Understanding Each File

### 🔹 `run_mcp_selenium.py`
Main script that **starts the FastMCP server** by importing `app` from `server.py` and running it.

### 🔹 `manifest.json`
Defines **metadata and environment variables** for MCP setup:
- `entry`: Script to start (`run_mcp_selenium.py`)
- `SELENIUM_DRIVER_PATH`: Path to Chrome WebDriver
- `SELENIUM_BINARY_PATH`: Chrome binary path

### 🔹 `requirements.txt`
Specifies core dependencies:
- `selenium` → for browser automation  
- `fastmcp` → for MCP server interface  
- `pydantic` → for structured data models  

### 🔹 `mcp_selenium/__init__.py`
Initializes the MCP Selenium package with logging and metadata.  
Logs “✅ MCP Selenium package initialized” at startup.

### 🔹 `mcp_selenium/browser_manager.py`
Handles:
- Starting and managing browser sessions  
- Tracking session IDs  
- Closing active sessions  
- Switching between session contexts  

### 🔹 `mcp_selenium/element_actions.py`
Provides all **UI interactions** like:
- `click(by, value)` → clicks on element  
- `send_keys(by, value, text)` → types input  
- `find_element(by, value)` → waits for presence of element  

### 🔹 `mcp_selenium/schemas.py`
Defines **Pydantic models** for tool input/output, ensuring validation and descriptive fields for commands like navigation.

### 🔹 `mcp_selenium/server.py`
Core MCP logic — defines all **tools available to the MCP inspector**, such as:
- `start_browser` → Launch Chrome in headless or UI mode  
- `navigate` → Open URL  
- `click_element` → Click an element by selector  
- `send_keys` → Type text into a field  
- `close_session` → Close browser  

This is the **main logic layer** of the system.

### 🔹 `mcp_selenium/utils.py`
Provides **support utilities** for screenshots and encoding:
- `save_screenshot()` → captures and stores browser images  
- `encode_image()` → returns base64-encoded screenshot  

---

## 🧭 Workflow & Lifecycle

1️⃣ **Initialization**
   - When `run_mcp_selenium.py` runs, FastMCP starts and registers all tools from `server.py`.

2️⃣ **Browser Launch**
   - MCP Inspector or client calls `start_browser` → BrowserManager opens Chrome.

3️⃣ **Navigation & Actions**
   - `navigate`, `click_element`, and `send_keys` interact with live browser session.

4️⃣ **Session Close**
   - `close_session` terminates WebDriver and clears memory.

5️⃣ **Logging & Debugging**
   - Logs appear in terminal to trace tool calls and session flow.

---

## 🔍 MCP Inspector — Interactive Testing

Use the MCP Inspector to explore, invoke, and debug all MCP tools:

```bash
npx @modelcontextprotocol/inspector python run_mcp_selenium.py
```

### ✅ Expected Behavior
- Inspector UI lists tools: `start_browser`, `navigate`, `click_element`, etc.
- You can call them interactively and see real-time results.
- Browser sessions launch in real Chrome instances via `chromedriver.exe`.

---

## 💡 Example Commands

### Start the server:
```bash
python run_mcp_selenium.py
```

### Start MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python run_mcp_selenium.py
```

### Example Workflow:
1. In Inspector, run:
   ```json
   {
     "tool": "start_browser",
     "input": { "browser": "chrome", "headless": false }
   }
   ```
2. Then:
   ```json
   { "tool": "navigate", "input": "https://example.com" }
   ```
3. Interact with elements:
   ```json
   { "tool": "click_element", "input": { "by": "css", "value": "#submit" } }
   ```
4. Close session:
   ```json
   { "tool": "close_session" }
   ```

---

## 🧾 Logging Example
When you start the app, you’ll see logs like:
```
INFO: ✅ MCP Selenium package initialized.
DEBUG: Starting FastMCP server on port 8000
```

---

## 🧩 Credits
**Author:** Rohit Anand  
**Version:** 1.0.0  
**License:** MIT (optional)

---

## 🧰 Future Enhancements
- Add multi-browser support (Firefox, Edge)  
- Capture screenshots on tool errors  
- Integrate AI-driven test case generation via LLM
