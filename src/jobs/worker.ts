import { Queue, Worker } from 'bullmq';
import pino from 'pino';

const logger = pino({ name: 'ozon-worker' });

const connection = {
  host: process.env.REDIS_HOST ?? 'localhost',
  port: Number(process.env.REDIS_PORT ?? 6379),
};

export const syncQueue = new Queue('ozon-sync', { connection });

new Worker(
  'ozon-sync',
  async (job) => {
    logger.info({ job: job.name }, 'Running sync job');
  },
  { connection },
);

logger.info('Worker started');
