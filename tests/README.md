# AutoScraper Tests & Diagnostics

This directory contains diagnostic and testing utilities to help verify your AutoScraper setup.

## Diagnostic Scripts

### 1. `test_env_integrations.py`
**Purpose:** Validates environment configuration and cloud integrations

**What it checks:**
- ✅ `.env` file loading
- ✅ Gemini API key accessibility
- ✅ Google Cloud Storage connection
- ✅ Logging configuration
- ✅ Environment variable setup

**When to run:**
- After initial setup
- Before deployment
- When troubleshooting configuration issues
- To verify cloud credentials

**How to run:**
```bash
python tests/test_env_integrations.py
```

**Expected output:**
```json
{
  "dotenv_used": true,
  "env_vars": {
    "GEMINI_API_KEY": true,
    "GCS_BUCKET_NAME": "your-bucket-name",
    "GCP_PROJECT_ID": "your-project-id"
  },
  "api_key": {"ok": true, "message": "Loaded API key"},
  "logging": {"ok": true, "message": "Env health check log at ..."},
  "storage": {"ok": true, "details": {...}}
}
```

---

### 2. `test_playwright.py`
**Purpose:** Verifies Playwright installation and browser functionality

**What it checks:**
- ✅ Playwright module import
- ✅ Chromium browser launch
- ✅ Page creation
- ✅ Website navigation
- ✅ HTML content retrieval

**When to run:**
- After installing dependencies
- When scraping fails
- To verify browser installation
- Before running agents

**How to run:**
```bash
python tests/test_playwright.py
```

**Expected output:**
```
================================================================================
PLAYWRIGHT DIAGNOSTIC TEST
================================================================================

✓ Test 1: Playwright module imported successfully
✓ Test 2: Browser launched successfully
✓ Test 3: Page created successfully
✓ Test 4: Navigation successful
✓ Test 5: Retrieved 1256 characters of HTML
✓ Test 6: Retrieved 45678 characters from Harvard

✅ ALL TESTS PASSED - Playwright is working correctly!
```

---

### 3. `test_scrapers.py`
**Purpose:** Tests generated scrapers from the repository

**What it checks:**
- ✅ Scraper loading from repository
- ✅ Scraper execution
- ✅ Data extraction validation
- ✅ Error handling

**How to run:**
```bash
python tests/test_scrapers.py
```

---

### 4. `test_tools.py`
**Purpose:** Tests agent tools (analyze_html, test_selector, execute_code)

**What it checks:**
- ✅ HTML fetching and parsing
- ✅ Selector testing functionality
- ✅ Code execution sandbox
- ✅ Tool error handling

**How to run:**
```bash
python tests/test_tools.py
```

---

## Troubleshooting Guide

### Common Issues

#### ❌ "Playwright browsers not installed"
**Solution:**
```bash
playwright install chromium
```

#### ❌ "API key missing or unreadable"
**Solution:**
1. Check `.env` file exists
2. Verify `GEMINI_API_KEY` is set
3. Ensure no extra quotes or spaces

#### ❌ "GCS bucket not accessible"
**Solution:**
1. Verify `GCS_BUCKET_NAME` in `.env`
2. Check service account permissions
3. Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON

#### ❌ "Timeout errors"
**Solution:**
1. Check internet connection
2. Try different websites
3. Increase timeout in code
4. Check firewall/proxy settings

---

## Running All Tests

To run all diagnostic tests at once:

```bash
# Windows PowerShell
Get-ChildItem tests\test_*.py | ForEach-Object { python $_.FullName }

# Linux/Mac
for test in tests/test_*.py; do python "$test"; done
```

---

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run diagnostic tests
  run: |
    python tests/test_env_integrations.py
    python tests/test_playwright.py
```

---

## Adding New Tests

When adding new functionality, create corresponding test files:

1. Name files `test_*.py`
2. Include clear error messages
3. Provide troubleshooting guidance
4. Test both success and failure cases
