# 從資料庫抓取還沒建立向量的新聞片段，透過Gemini轉成向量之後再存進去

import os
import time
import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL is not set')
if not GEMINI_API_KEY:
    raise RuntimeError('GEMINI_API_KEY is not set')

client = genai.Client(api_key=GEMINI_API_KEY)


def get_embedding(text: str) -> str:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    values = result.embeddings[0].values
    return "[" + ",".join(str(v) for v in values) + "]"


def main() -> None:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        SELECT article_url, chunk_index, chunk_text
        FROM public.news_article_chunks
        WHERE embedding IS NULL
        LIMIT 50;
    """)
    rows = cur.fetchall()
    print(f"待 embedding chunk 數: {len(rows)}")

    success = 0
    for (article_url, chunk_index, chunk_text) in rows:
        try:
            embedding = get_embedding(chunk_text)
            cur.execute("""
                UPDATE public.news_article_chunks
                SET embedding = %s::vector
                WHERE article_url = %s AND chunk_index = %s
            """, (embedding, article_url, chunk_index))
            conn.commit()
            success += 1
            print(f"  完成 {success}/{len(rows)}")
            time.sleep(1)
        except Exception as e:
            conn.rollback()
            print(f"  失敗（{article_url} chunk {chunk_index}）: {e}")

    cur.close()
    conn.close()
    print(f"完成，成功 embedding: {success} 筆")


if __name__ == "__main__":
    main()