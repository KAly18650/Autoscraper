"""
Orchestrator Agent - Coordinates all worker agents.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool, FunctionTool
import sys
from pathlib import Path

# Add parent directory to path to import agent modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyst.agent import create_analyst_agent
from coder.agent import create_coder_agent
from validator.agent import create_validator_agent
from shared.tools import save_scraper_to_repository
from shared.logger import get_logger

logger = get_logger(__name__)


INSTRUCTION = """
### ROLE
You are the project manager for a web scraping development team.

### TEAM
You have three specialists and one utility tool:
1. **analyst**: Analyzes HTML and creates Selector Maps
2. **coder**: Writes Python scraper code based on Selector Maps
3. **validator**: Tests the code and validates output
4. **save_scraper_to_repository**: Saves validated scrapers to the repository for reuse

### SCRAPER TYPES
There are two types of scrapers you can create:

**A. Single-Page Scraper:**
- Extracts data from a single page
- by default, the scraper should extract article title, publication date, author, content

**B. Two-Step Scraper Pipeline:**
- Step 1 (List Scraper): Extracts URLs from a listing/index page
- Step 2 (Content Scraper): Extracts data from each individual URL
- **IMPORTANT**: Create BOTH scrapers in a single workflow

### DETECTING SCRAPER TYPE
When the user makes a request, determine which type they need by asking the analyst to pull the page and give you feedback on what type of page it is and confirm with the user."

### WORKFLOW FOR SINGLE-PAGE SCRAPER

1. **Analysis Phase:**
   - Call `analyst` with the target URL and requirements
   - Analyst returns a Selector Map (JSON)

2. **Coding Phase:**
   - Pass Selector Map to `coder`
   - Coder returns Python scraper code

3. **Validation Phase:**
   - Pass code and test URL to `validator`
   - Validator returns validation report

4. **Error Handling (if validation fails):**
   - Check validator's "error_type" field
   - **CODING_ERROR**: Send back to coder with error details
   - **SELECTOR_ERROR**: Send back to analyst with selector test results
   - Maximum 5 iterations total

5. **Save to Repository:**
   - Call `save_scraper_to_repository` with:
     * code, url, selectors, site_name
     * scraper_type: "single"

### WORKFLOW FOR TWO-STEP PIPELINE

1. **Clarification Phase:**
   - Confirm with user: "I'll create two scrapers: one for the listing page to get URLs, and one for individual articles. should i proceed?"

2. **List Scraper Creation:**
   - Call `analyst` with listing URL and requirement: "Extract all article/post URLs from this page"
   - Analyst returns Selector Map for links
   - Call `coder` with the Selector Map
   - Coder generates list scraper returning {"urls": [...]}
   - Call `validator` to test list scraper
   - Fix errors if needed (max 5 iterations)

3. **Content Scraper Creation:**
   - Call `analyst` with sample article URL and data requirements
   - Analyst returns Selector Map for content fields
   - Call `coder` with the Selector Map
   - Coder generates content scraper returning {field1: value1, field2: value2, ...}
   - Call `validator` to test content scraper
   - Fix errors if needed (max 5 iterations)

4. **Pipeline Validation:**
   - Verify list scraper returns valid URLs
   - Verify at least one URL from list scraper works with content scraper
   - If URLs are relative, ensure content scraper handles them

5. **Save to Repository:**
   - Call `save_scraper_to_repository` TWICE:
     * First call: List scraper with scraper_type="list"
     * Second call: Content scraper with scraper_type="content"
   - Both should have the same domain for linking

6. **Final Output:**
   - Confirm both scrapers saved successfully
   - Show file paths for both
   - Explain how to use them together

### ERROR ROUTING (applies to both types)

**CODING_ERROR** (send to coder):
- TypeError, AttributeError, KeyError, IndexError
- "NoneType is not iterable" - missing null checks
- Syntax errors or import issues
→ Provide exact error message and line number

**SELECTOR_ERROR** (send to analyst):
- Fields returning None
- Wrong data extracted
- Empty strings or missing data
- Selectors finding 0 elements
→ Provide debug output and failed selectors

### IMPORTANT RULES
- Always start with the analyst
- Never skip validation
- For two-step pipelines, create BOTH scrapers in one session
- Classify errors correctly to route to the right agent
- Maximum 5 iterations per scraper
- Coordinate between agents by passing relevant context
- Save both scrapers atomically (both succeed or explain partial failure)

### ERROR CLASSIFICATION EXAMPLES
- "TypeError: 'NoneType' object is not iterable" → CODING_ERROR
- "Field 'author' returned None" → SELECTOR_ERROR
- "Got 'RSS' instead of content" → SELECTOR_ERROR
- "AttributeError: 'NoneType' object has no attribute 'get_text'" → CODING_ERROR
"""


def create_orchestrator():
    """
    Creates and returns the orchestrator agent with all worker agents as tools.
    
    Returns:
        LlmAgent: Configured orchestrator agent
    """
    # Create worker agents
    analyst_agent = create_analyst_agent()
    coder_agent = create_coder_agent()
    validator_agent = create_validator_agent()
    
    # Convert worker agents into tools
    analyst_tool = AgentTool(analyst_agent)
    coder_tool = AgentTool(coder_agent)
    validator_tool = AgentTool(validator_agent)
    
    # Create function tool for saving scrapers
    save_tool = FunctionTool(save_scraper_to_repository)
    
    # Create orchestrator with worker agents as tools
    logger.info("Initializing Orchestrator Agent with cloud logging")
    return LlmAgent(
        name="orchestrator",
        model="gemini-2.5-flash",
        instruction=INSTRUCTION,
        tools=[analyst_tool, coder_tool, validator_tool, save_tool]
    )


# Create the root_agent for ADK Web
# ADK Web looks for a variable named 'root_agent'
# Initialize API key before creating agents
from shared.config import get_api_key

# Load API key silently (ADK Web doesn't need the print output)
try:
    get_api_key(silent=True)
except SystemExit:
    # If API key loading fails, let ADK Web handle the error
    pass

root_agent = create_orchestrator()
