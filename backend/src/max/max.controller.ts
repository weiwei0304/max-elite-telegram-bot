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
}
