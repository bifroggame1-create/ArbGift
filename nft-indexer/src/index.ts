import { startAPIServer } from './api/server';
import { indexCollectionsJob } from './jobs/indexCollections';
import { CONFIG } from './config';

/**
 * Main entry point - запускает:
 * 1. API Server
 * 2. CRON jobs для индексации
 */
async function main() {
  console.log('🚀 TON NFT Market Indexer starting...\n');

  // Запускаем API server
  startAPIServer();

  // Первый запуск индексации сразу
  console.log('[Main] Running initial indexing...');
  await indexCollectionsJob();

  // Запускаем периодическую индексацию
  setInterval(async () => {
    try {
      await indexCollectionsJob();
    } catch (error: any) {
      console.error('[Main] Index job failed:', error.message);
    }
  }, CONFIG.INDEX_INTERVAL);

  console.log(`[Main] ✅ Scheduled indexing every ${CONFIG.INDEX_INTERVAL / 1000}s`);
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('\n[Main] SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\n[Main] SIGINT received, shutting down gracefully...');
  process.exit(0);
});

// Start
main().catch((error) => {
  console.error('[Main] Fatal error:', error);
  process.exit(1);
});
