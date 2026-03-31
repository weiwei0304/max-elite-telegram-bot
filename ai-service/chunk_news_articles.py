import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("找不到 DATABASE_URL，請確認 ai-service/.env 有設定。")


def chunk_words(text: str, chunk_size_words: int = 250, overlap_words: int = 50) -> list[str]:
    # 用詞切塊，比較不會把單字切斷；overlap 讓相鄰 chunk 保留上下文
    words = text.split()
    if not words:
        return []

    chunks = []
    i = 0
    while i < len(words):
        end = i + chunk_size_words
        chunk = " ".join(words[i:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
        i = end - overlap_words
        if i < 0:
            i = 0
    return chunks


def main() -> None:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # 撈出尚未 chunk 過的文章（粗略：假設只要有 chunk 表就代表已處理）
    cur.execute("""
      SELECT a.url, a.content
      FROM public.news_articles a
      WHERE a.content IS NOT NULL
        AND NOT EXISTS (
          SELECT 1
          FROM public.news_article_chunks c
          WHERE c.article_url = a.url
        )
      LIMIT 50;
    """)
    rows = cur.fetchall()

    total_articles = len(rows)
    total_chunks = 0
    inserted_chunks = 0

    for (article_url, content) in rows:
        if not content:
            continue

        chunks = chunk_words(content, chunk_size_words=250, overlap_words=50)
        total_chunks += len(chunks)

        for idx, chunk_text in enumerate(chunks):
            cur.execute("""
              INSERT INTO public.news_article_chunks (article_url, chunk_index, chunk_text)
              VALUES (%s, %s, %s)
              ON CONFLICT (article_url, chunk_index) DO NOTHING
            """, (article_url, idx, chunk_text))
            if cur.rowcount == 1:
                inserted_chunks += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"待處理文章數: {total_articles}")
    print(f"理論產生 chunk 數: {total_chunks}")
    print(f"實際插入 chunk 數: {inserted_chunks}")


if __name__ == "__main__":
    main()