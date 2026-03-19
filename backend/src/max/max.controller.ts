import { Controller, Get } from '@nestjs/common';
import { MaxService } from './max.service';

@Controller()
export class MaxController {
  constructor(private readonly maxService: MaxService) {}
  @Get('balance')
  async getBalance() {
    const data = await this.maxService.getAccounts();
    return { data };
  }

  @Get('tickers')
  async getTickers() {
    const data = await this.maxService.getTickers();
    return { data };
  }

  @Get('snapshot')
  async getSnapshot() {
    const data = await this.maxService.getSnapshot();
    return { data };
  }

  @Get('telegram/message')
  async getTelegramMessage() {
    const message = await this.maxService.formatTelegramMessage();
    console.log('[API] /telegram/message called at', new Date().toISOString());
    return { message };
  }
}
