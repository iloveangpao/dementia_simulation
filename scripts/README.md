# Knowledge Base Fetching Scripts

## fetch_kb.py

This script fetches dementia communication sources from the web, normalizes them into Markdown with YAML front matter, and saves them to `data/knowledge_base/`.

### Usage

```bash
python scripts/fetch_kb.py --manifest scripts/kb_manifest.yml
```

### Features

- Downloads HTML and PDF sources
- Applies licensing policies (full text for public domain, summaries for copyrighted content)
- Maintains checksums for idempotent operation (won't re-download unchanged files)
- Extracts and cleans text from HTML using BeautifulSoup
- Extracts text from PDFs using pdfminer.six
- Generates YAML front matter with metadata (title, source URL, publisher, license, tags, date accessed)
- Handles errors gracefully and continues with remaining sources

### Dependencies

The following packages are required and included in requirements.txt:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `pdfminer.six` - PDF text extraction
- `brotli` - Brotli decompression support for websites using br encoding
- `PyYAML` - YAML parsing

### Manifest Format

The `kb_manifest.yml` file defines sources to fetch:

```yaml
defaults:
  out_kb_dir: data/knowledge_base
  out_raw_dir: data/raw
  user_agent: "Mozilla/5.0 ..."
  max_md_words: 800
  min_md_words: 300
  quote_max_lines: 2
  retry: { attempts: 3, backoff_sec: 3 }

sources:
  - title: "Source Title"
    publisher: "Publisher Name"
    license: "License Type"
    url: "https://example.com/source"
    format: "html"  # or "pdf"
    tags: ["tag1", "tag2"]
    policy: "full"  # or "summary"
```

### Output

- Raw files saved to: `data/raw/<publisher>/<slug>.<ext>`
- Normalized markdown files saved to: `data/knowledge_base/<publisher>/<slug>.md`
- Checksums stored in: `scripts/checksums.json`

### Status

Current fetch status (as of last run):
- **10 of 15 sources successfully downloaded**
- Failed sources:
  - 4 NIA sources (nia.nih.gov) - returning 405 errors (CAPTCHA protection)
  - 1 Alzheimer's Society UK source - returning 404 error (URL may have changed)

The successfully downloaded sources provide comprehensive coverage of dementia communication best practices from various authoritative sources including WHO, NHS, VA, and others.
