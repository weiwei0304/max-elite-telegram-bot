# 專案脈絡（給新聊天與自己參考）

這份文件是根據開發過程中的對話整理而成，方便**新開 Cursor 聊天時**用 `@docs/CONTEXT.md` 帶入脈絡，或自己之後維護專案時快速回憶「做過什麼、為什麼這樣做、接下來要做什麼」。

---

## 一、專案從哪裡來

- 因參加 **MAX 8 週年慶交易競賽 - 菁英組**，希望定時收到 MAX 帳戶與行情資訊。
- 同時作為**轉職 AI 應用工程師**的練習：學習 API 串接、定時任務、前後端分離、之後加入 Python／NestJS／React，並以**完全免費**方式部署。

---

## 二、目前已完成的事

1. **Git 與 GitHub**
   - 專案已用 `.gitignore` 排除 `.env`、`node_modules` 等，並 push 到公開 repo（例如 weiwei0304/max-elite-telegram-bot）。

2. **Telegram Bot**
   - 透過 BotFather 建立 Bot，取得 Token 與 Chat ID；已確認能發送訊息（需先對 Bot 傳過 /start）。

3. **MAX API**
   - 使用私人 API（個人及帳戶讀取、訂單讀取）取得餘額；使用公開 API（getTickers）取得市價。金鑰存於 `.env`（MAX_ACCESS_KEY、MAX_SECRET_KEY）。

4. **send-balance.js**
   - 用 Node.js + dotenv + max-exchange-api-node：
     - 讀取 .env
     - 呼叫 `spotWallet.getAccounts({})` 取得各幣餘額（可用 = balance - locked）
     - 呼叫 `getTickers({ markets: ['btctwd','ethtwd','maxtwd'] })` 取得目前市價
     - 組成一則訊息（餘額 + 市價），用 Telegram Bot API 的 sendMessage 發送
   - 本機用 `setInterval` 每 10 分鐘執行一次；之後上 GitHub Actions 時會改為「只執行一次」，由 workflow 排程觸發（建議每 30 分鐘～1 小時以節省免費額度）。

5. **名詞與單位**
   - 餘額的「單位」即該行幣別（twd=台幣、eth=以太坊、max=MAX 代幣）。
   - 「鎖定」= 被掛單等占用的金額；「可用」= 可自由使用的部分。

---

## 三、做過的決定與原因

- **不定義 IP 白名單**：方便之後用 GitHub Actions 或免費雲端跑腳本，IP 會變動。
- **只開讀取、不開寫入**：目前僅需查餘額與市價；若未來要參加「API 交易量」採計，才需開訂單寫入。
- **定時用 GitHub Actions**：不需自架硬體；排程勿過密以維持免費（例如每 30 分鐘～1 小時）。
- **完全免費方案**：GitHub（+ Actions）、Vercel（React）、Render（NestJS）、Supabase 或 Neon（DB），不買硬體、不付費。

---

## 四、規劃中的擴充（尚未實作）

- **GitHub Actions**：建立 workflow，每 30 分鐘～1 小時執行一次「只跑一次的發送腳本」，並用 GitHub Secrets 存金鑰。
- **Python**：爬虛擬貨幣新聞、簡單情緒分析；可選輕量模型（特徵+標籤）產出「看多/看空」或關注列表，供學習 pipeline，不保證預測準確。
- **NestJS**：後端 API（餘額、市價、新聞、模型結果）、定時任務（可與 Actions 分攤）、寫入 DB。
- **React + TypeScript**：儀表板（餘額、市價、新聞、模型建議）、設定頁；部署到 Vercel。
- **資料庫**：存歷史餘額、市價、新聞與情緒等，供前端與模型使用（Supabase 或 Neon 免費方案）。

---

## 五、新聊天時怎麼用這份檔案

在新 Cursor 聊天開頭可以這樣寫：

- 「這是 max-elite-telegram-bot 專案，請先讀 @.cursor/rules 和 @docs/CONTEXT.md，我們接下來要做 [具體事項]。」
- 或：「延續 CONTEXT 裡的規劃，我們現在要做 GitHub Actions / Python 爬蟲 / NestJS API / React 儀表板…」

這樣新聊天就能延續同一個專案邏輯與決策，不必從頭口述。

---

## 六、以後怎麼維護這類檔案

- **.cursor/rules/*.mdc**：放「規則類」內容（專案目標、技術棧、程式約定），簡短、可多則規則分檔；Cursor 會自動參考。
- **docs/CONTEXT.md**：放「脈絡類」內容（做過什麼、為什麼、下一步），可較長、敘事化；新聊天用 @ 提到即可帶入。
- 每完成一個階段或做重要決定時，更新 CONTEXT 的「目前已完成」與「規劃中的擴充」，並在規則裡補上新的約定或檔案說明。
