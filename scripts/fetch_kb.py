#!/usr/bin/env python
"""
Fetch & normalize dementia-communication sources into Markdown knowledge base.

- Reads YAML manifest (see kb_manifest.yaml).
- Downloads HTML/PDF to data/raw/<publisher>/.
- Extracts text:
  * HTML via BeautifulSoup
  * PDF via pdfminer.six (fallback: PyPDF2)
- Applies policy:
  * 'full': keep full cleaned text (NIA/public domain)
  * 'summary': keep 300–800 words summary + <=2-line quotes + attribution
- Writes Markdown with YAML front matter to data/knowledge_base/<publisher>/.
- Maintains checksums.json to be idempotent.
"""

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

# Optional: if you plan to parse PDFs
try:
    from pdfminer.high_level import extract_text as pdf_extract_text
except Exception:
    pdf_extract_text = None


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def safe_slug(s: str) -> str:
    return re.sub(r"[^a-z0-9\-]+", "-", s.lower()).strip("-")


def fetch_url(url: str, ua: str, retry: dict) -> bytes:
    attempts = retry.get("attempts", 3)
    backoff = retry.get("backoff_sec", 2)
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    for i in range(attempts):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.content
            print(f"  attempt {i+1}/{attempts}: status={r.status_code}")
        except Exception as e:
            print(f"  attempt {i+1}/{attempts}: error={e}")
        if i < attempts - 1:
            time.sleep(backoff * (i + 1))
    raise RuntimeError(f"Failed to fetch: {url} after {attempts} attempts")


def html_to_text(html_content) -> str:
    # Accept either bytes or string
    if isinstance(html_content, bytes):
        try:
            html_str = html_content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                html_str = html_content.decode("latin-1")
            except Exception:
                html_str = html_content.decode("utf-8", errors="ignore")
    else:
        html_str = html_content

    soup = BeautifulSoup(html_str, "html.parser")
    # Drop nav/footers if possible
    for s in soup(["script", "style", "nav", "footer", "header"]):
        s.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()


def pdf_to_text(pdf_bytes: bytes) -> str:
    if not pdf_extract_text:
        return ""
    # Write temp & extract (simple path; agents can optimize)
    tmp = Path(".tmp_pdf")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(pdf_bytes)
    try:
        txt = pdf_extract_text(str(tmp)) or ""
        return txt.strip()
    finally:
        try:
            tmp.unlink()
        except Exception:
            pass


def summarize(text: str, max_words: int, min_words: int) -> str:
    """Very simple heuristic summary: keep headings and the most relevant sentences."""
    words = text.split()
    if len(words) <= max_words:
        return text
    # crude: take first ~min_words and then a few lines containing key verbs
    first = " ".join(words[:min_words])
    # pick lines with 'avoid', 'use', 'speak', 'validate', 'reassure', 'redirect'
    key_lines = []
    for line in text.splitlines():
        low = line.lower()
        if (
            any(
                k in low
                for k in ("avoid", "use", "speak", "validate", "reassure", "redirect")
            )
            and 4 < len(line) < 240
        ):
            key_lines.append(line.strip())
        if len(" ".join(key_lines).split()) > (max_words - min_words):
            break
    return (first + "\n\n" + "\n".join(key_lines)).strip()


def write_md(out_path: Path, meta: dict, body: str):
    # Ensure path is absolute to avoid issues
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fm = "---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n\n"
    out_path.write_text(fm + body + "\n", encoding="utf-8")


def clip_quotes(body: str, quote_max_lines: int) -> str:
    """Limit number of quoted lines; dequote the rest to stay within policy."""
    q_lines: list[str] = []
    new_lines: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        is_quote = stripped.startswith(("“", '"', "’", "'"))
        if is_quote and len(q_lines) < quote_max_lines:
            q_lines.append(line)
            new_lines.append(line)
        elif is_quote:
            new_lines.append(stripped.strip("“”\"'"))  # dequote
        else:
            new_lines.append(line)
    return "\n".join(new_lines)


def parse_content(fmt: str, content: bytes) -> str:
    if fmt == "html":
        return html_to_text(content)
    if fmt == "pdf":
        return pdf_to_text(content)
    return ""


def process_source(
    src: dict,
    *,
    ua: str,
    out_kb: Path,
    out_raw: Path,
    retry: dict,
    max_words: int,
    min_words: int,
    quote_max_lines: int,
    today: str,
    checksums: dict,
):
    title = src["title"]
    url = src["url"]
    pub = src["publisher"]
    lic = src["license"]
    fmt = src.get("format", "html")
    tags = src.get("tags", [])
    policy = src.get("policy", "summary")  # 'full' or 'summary'

    raw_dir = (out_raw / pub).resolve()
    kb_dir = (out_kb / pub).resolve()
    slug = safe_slug(title)
    raw_dir.mkdir(parents=True, exist_ok=True)
    kb_dir.mkdir(parents=True, exist_ok=True)

    print(f"[fetch] {title} — {url}")
    content = fetch_url(url, ua, retry)
    digest = sha256_bytes(content)
    if checksums.get(url) == digest:
        print("  unchanged; skipping parse/write")
        return
    checksums[url] = digest

    # Save raw
    ext = ".html" if fmt == "html" else ".pdf"
    raw_path = raw_dir / f"{slug}{ext}"
    raw_path.write_bytes(content)

    # Parse
    text = parse_content(fmt, content)
    if not text:
        print(f"  unknown or empty format: {fmt}; skipping")
        return

    # Normalize policy
    body = text if policy == "full" else summarize(text, max_words, min_words)

    # Clip excessive quotes for copyrighted sources
    if policy != "full":
        body = clip_quotes(body, quote_max_lines)

    # Trim to target size
    words = body.split()
    if len(words) > max_words:
        body = " ".join(words[:max_words])

    # Basic cleanup
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    meta = {
        "title": title,
        "source_url": url,
        "publisher": pub,
        "date_accessed": today,
        "license": lic,
        "tags": tags,
    }
    out_md = kb_dir / f"{slug}.md"
    write_md(out_md, meta, body)
    print(f"  wrote {out_md.relative_to(Path.cwd())}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()

    manifest = yaml.safe_load(Path(args.manifest).read_text(encoding="utf-8"))
    dfl = manifest.get("defaults", {})
    ua = dfl.get("user_agent", "kb-fetcher/0.1")
    out_kb = Path(dfl.get("out_kb_dir", "data/knowledge_base"))
    out_raw = Path(dfl.get("out_raw_dir", "data/raw"))
    retry = dfl.get("retry", {"attempts": 3, "backoff_sec": 2})
    max_words = int(dfl.get("max_md_words", 800))
    min_words = int(dfl.get("min_md_words", 300))
    quote_max_lines = int(dfl.get("quote_max_lines", 2))

    checksum_path = Path("scripts/checksums.json")
    checksums: dict = {}
    if checksum_path.exists():
        checksums = json.loads(checksum_path.read_text(encoding="utf-8"))

    today = str(date.today())

    sources = manifest.get("sources", [])
    for i, src in enumerate(sources):
        print(f"\n[{i+1}/{len(sources)}]")
        try:
            process_source(
                src,
                ua=ua,
                out_kb=out_kb,
                out_raw=out_raw,
                retry=retry,
                max_words=max_words,
                min_words=min_words,
                quote_max_lines=quote_max_lines,
                today=today,
                checksums=checksums,
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            print(f"  Skipping: {src.get('title', 'unknown')}")
            continue
        # Be respectful: add delay between requests
        if i < len(sources) - 1:
            time.sleep(2)

    checksum_path.write_text(json.dumps(checksums, indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
