# AutoScraper: AI-Powered Multi-Agent Web Scraping Pipeline

> **Automatically generate production-ready web scrapers using coordinated AI agents**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4.svg)](https://ai.google.dev/adk)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-8E75B2.svg)](https://ai.google.dev/)

AutoScraper transforms web scraping from a manual, time-consuming process into an autonomous, AI-driven workflow. Using a team of specialized agents, it analyzes websites, generates Python code, validates output, and saves reusable scrapers—all in minutes.

---

## 🎯 Problem & Solution

**The Problem:** Creating web scrapers traditionally requires:
- Hours of HTML inspection to find the right selectors
- Writing complex Python code with error handling
- Extensive testing and debugging
- Maintenance when websites change

**The Solution:** AutoScraper automates this entire workflow using coordinated AI agents that work like a real development team—analyst, coder, and QA engineer—orchestrated by an intelligent project manager.

---

## 🏗️ Architecture

AutoScraper uses a **hierarchical multi-agent system** with four specialized agents:

```
┌─────────────────────────────────────────────────┐
│           Orchestrator Agent                    │
│         (Project Manager)                       │
│  • Coordinates workflow                         │
│  • Routes tasks to specialists                  │
│  • Handles error classification                 │
│  • Manages iterative refinement                 │
└──────────┬──────────────┬──────────────┬────────┘
           │              │              │
    ┌──────▼─────┐ ┌─────▼──────┐ ┌────▼────────┐
    │  Analyst   │ │   Coder    │ │  Validator  │
    │  Agent     │ │   Agent    │ │   Agent     │
    ├────────────┤ ├────────────┤ ├─────────────┤
    │ • Analyzes │ │ • Generates│ │ • Executes  │
    │   HTML     │ │   Python   │ │   code      │
    │ • Tests    │ │   code     │ │ • Validates │
    │   selectors│ │ • Error    │ │   output    │
    │ • Returns  │ │   handling │ │ • Classifies│
    │   Selector │ │ • Best     │ │   errors    │
    │   Map      │ │   practices│ │             │
    └────────────┘ └────────────┘ └─────────────┘
           │              │              │
           └──────────────┴──────────────┘
                         │
                  ┌──────▼──────┐
                  │  Scraper    │
                  │  Repository │
                  └─────────────┘
```

### Key Features

✅ **Two Scraper Types**
- **Content Scrapers**: Extract data from individual pages (title, author, content, etc.)
- **List Scrapers**: Extract URLs from listing pages, then scrape each URL

✅ **Intelligent Error Routing**
- Coding errors → Route back to Coder Agent
- Selector errors → Route back to Analyst Agent
- Max 5 iterations with automatic refinement

✅ **Reusable Repository**
- Validated scrapers saved with metadata
- Auto-detection from URLs
- Pipeline support (list + content scrapers)

✅ **Production-Ready**
- Docker containerization
- Google Cloud Storage integration
- Cloud Run deployment
- Comprehensive error handling

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Google Gemini API key ([Get one here](https://ai.google.dev/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/autoscraper.git
   cd autoscraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

4. **Verify setup**
   ```bash
   python tests/test_env_integrations.py
   python tests/test_playwright.py
   ```

---

## 💻 Usage

### Command Line Interface

Create a scraper for any website:

```bash
python main.py --url "https://hms.harvard.edu/news/article" \
               --prompt "Extract title, author, date, and content"
```

**What happens:**
1. Orchestrator coordinates the workflow
2. Analyst analyzes HTML and identifies selectors
3. Coder generates Python scraper code
4. Validator tests and validates the scraper
5. Scraper saved to `scraper_repository/scrapers/`

### ADK Web Interface

For interactive scraper creation:

```bash
adk web
```

Then open http://localhost:8000 and chat with the orchestrator agent.

### Using Saved Scrapers

Once generated, scrapers are reusable:

```python
from scraper_repository import get_scraper

# Get scraper by domain
scraper = get_scraper("hms.harvard.edu")
data = scraper.scrape("https://hms.harvard.edu/news/any-article")

print(data)
# {'title': '...', 'author': '...', 'publish_date': '...', 'content': '...'}
```

### Two-Step Pipeline

For news sites and blogs:

```python
from scraper_repository import get_scraper_pipeline

# Get both list and content scrapers
list_scraper, content_scraper = get_scraper_pipeline("hms.harvard.edu")

# Step 1: Get all article URLs
urls = list_scraper.scrape("https://hms.harvard.edu/news")["urls"]

# Step 2: Scrape each article
articles = [content_scraper.scrape(url) for url in urls]
```

---

## 📁 Project Structure

```
autoscraper/
├── orchestrator/          # Orchestrator agent (coordinates workflow)
├── analyst/              # Analyst agent (HTML analysis)
├── coder/                # Coder agent (code generation)
├── validator/            # Validator agent (testing & validation)
├── shared/               # Shared tools and utilities
│   ├── tools.py         # Agent tools (analyze_html, test_selector, execute_code)
│   ├── storage.py       # GCS + local storage abstraction
│   ├── config.py        # Configuration management
│   └── logger.py        # Structured logging
├── scraper_repository/   # Generated scrapers
│   ├── scrapers/        # Python scraper modules
│   ├── metadata/        # Scraper metadata (JSON)
│   └── __init__.py      # Repository API
├── examples/             # Usage examples
├── tests/                # Diagnostic tests
├── main.py              # CLI entry point
├── Dockerfile           # Container definition
└── deploy_cloud_run.ps1 # Deployment script
```

---

## 🛠️ Technologies

| Category | Technologies |
|----------|-------------|
| **AI Framework** | Google ADK, Gemini 2.5 Flash, Gemini 2.0 Flash |
| **Web Scraping** | Playwright, BeautifulSoup4 |
| **Cloud** | Google Cloud Storage, Cloud Run, Secret Manager |
| **Development** | Python 3.12, Docker, PowerShell |

---

## 📚 Documentation

- **[PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md)** - Detailed competition submission (problem statement, architecture, demo)
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Cloud deployment guide (GCP setup, Cloud Run deployment)
- **[examples/README.md](examples/README.md)** - Usage examples and patterns
- **[tests/README.md](tests/README.md)** - Diagnostic tests and troubleshooting

---

## 🧪 Testing

Run diagnostic tests to verify your setup:

```bash
# Test environment configuration
python tests/test_env_integrations.py

# Test Playwright installation
python tests/test_playwright.py

# Test generated scrapers
python tests/test_scrapers.py

# Test agent tools
python tests/test_tools.py
```

---

## 🚢 Deployment

Deploy to Google Cloud Run:

1. **Configure `.env`** with your GCP project details
2. **Run deployment script:**
   ```powershell
   .\deploy_cloud_run.ps1
   ```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## 🎓 Examples

### Example 1: Single-Page Scraper
```bash
python main.py --url "https://example.com/article" \
               --prompt "Extract title and content"
```

### Example 2: List Scraper
```bash
python main.py --url "https://example.com/blog" \
               --prompt "Create a list scraper for blog post URLs"
```

### Example 3: Using Repository
```bash
python examples/example_use_repository.py
```

### Example 4: Pipeline Workflow
```bash
python examples/example_use_pipeline.py
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with [Google ADK](https://ai.google.dev/adk)
- Powered by [Gemini AI](https://ai.google.dev/)
- Created for the 5-Day AI Agents Intensive

---

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made with ❤️ using AI Agents**
