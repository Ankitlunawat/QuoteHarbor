# QuoteHarbor

Text extraction and research workspace with traceable source records.

## What is this project used for?

QuoteHarbor demonstrates a repeatable way to extract text, author names, topics and source links from paginated public web pages. A researcher can inspect structured records, search text, filter authors and topics, and export the relevant subset as CSV or JSON. It illustrates content research and text dataset preparation rather than another product-price catalogue scraper.

## Features

- Real HTTP extraction from the Quotes to Scrape practice website.
- Exact host allowlist, robots checks, bounded pagination and request pacing.
- Timeouts, bounded retries and redirect refusal.
- Deterministic identifiers, duplicate removal and required-field validation.
- Capture timestamp, source links, rejected-entry and duplicate metrics.
- Responsive React inspector with author/topic filters and CSV/JSON exports.

## Run extraction

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scraper.py --pages 3 --output output
```

On Windows activate `.venv\Scripts\activate`. Output files are `output/capture.json` (records and metrics) and `output/quotes.csv`. Page limit: 1–10. The source is fixed to `https://quotes.toscrape.com/`; arbitrary websites are not accepted. New source adapters require their own permission checks and selector tests.

## Inspect and rebuild

Requires Node 20.19+ or 22.12+.

```bash
cd frontend
npm ci
npm run dev
npm run build
```

The frontend imports the saved capture; rerun extraction and rebuild to update it. `docs/` contains the compiled public interface. Browser filtering and exports work on saved records. The interface does not launch live scraping or claim an active scheduler.

## Actual sample run

The included capture contains 30 unique records from three pages, collected on 15 October 2026, with zero duplicates and zero rejected entries. Quotes to Scrape is a public practice source; author names, text and tags come from that source. Original attribution links are retained. This is an independent personal project, not a paid engagement or a claim of commercial outcomes.

## Validation

```bash
python -m unittest discover -s tests -v
cd frontend && npm ci && npm run build
```

Tests cover field parsing, whitespace normalization, deterministic identifiers, pagination, malformed records and source scope. A live three-page extraction and production frontend build were also completed.

## Structure

`scraper.py`: extraction, validation and export. `tests/`: parser and scope tests. `output/`: actual capture. `frontend/src/`: searchable React workspace. `docs/`: browser build.
