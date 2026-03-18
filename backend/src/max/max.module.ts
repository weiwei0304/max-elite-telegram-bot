import { Module } from '@nestjs/common';
import { MaxController } from './max.controller';
import { MaxService } from './max.service';

@Module({
  controllers: [MaxController],
  providers: [MaxService],
})
export class MaxModule {}
