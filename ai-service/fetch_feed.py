import os
import ssl
import urllib.request

import certifi
import feedparser
import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

FEED_URL='https://www.coindesk.com/arc/outboundfeeds/rss'

ctx = ssl.create_default_context(cafile = certifi.where())

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

def build_request(url: str, accept_header: str) -> urllib.request.Request:
    return urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": accept_header,
        },
    )
def fetch_rss(feed_url: str) -> list[dict]:
    req = build_request(feed_url, "application/rss+xml, application/xml;q=0.9, */*;q=0.8")
    with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
        data = response.read()
    text = data.decode('utf-8', errors='replace')
    feed = feedparser.parse(text)
    entries = []
    for e in feed.entries:
        entries.append({
            "title": e.get("title"),
            "url": e.get("link"),
            "published": e.get("published") or e.get("updated"),
        })
    return entries
def fetch_article_html(article_url: str) -> str:
    req = build_request(article_url, "text/html,application/xhtml+xml,*/*;q=0.8")
    with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
        html_bytes = response.read()
    return html_bytes.decode('utf-8', errors='replace')
def extract_text_from_html(html_text: str) -> str:
    soup = BeautifulSoup(html_text, 'html.parser')
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()
    article_tag = soup.find('article')
    target = article_tag if article_tag else soup.body
    if target:
        return target.get_text(separator=' ', strip=True)
    return soup.get_text(separator=' ', strip=True)

def save_articles(articles: list[dict]) -> None:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    inserted = 0
    skipped = 0
    for article in articles:
        cur.execute(
            """
            INSERT INTO news_articles (source, title, url, published_at, content)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
            """,
            (
                article["source"],
                article["title"],
                article["url"],
                article["published_at"],
                article["content"],
            ),
        )
        if cur.rowcount == 1:
            inserted += 1
        else:
            skipped += 1
    conn.commit()
    cur.close()
    conn.close()
    print(f"寫入：{inserted} 筆，跳過（重複）：{skipped} 筆")

def main() -> None:
    try:
        entries = fetch_rss(FEED_URL)
        print(f'RSS 共 {len(entries)} 篇文章')

        articles = []
        for i, entry in enumerate(entries):
            print(f'抓取第 {i + 1}/{len(entries)} 篇：{entry["title"]}')
            try:
                html = fetch_article_html(entry["url"])
                content = extract_text_from_html(html)
                articles.append({
                    "source": "coindesk",
                    "title": entry["title"],
                    "url": entry["url"],
                    "published_at": entry["published"],
                    "content": content,
                })
            except Exception as e:
                print(f'  跳過（抓取失敗）：{e}')

        print(f'成功抓取 {len(articles)} 篇，準備寫入資料庫...')
        save_articles(articles)
        print('OK')
    except Exception as e:
        print('ERROR:', e)

if __name__ == '__main__':
    main()