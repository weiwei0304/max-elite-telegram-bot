import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { MAX } from 'max-exchange-api-node';

@Injectable()
export class MaxService {
  private max: InstanceType<typeof MAX>;

  constructor(private readonly config: ConfigService) {
    const accessKey = this.config.getOrThrow<string>('MAX_ACCESS_KEY');
    const secretKey = this.config.getOrThrow<string>('MAX_SECRET_KEY');

    this.max = new MAX({ accessKey, secretKey });
  }

  async getAccounts() {
    const accounts = await this.max.rest.spotWallet.getAccounts({});
    return accounts.map((acc) => {
      const balance = Number(acc.balance);
      const locked = Number(acc.locked);
      return {
        currency: acc.currency,
        balance,
        locked,
        available: balance - locked,
      };
    });
  }

  async getTickers(markets: string[] = ['btctwd', 'ethtwd', 'maxtwd']) {
    const tickers = await this.max.rest.getTickers({ markets });
    return tickers.map((t) => ({
      market: t.market,
      last: Number(t.last),
    }));
  }

  async getSnapshot() {
    try {
      const [accounts, tickers] = await Promise.all([
        this.getAccounts(),
        this.getTickers(),
      ]);

      return {
        accounts,
        tickers,
      };
    } catch (error) {
      console.error('錯誤:', error.message);
      throw error;
    }
  }

  async formatTelegramMessage(): Promise<string> {
    const { accounts, tickers } = await this.getSnapshot();

    const lines = ['📊 MAX 帳戶餘額'];
    for (const acc of accounts) {
      if (acc.balance > 0 || acc.locked > 0) {
        lines.push(
          `${acc.currency}: 可用 ${acc.available.toFixed(8)} | 鎖定 ${acc.locked.toFixed(8)}`,
        );
      }
    }

    const priceLines = ['📈 目前市價'];
    for (const t of tickers) {
      const price = parseFloat(t.last.toString());
      const marketName = t.market.toUpperCase();
      priceLines.push(`${marketName}: ${price.toLocaleString('zh-TW')}`);
    }

    return lines.join('\n') + '\n\n' + priceLines.join('\n');
  }
}
