# 專案脈絡與階段性架構規劃

## 0. 下次回來先看這裡（快速接手）

> 最後更新：2026-03-24

### 目前做到哪裡

- 已完成階段一（NestJS + Render + GitHub Actions 排程 + Telegram 推播）。
- 已完成階段二（Supabase + Prisma + Balance Snapshot 落地）。
- 已完成階段三全部：
  - `fetch_feed.py`：抓 Coindesk RSS → 清理正文 → 寫入 `news_articles`（去重）
  - `chunk_news_articles.py`：把文章切成 250 詞 / overlap 50 詞的 chunk，寫入 `news_article_chunks`
  - `embed_chunks.py`：用 Gemini `gemini-embedding-001` 產生 3072 維向量，寫入 `news_article_chunks.embedding`（`vector(3072)`）
  - 整條管線手動跑通，159 個 chunk 全部 embedding 完成

### 目前狀態判斷

- 階段三「爬蟲 → chunking → embedding」完整跑通。
- 向量已存進 Supabase pgvector，可以做相似度搜尋。
- 下一步是 RAG 查詢 + Telegram 問答（階段四）。
- 尚未排程化（三支腳本都還是手動跑）。

### 你下次回來建議直接做

1. 在 Supabase 啟用 `pgvector` 的 `ivfflat` 或 `hnsw` 索引（加速向量搜尋）。
2. 新增 `rag_query.py`：
   - 輸入一個問題字串
   - 對問題做 embedding
   - 用 `<=>` 做相似度搜尋，撈出最相關的 5 個 chunk
   - 把 chunk + 問題組成 Prompt 傳給 Gemini LLM
   - 回傳答案
3. 把 `rag_query.py` 串進 Telegram Bot（Webhook 或 long polling）。
4. 最後把三支腳本（fetch + chunk + embed）放進 GitHub Actions 排程。

### 已知待處理事項（技術債）

- 目前僅抓 Coindesk 單一來源，之後要擴充。
- 內文清理邏輯偏粗略，可能殘留導覽文字。
- 三支腳本都還是手動跑，尚未排程化。
- `test_db.py` 是臨時測試檔，之後可以刪除。

本專案（max-elite-telegram-bot）的終極目標是打造一個**「具備 RAG (檢索增強生成) 與 Embedding 能力的個人化加密貨幣 AI 助手」**。
同時，這也是一個為轉職「AI 應用工程師」量身打造的實戰練習場，且**全程嚴格採用免費方案**。

---

## 一、 階段性任務與闖關地圖

專案將分為四大階段進行，每完成一階段都會獲得一個可實際運作的成果：

### 🟢 階段一：解耦與微服務化（目前狀態 - 已完成）

**目標**：建立穩定且易於擴充的基礎後端架構。

- [x] **NestJS 後端**：負責與 MAX API 溝通，取得餘額與市價，並組裝 Telegram 訊息。
- [x] **雲端部署**：將 NestJS 部署至 Render (Free tier)。
- [x] **GitHub Actions 排程**：定時執行 `send-balance.js` 向 Render 請求資料並推播至 Telegram。
- **架構特點**：資料擷取邏輯（NestJS）與排程發送（Actions）完全拆分，為未來擴充鋪路。

### 🟡 階段二：引入資料庫與歷史追蹤（下一步）

**目標**：讓系統擁有「記憶」，能追蹤資產變化，並為未來的向量檢索（RAG）準備基礎設施。

- [x] **申請 Supabase**：建立免費的 PostgreSQL 資料庫，並確認支援 `pgvector` 擴充功能。
- [x] **ORM 串接**：在 NestJS 中引入 Prisma 或 TypeORM，連線至 Supabase。
- [x] **資產快照 (Snapshot)**：將每次定時抓到的「帳戶餘額與市價」寫入資料庫，建立歷史時間序列資料。

### 🟠 階段三：Python 爬蟲與 Embedding (AI 基礎建立)

**目標**：開始接觸 AI 應用核心技術，建立外部知識庫。

- [x] **建立 Python 微服務**：已新增 `ai-service` 資料夾。
- [x] **新聞爬蟲**：函式化重構完成，抓取 Coindesk RSS 全部文章並寫入 Supabase，支援去重。
- [x] **文本清理與分塊 (Chunking)**：`chunk_news_articles.py` 完成，250 詞 / overlap 50 詞。
- [x] **Embedding (向量化)**：`embed_chunks.py` 完成，使用 Gemini `gemini-embedding-001`，3072 維向量。
- [x] **寫入向量資料庫**：向量存入 `news_article_chunks.embedding`（`vector(3072)`）。

### 🔴 階段四：RAG 檢索增強生成 (最終目標)

**目標**：讓 Telegram Bot 具備對話與分析能力。

- [ ] **Telegram Webhook**：將 Bot 從單向推播升級為「可接收使用者訊息」的對話機器人。
- [ ] **意圖識別**：當使用者發問時（例如：「最近 BTC 有什麼利多？我的資產夠買嗎？」），判斷是否需要呼叫 AI。
- [ ] **RAG 實作 (檢索 + 生成)**：
  1. 將使用者的問題 Embedding。
  2. 去 Supabase 進行「相似度搜尋 (Similarity Search)」，找出最相關的新聞向量。
  3. 從資料庫撈出使用者「當下的資產狀況」。
  4. 將 **[相關新聞] + [資產狀況] + [使用者問題]** 組合成 Prompt，傳給 Gemini LLM。
- [ ] **回傳答案**：LLM 生成分析報告，透過 Telegram 傳送給使用者。

---

## 二、 完整系統架構圖 (最終形態)

當階段四完成時，系統的資料流將如下圖所示：

```text
                               ┌─────────────────────────┐
                               │   MAX 交易所 API        │
                               └──────────┬──────────────┘
                                          │ (API Keys)
┌─────────────────┐            ┌──────────▼──────────────┐
│ GitHub Actions  ├─(定時觸發)─►│    NestJS (Render)     │◄─(查詢資產)─┐
│ (每2小時)       │            │  (資產快照、路由中心)  │             │
└────────┬────────┘            └──────────┬──────────────┘             │
         │                                │ (寫入快照)                 │
         │                     ┌──────────▼──────────────┐             │
         │ (拿訊息發送)        │   Supabase (PostgreSQL) │             │
         │                     │  [關聯資料] + [pgvector]│◄─(檢索新聞)─┤
         ▼                     └──────────▲──────────────┘             │
┌─────────────────┐                       │ (寫入向量)                 │
│ Telegram Bot    │                       │                            │
│ (推送 / 接收問答)│            ┌──────────┴──────────────┐   ┌─────────┴────────┐
└────────┬────────┘            │ Python AI Service       │   │ Google Gemini API│
         │ (Webhook/長輪詢)    │ (爬蟲、Embedding、RAG)  ├───► (LLM 生成 & 向量化)│
         └────────────────────►│                         │   └──────────────────┘
                               └──────────┬──────────────┘
                                          │ (抓取)
                               ┌──────────▼──────────────┐
                               │ 外部幣圈新聞源 (RSS/API)│
                               └─────────────────────────┘
```
