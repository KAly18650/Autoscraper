# AutoScraper: AI-Powered Multi-Agent Web Scraping Pipeline

**Competition Submission - Enterprise Agents Track**

---

## Problem Statement

### The Challenge

Web scraping is essential for modern businesses—market research, competitive intelligence, content aggregation, and data analytics all depend on it. However, creating web scrapers is a **manual, time-intensive process**:

1. **HTML Analysis** (30-60 min): Inspecting page structure to identify CSS selectors
2. **Code Development** (1-2 hours): Writing Python code with error handling and parsing logic
3. **Testing & Debugging** (30-60 min): Validating selectors and handling edge cases
4. **Maintenance** (ongoing): Updating scrapers when websites change

**Total time per scraper: 3-4 hours** for an experienced developer.

### Why This Matters

In today's data-driven economy, businesses need to extract structured data from websites **quickly and reliably**. Current barriers:

- ❌ **Too slow**: Manual development takes hours per website
- ❌ **Too expensive**: Requires senior developer expertise
- ❌ **Too brittle**: Scrapers break when websites change
- ❌ **Not scalable**: Each new website requires starting from scratch

**Business Impact**: Companies lose competitive advantages because they can't access web data fast enough. Market opportunities pass while waiting for scrapers to be built.

---

## Why Agents?

Agents are the **ideal solution** because web scraper creation is inherently a **multi-step workflow requiring specialized expertise**—exactly what multi-agent systems excel at.

### 1. Specialized Expertise

Just as a real development team has different roles, scraper creation needs:

| Traditional Team | AutoScraper Agent | Expertise |
|-----------------|-------------------|-----------|
| Business Analyst | **Analyst Agent** | HTML structure analysis, CSS selector identification |
| Software Developer | **Coder Agent** | Python code generation, error handling, best practices |
| QA Engineer | **Validator Agent** | Testing, validation, error classification |
| Project Manager | **Orchestrator Agent** | Workflow coordination, decision-making, error routing |

### 2. Iterative Refinement

Scraper creation isn't linear—it requires **feedback loops**:

```
User Request → Analyst → Coder → Validator
                  ↑                    ↓
                  └──── Error? ────────┘
                  (Route to correct agent)
```

**Dynamic Error Routing:**
- Selector errors (data not found) → Route back to **Analyst**
- Coding errors (null pointer, type errors) → Route back to **Coder**
- Validation passes → **Save to repository**

This adaptive workflow is **exactly what agents excel at**—making intelligent decisions based on context and results.

### 3. Autonomous Problem-Solving

Agents can:
- ✅ **Use tools independently** (fetch HTML, test selectors, execute code)
- ✅ **Reason about results** (is this selector working? is this error a coding issue?)
- ✅ **Adapt their approach** (try alternative selectors, fix null checks)
- ✅ **Learn from failures** (iterate up to 5 times with improvements)

A traditional script would require **hardcoded decision trees** and couldn't adapt to different website structures. Agents can **reason, adapt, and learn**.

---

## What I Created

### System Architecture

AutoScraper implements a **hierarchical multi-agent system** with clear separation of concerns:

#### **Orchestrator Agent** (Project Manager)
- Coordinates entire workflow from user request to saved scraper
- Routes tasks to appropriate specialist agents
- Classifies errors (CODING_ERROR vs SELECTOR_ERROR)
- Manages iterative refinement (max 5 iterations)
- Saves validated scrapers to repository

#### **Analyst Agent** (HTML Expert)
**Tools:** `analyze_html_structure()`, `test_selector()`

- Fetches webpages using Playwright (handles JavaScript)
- Analyzes HTML structure to identify optimal selectors
- Tests selectors before finalizing
- Returns validated "Selector Map" (JSON)
- Handles both content scrapers and list scrapers

#### **Coder Agent** (Python Developer)
**Tools:** None (pure code generation)

- Generates production-ready Python scraper code
- Implements proper error handling and null checks
- Uses Playwright + BeautifulSoup for robust scraping
- Returns structured JSON data
- Follows Python best practices

#### **Validator Agent** (QA Engineer)
**Tools:** `execute_code()`, `test_selector()`

- Executes generated code in sandboxed environment
- Validates output against requirements
- Classifies errors for proper routing
- Provides detailed debug information
- Ensures scrapers work before deployment

### Key Innovations

#### 1. **Two Scraper Types**
- **Content Scrapers**: Extract data from individual pages
- **List Scrapers**: Extract URLs from listing pages
- **Pipelines**: Combine both for complete workflows (list → content)

#### 2. **Reusable Repository**
Generated scrapers are saved with metadata:
- Domain-based organization
- Automatic URL detection
- Versioning and timestamps
- Pipeline linking (list + content scrapers)

#### 3. **Intelligent Error Classification**
```python
if "TypeError" or "AttributeError":
    error_type = "CODING_ERROR"  # Route to Coder
elif field_is_None or empty_data:
    error_type = "SELECTOR_ERROR"  # Route to Analyst
```

#### 4. **Production-Ready**
- Docker containerization
- Google Cloud Storage integration
- Cloud Run deployment
- Comprehensive logging
- Security best practices (secrets in .env)

