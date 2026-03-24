import ssl
import urllib.request

import certifi
import feedparser
from bs4 import BeautifulSoup

FEED_URL='https://www.coindesk.com/arc/outboundfeeds/rss'

ctx = ssl.create_default_context(cafile = certifi.where())

req = urllib.request.Request(
    FEED_URL,
    headers={
        "User-Agent":(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept":"application/rss+xml, application/xml;q=0.9, */*;q=0.8"
    }
)

with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
    data = response.read()

text = data.decode('utf-8', errors='replace')
feed = feedparser.parse(text)
print('entries:', len(feed.entries))
for i, e in enumerate(feed.entries[:3]):
    print('---', i)
    print('title:', e.get('title'))
    print('link:', e.get('link'))
    print('published:', e.get('published') or e.get('updated'))

article_url = feed.entries[0].get('link')
print('article_url:', article_url)

if article_url:
    article_req = urllib.request.Request(
        article_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )

    with urllib.request.urlopen(article_req, context=ctx, timeout=30) as response:
        html_bytes = response.read()

    html_text = html_bytes.decode('utf-8', errors='replace')
    print('html_len:', len(html_text))
    soup = BeautifulSoup(html_text, 'html.parser')
# 先移除高噪音區塊，避免抓到一堆腳本與樣式
for tag in soup(['script', 'style', 'noscript']):
    tag.decompose()
# 優先嘗試 article 區塊；抓不到再退回 body
article_tag = soup.find('article')
target = article_tag if article_tag else soup.body
if target:
    text = target.get_text(separator=' ', strip=True)
else:
    text = soup.get_text(separator=' ', strip=True)
print('article_text_len:', len(text))
print('article_text_preview:', text[:500])