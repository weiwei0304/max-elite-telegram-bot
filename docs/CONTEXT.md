# 專案脈絡與階段性架構規劃

## 0. 下次回來先看這裡（快速接手）

> 最後更新：2026-03-24

### 目前做到哪裡

- 已完成階段一（NestJS + Render + GitHub Actions 排程 + Telegram 推播）。
- 已完成階段二（Supabase + Prisma + Balance Snapshot 落地）。
- 已完成階段三前半段：
  - `fetch_feed.py` 重構為函式化（`build_request`、`fetch_rss`、`fetch_article_html`、`extract_text_from_html`、`save_articles`、`main`）
  - Supabase 建立 `news_articles` 資料表（含 url UNIQUE 防重複）
  - Python 透過 `psycopg2` + `.env` 連線 Supabase
  - 抓 Coindesk RSS 全部文章並寫入資料庫，重複執行安全（ON CONFLICT DO NOTHING）

### 目前狀態判斷

- 階段三「爬蟲入庫」已完成，資料可穩定累積。
- 尚未做 chunking、embedding、pgvector。
- 尚未排程化（還是手動跑）。

### 你下次回來建議直接做

1. **資料品質檢查**：進 Supabase 隨機看幾筆 `content`，確認文字乾淨沒有殘留 UI 文字。
2. **chunking**：把每篇 `content` 切成固定長度段落（建議 500 字、overlap 50 字）。
3. 串 **Gemini embedding API**，把每個 chunk 轉成向量。
4. 在 `news_articles` 或新表加 `embedding vector(768)` 欄位，寫入向量。
5. 最後才接 RAG 查詢流程到 Telegram 問答。

### 已知待處理事項（技術債）

- 目前僅抓 Coindesk 單一來源，之後要擴充來源。
- 內文清理邏輯偏粗略，可能殘留導覽文字或廣告片段。
- 還沒有 HTTP 重試機制（單篇抓取失敗只是跳過）。
- 還沒有把 Python service 放進排程（GitHub Actions 或 Render Cron）。
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
- [ ] **文本清理與分塊 (Chunking)**：將新聞長文切分成適合 AI 處理的段落。
- [ ] **Embedding (向量化)**：呼叫 Google Gemini API (Free tier) 將新聞段落轉換為向量 (Vector)。
- [ ] **寫入向量資料庫**：將向量與原文對應存入 Supabase 的 `pgvector` 資料表中。

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
