import { NFTIndexer } from '../services/ton/NFTIndexer';
import { UnifiedMarketAdapter } from '../services/markets/UnifiedMarketAdapter';
import { CONFIG } from '../config';

/**
 * CRON Job: Индексация NFT коллекций
 *
 * Запуск: каждые 5 минут (CONFIG.INDEX_INTERVAL)
 * Действия:
 * 1. Индексировать все NFT из известных коллекций
 * 2. Обновить listings с GetGems
 * 3. Обновить floor price коллекций
 */
export async function indexCollectionsJob(): Promise<void> {
  console.log('\n[Job:IndexCollections] Starting...');
  const startTime = Date.now();

  const nftIndexer = new NFTIndexer();
  const marketAdapter = new UnifiedMarketAdapter();

  for (const collectionAddress of CONFIG.GIFT_COLLECTIONS) {
    try {
      console.log(`\n[Job] Processing collection: ${collectionAddress}`);

      // 1. Индексируем все NFT из коллекции (metadata + base data)
      await nftIndexer.indexCollection(collectionAddress);

      // 2. Индексируем listings со ВСЕХ маркетов (GetGems, Fragment, TON Diamonds, etc)
      const stats = await marketAdapter.indexCollection(collectionAddress);

      console.log(`[Job] ✅ ${stats.nfts_indexed} NFTs, ${stats.listings_indexed} listings from ${stats.markets.join(', ')}`);

      // 3. Обновляем floor price коллекции
      await updateCollectionFloorPrice(collectionAddress);
    } catch (error: any) {
      console.error(`[Job] Error processing collection ${collectionAddress}:`, error.message);
    }
  }

  const duration = ((Date.now() - startTime) / 1000).toFixed(2);
  console.log(`\n[Job:IndexCollections] ✅ Completed in ${duration}s\n`);
}

/**
 * Обновить floor price коллекции
 */
async function updateCollectionFloorPrice(collectionAddress: string): Promise<void> {
  const { DB } = await import('../db');

  const result = await DB.queryOne<{ floor_price: string }>(
    `SELECT MIN(l.price) as floor_price
     FROM listings l
     JOIN nfts n ON n.address = l.nft_address
     JOIN collections c ON c.id = n.collection_id
     WHERE c.address = $1 AND l.is_active = true`,
    [collectionAddress]
  );

  if (result?.floor_price) {
    await DB.query(
      `UPDATE collections SET floor_price = $1 WHERE address = $2`,
      [result.floor_price, collectionAddress]
    );
    console.log(`[Job] Updated floor price for ${collectionAddress}: ${result.floor_price} TON`);
  }
}

// Если запущен напрямую
if (require.main === module) {
  indexCollectionsJob()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('[Job] Fatal error:', error);
      process.exit(1);
    });
}
