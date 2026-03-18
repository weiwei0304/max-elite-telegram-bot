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
}
