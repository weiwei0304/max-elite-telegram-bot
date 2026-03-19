// 從 .env 讀取環境變數
require("dotenv").config();

//const { MAX } = require("max-exchange-api-node");

async function sendBalance() {
  try {
    // const max = new MAX({
    //   accessKey: process.env.MAX_ACCESS_KEY,
    //   secretKey: process.env.MAX_SECRET_KEY,
    // });

    // const accounts = await max.rest.spotWallet.getAccounts({});
    // // 目前市價
    // const marketsToShow = ["btctwd", "ethtwd", "maxtwd"];
    // const tickers = await max.rest.getTickers({ markets: marketsToShow });

    // const priceLines = ["📈 目前市價"];
    // for (const t of tickers) {
    //   const price = parseFloat(t.last.toString());
    //   const marketName = t.market.toUpperCase();
    //   priceLines.push(`${marketName}: ${price.toLocaleString("zh-TW")}`);
    // }

    // const lines = ["📊 MAX 帳戶餘額"];
    // for (const acc of accounts) {
    //   const balance = parseFloat(acc.balance.toString());
    //   const locked = parseFloat(acc.locked.toString());
    //   const available = balance - locked;
    //   if (balance > 0 || locked > 0) {
    //     lines.push(
    //       `${acc.currency}: 可用 ${available.toFixed(8)} | 鎖定 ${locked.toFixed(8)}`,
    //     );
    //   }
    // }
    // const message = lines.join("\n") + "\n\n" + priceLines.join("\n");

    const backendUrl = process.env.BACKEND_URL || "http://localhost:3000";
    const snapshotRes = await fetch(`${backendUrl}/telegram/message`);

    if (!snapshotRes.ok) {
      console.error(
        "取得 Nest 訊息失敗:",
        snapshotRes.status,
        await snapshotRes.text(),
      );
      return;
    }
    const payload = await snapshotRes.json();
    const message = payload.message;

    const token = process.env.TELEGRAM_BOT_TOKEN;
    const chatId = process.env.TELEGRAM_CHAT_ID;
    const url = `https://api.telegram.org/bot${token}/sendMessage?chat_id=${chatId}&text=${encodeURIComponent(message)}`;
    const res = await fetch(url);

    if (!res.ok) {
      console.error("Telegram 發送失敗:", res.status, await res.text());
      return;
    }
    console.log("已發送:", new Date().toLocaleString("zh-TW"));
  } catch (err) {
    console.error("錯誤:", err.message);
  }
}

const runOnce = process.env.RUN_ONCE === "1";

if (runOnce) {
  sendBalance()
    .then(() => process.exit(0))
    .catch((err) => {
      console.error("錯誤:", err.message);
      process.exit(1);
    });
} else {
  sendBalance();
  setInterval(sendBalance, 2 * 60 * 60 * 1000);
}
