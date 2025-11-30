# AutoScraper Examples

This directory contains example scripts demonstrating how to use AutoScraper's scraper repository.

## Examples

### 1. `example_use_repository.py`
**Purpose:** Shows basic scraper repository usage

**What it demonstrates:**
- Getting a scraper by domain name
- Auto-detecting scraper from URL
- Listing all available scrapers
- Batch scraping multiple URLs

**Run it:**
```bash
python examples/example_use_repository.py
```

---

### 2. `example_use_pipeline.py`
**Purpose:** Shows two-step scraper pipeline usage

**What it demonstrates:**
- Using list scrapers to get article URLs
- Using content scrapers to extract article data
- Combining both for complete workflows
- Error handling in batch operations

**Run it:**
```bash
python examples/example_use_pipeline.py
```

---

## Prerequisites

Before running these examples:

1. **Generate scrapers first** using ADK Web or main.py:
   ```bash
   python main.py --url "https://hms.harvard.edu/news" --prompt "Create a list scraper"
   python main.py --url "https://hms.harvard.edu/news/article" --prompt "Extract article data"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

---

## Expected Output

### Repository Example
```
Found 3 scraper(s):

Domain: hms.harvard.edu
  Site: Harvard Medical School News
  Fields: title, author, publish_date, content
  Created: 2024-11-30T10:30:00
```

### Pipeline Example
```
Step 1: Getting URLs from listing page
Found 15 URLs

Step 2: Scraping first 3 articles...
  [1] Scraping: https://hms.harvard.edu/news/article-1
      Title: AI System with Detailed Diagnostic Reasoning...
✓ Successfully scraped 3 articles
```

---

## Customization

Feel free to modify these examples for your own use cases:
- Change target domains
- Adjust batch sizes
- Add data export (CSV, JSON, database)
- Implement rate limiting
- Add logging
