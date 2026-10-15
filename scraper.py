"""Bounded text extraction from the public Quotes to Scrape practice site."""
import argparse
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = 'https://quotes.toscrape.com/'
AGENT = 'QuoteHarbor/1.0 (educational text extraction)'

def allowed(url):
    parts = urlsplit(url)
    return parts.scheme == 'https' and parts.netloc == 'quotes.toscrape.com' and not parts.query

def parse_page(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    records, rejected = [], 0
    for quote in soup.select('.quote'):
        text = quote.select_one('.text')
        author = quote.select_one('.author')
        profile = quote.select_one('a[href^="/author/"]')
        if not text or not author or not profile:
            rejected += 1
            continue
        text = ' '.join(text.get_text().split())
        author = ' '.join(author.get_text().split())
        if not text or not author:
            rejected += 1
            continue
        records.append({'id': hashlib.sha256((author + '\0' + text).encode()).hexdigest()[:20], 'text': text, 'author': author,
                        'tags': [tag.get_text(strip=True) for tag in quote.select('.tag')],
                        'author_url': urljoin(BASE, profile['href']), 'source_url': url})
    link = soup.select_one('li.next a')
    return records, urljoin(url, link['href']) if link else None, rejected

def scrape(pages=3, delay=1.0):
    if not 1 <= pages <= 10 or delay < 1: raise ValueError('Use 1–10 pages and at least one second between requests')
    session = requests.Session()
    session.headers['User-Agent'] = AGENT
    session.mount('https://', HTTPAdapter(max_retries=Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
    robots_response = session.get(urljoin(BASE, 'robots.txt'), timeout=20, allow_redirects=False)
    robots = RobotFileParser()
    if robots_response.status_code == 404: robots.parse(['User-agent: *', 'Allow: /'])
    else:
        robots_response.raise_for_status()
        if robots_response.status_code != 200: raise RuntimeError('Unexpected robots response')
        robots.parse(robots_response.text.splitlines())
    results, seen, visited = [], set(), set()
    duplicates = rejected = 0
    url = BASE
    for _ in range(pages):
        if not url or url in visited: break
        if not allowed(url) or not robots.can_fetch(AGENT, url): raise ValueError('Source is outside the allowed crawl scope')
        time.sleep(max(delay, robots.crawl_delay(AGENT) or 0))
        response = session.get(url, timeout=20, allow_redirects=False)
        response.raise_for_status()
        if response.status_code != 200: raise RuntimeError('Redirects and non-200 responses are not followed')
        records, next_url, errors = parse_page(response.text, url)
        if not records: raise RuntimeError('No records found; source structure may have changed')
        visited.add(url); rejected += errors
        for record in records:
            if record['id'] in seen: duplicates += 1; continue
            seen.add(record['id']); results.append(record)
        url = next_url
    return {'captured_at': datetime.now(timezone.utc).isoformat(), 'pages': len(visited), 'duplicates': duplicates, 'rejected': rejected, 'records': results}

def write_output(data, directory):
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    (directory / 'capture.json').write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    with (directory / 'quotes.csv').open('w', newline='', encoding='utf-8') as stream:
        fields = ['id', 'text', 'author', 'tags', 'author_url', 'source_url']
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        for row in data['records']:
            row = {**row, 'tags': ', '.join(row['tags'])}
            writer.writerow({k: "'" + str(v) if str(v).lstrip().startswith(('=', '+', '-', '@')) else v for k, v in row.items()})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pages', type=int, default=3)
    parser.add_argument('--output', default='output')
    args = parser.parse_args()
    result = scrape(args.pages)
    write_output(result, args.output)
    print(json.dumps({key: len(value) if key == 'records' else value for key, value in result.items()}))