---

## Demo

### Command Line Usage

```bash
python main.py --url "https://hms.harvard.edu/news/article" \
               --prompt "Extract title, author, date, and content"
```

**Workflow:**

1. **Orchestrator** receives request → calls **Analyst**
2. **Analyst** analyzes HTML → returns Selector Map:
   ```json
   {
     "selectors": {
       "title": {"selector": "h1.field__item", "type": "text"},
       "author": {"selector": ".author-name", "type": "text"},
       "publish_date": {"selector": "time[datetime]", "attribute": "datetime"},
       "content": {"selector": "div.field-body", "type": "text"}
     }
   }
   ```

3. **Coder** generates Python code with error handling
4. **Validator** executes and validates:
   - ✓ All fields present
   - ✓ Data is meaningful
   - ✓ No errors

5. **Orchestrator** saves to `scraper_repository/scrapers/hms_harvard_edu.py`

### Reusing Scrapers

```python
from scraper_repository import get_scraper

scraper = get_scraper("hms.harvard.edu")
data = scraper.scrape("https://hms.harvard.edu/news/any-article")
# {'title': '...', 'author': '...', 'content': '...'}
```

### Two-Step Pipeline

```python
from scraper_repository import get_scraper_pipeline

list_scraper, content_scraper = get_scraper_pipeline("hms.harvard.edu")

# Step 1: Get URLs
urls = list_scraper.scrape("https://hms.harvard.edu/news")["urls"]

# Step 2: Scrape articles
articles = [content_scraper.scrape(url) for url in urls]
```

**Time Savings:** 3-4 hours → **5 minutes**

---

## The Build

### Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI** | Google ADK | Agent framework and orchestration |
| | Gemini 2.5 Flash | Analyst & Validator reasoning |
| | Gemini 2.0 Flash | Coder code generation |
| **Scraping** | Playwright | JavaScript-rendered content |
| | BeautifulSoup4 | HTML parsing |
| **Cloud** | Google Cloud Storage | Centralized scraper repository |
| | Cloud Run | Serverless deployment |
| | Secret Manager | Secure credential storage |
| **Dev** | Python 3.12 | Core language |
| | Docker | Containerization |

### Development Timeline

**Day 1-2: Agent Design**
- Designed four-agent architecture
- Created detailed instruction prompts
- Defined tool interfaces

**Day 2-3: Core Tools**
- Implemented Playwright-based HTML fetching
- Built selector testing tool
- Created code execution sandbox
- Developed storage abstraction

**Day 3-4: Repository System**
- Built scraper save/load functionality
- Implemented metadata tracking
- Created pipeline support
- Added auto-detection

**Day 4-5: Error Handling**
- Implemented error classification
- Added iterative refinement loops
- Built comprehensive validation
- Added debug output

**Day 5: Deployment**
- Dockerized application
- Integrated with GCS
- Deployed to Cloud Run
- Created examples and tests

---

## Business Value

### ROI Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Time per scraper** | 3-4 hours | 5 minutes | **36-48x faster** |
| **Developer skill required** | Senior | None (AI-driven) | **Democratized** |
| **Maintenance** | Manual updates | Regenerate in 5 min | **Automated** |
| **Scalability** | Linear (1 dev = 1 scraper) | Parallel (unlimited) | **Infinite** |

### Enterprise Applications

1. **Competitive Intelligence**: Monitor competitor pricing, products, content
2. **Market Research**: Aggregate industry news, trends, sentiment
3. **Lead Generation**: Extract contact information, company data
4. **Content Aggregation**: Curate news, blogs, research papers
5. **Compliance Monitoring**: Track regulatory changes, legal updates

---

## If I Had More Time

### Advanced Features
- **Self-Healing Scrapers**: Auto-detect website changes and regenerate
- **Pagination Support**: Handle "next page" buttons automatically
- **Authentication**: Support login-required pages
- **Rate Limiting**: Respect website policies

### Enhanced Intelligence
- **Pattern Recognition**: Learn from existing scrapers
- **Confidence Scoring**: Rate scraper reliability
- **A/B Testing**: Generate multiple variants, choose best

### Enterprise Features
- **Multi-tenancy**: Separate repositories per organization
- **Access Control**: Role-based permissions
- **Audit Logs**: Track scraper creation/modification
- **SLA Monitoring**: Uptime guarantees and failover

### User Experience
- **Visual Selector Builder**: Point-and-click interface
- **Scraper Marketplace**: Share community-built scrapers
- **Batch Operations**: Queue multiple requests
- **Export Options**: CSV, JSON, database integration

---

## Conclusion

AutoScraper demonstrates that **agents aren't just for chatbots**—they're powerful tools for automating complex, multi-step technical workflows that traditionally required human expertise.

By coordinating specialized AI agents, AutoScraper transforms a **3-4 hour manual process** into a **5-minute autonomous workflow**, making web scraping accessible to everyone while maintaining production-quality output.

This is the future of enterprise automation: **intelligent agents working together to solve real business problems**.

---

**Project Repository:** [GitHub Link]  
**Live Demo:** [Cloud Run URL]  
**Documentation:** See README.md and DEPLOYMENT.md
