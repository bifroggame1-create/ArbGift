import axios, { AxiosInstance } from 'axios';
import { CONFIG } from '../../config';
import { DB } from '../../db';

/**
 * TonApiAdapter - основной адаптер через tonapi.io
 *
 * Преимущества:
 * - Агрегирует ВСЕ маркеты (GetGems, Fragment, TON Diamonds, etc)
 * - Один источник для всех listings
 * - Официальный API с высоким uptime
 * - Rate limit: 1 req/sec (free), до 10 req/sec (paid)
 */
export class TonApiAdapter {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: CONFIG.TONAPI_BASE_URL,
      headers: CONFIG.TONAPI_KEY
        ? { Authorization: `Bearer ${CONFIG.TONAPI_KEY}` }
        : {},
      timeout: 15000,
    });
  }

  /**
   * Получить все active listings для коллекции
   * Includes: GetGems, Fragment, TON Diamonds, и другие
   */
  async fetchCollectionListings(collectionAddress: string): Promise<number> {
    console.log(`[TonApiAdapter] Fetching listings for collection: ${collectionAddress}`);

    let totalListings = 0;
    let offset = 0;
    const limit = 1000;

    while (true) {
      try {
        const response = await this.api.get(`/nfts/collections/${collectionAddress}/items`, {
          params: { limit, offset },
        });

        const { nft_items, next_from } = response.data;

        if (!nft_items || nft_items.length === 0) break;

        // Фильтруем только NFT с active sale
        const withSale = nft_items.filter((nft: any) => nft.sale);

        for (const nft of withSale) {
          const priceInTON = (parseInt(nft.sale.price.value) / 1e9).toFixed(9);
          const market = nft.sale.market.name.toLowerCase();

          await DB.upsertListing({
            nft_address: nft.address,
            market,
            price: priceInTON,
            seller: nft.sale.owner.address,
            sale_contract_address: nft.sale.address,
            listing_url: this.buildMarketplaceURL(market, nft.address),
          });

          totalListings++;
        }

        console.log(`[TonApiAdapter] Processed ${totalListings} listings...`);

        if (!next_from) break;
        offset = next_from;

        // Rate limiting
        await this.sleep(1100);
      } catch (error: any) {
        console.error(`[TonApiAdapter] Error at offset ${offset}:`, error.message);
        break;
      }
    }

    console.log(`[TonApiAdapter] ✅ Total listings indexed: ${totalListings}`);
    return totalListings;
  }

  /**
   * Получить listing для конкретного NFT
   */
  async fetchNFTListing(nftAddress: string): Promise<void> {
    try {
      const response = await this.api.get(`/nfts/${nftAddress}`);
      const nft = response.data;

      if (nft.sale) {
        const priceInTON = (parseInt(nft.sale.price.value) / 1e9).toFixed(9);
        const market = nft.sale.market.name.toLowerCase();

        await DB.upsertListing({
          nft_address: nft.address,
          market,
          price: priceInTON,
          seller: nft.sale.owner.address,
          sale_contract_address: nft.sale.address,
          listing_url: this.buildMarketplaceURL(market, nft.address),
        });

        console.log(`[TonApiAdapter] Updated listing for ${nft.address} on ${market}`);
      } else {
        // Нет активной продажи — деактивируем старые listings
        await DB.query(
          `UPDATE listings SET is_active = false WHERE nft_address = $1`,
          [nft.address]
        );
      }
    } catch (error: any) {
      console.error(`[TonApiAdapter] Error fetching NFT ${nftAddress}:`, error.message);
    }
  }

  /**
   * Получить статистику по маркетам
   */
  async getMarketStats(): Promise<Array<{
    market: string;
    listings_count: number;
    floor_price: string;
    avg_price: string;
  }>> {
    return await DB.query(`
      SELECT
        market,
        COUNT(DISTINCT nft_address) as listings_count,
        MIN(price::numeric) as floor_price,
        AVG(price::numeric) as avg_price
      FROM listings
      WHERE is_active = true
      GROUP BY market
      ORDER BY listings_count DESC
    `);
  }

  /**
   * Деактивировать stale listings (которых больше нет on-chain)
   */
  async deactivateStaleListings(collectionAddress: string): Promise<void> {
    console.log(`[TonApiAdapter] Checking for stale listings...`);

    // Получаем текущие active sale contracts
    const activeSales = new Set<string>();
    let offset = 0;
    const limit = 1000;

    while (true) {
      try {
        const response = await this.api.get(`/nfts/collections/${collectionAddress}/items`, {
          params: { limit, offset },
        });

        const { nft_items, next_from } = response.data;
        if (!nft_items || nft_items.length === 0) break;

        nft_items
          .filter((nft: any) => nft.sale)
          .forEach((nft: any) => {
            activeSales.add(`${nft.address}:${nft.sale.address}`);
          });

        if (!next_from) break;
        offset = next_from;
        await this.sleep(1100);
      } catch (error) {
        break;
      }
    }

    // Деактивируем listings которых нет в active sales
    const dbListings = await DB.query<{ nft_address: string; sale_contract_address: string }>(
      `SELECT nft_address, sale_contract_address
       FROM listings
       WHERE is_active = true`
    );

    let deactivated = 0;
    for (const listing of dbListings) {
      const key = `${listing.nft_address}:${listing.sale_contract_address}`;
      if (!activeSales.has(key)) {
        await DB.query(
          `UPDATE listings SET is_active = false
           WHERE nft_address = $1 AND sale_contract_address = $2`,
          [listing.nft_address, listing.sale_contract_address]
        );
        deactivated++;
      }
    }

    console.log(`[TonApiAdapter] ✅ Deactivated ${deactivated} stale listings`);
  }

  private buildMarketplaceURL(market: string, nftAddress: string): string {
    switch (market) {
      case 'getgems':
        return `https://getgems.io/nft/${nftAddress}`;
      case 'fragment':
        return `https://fragment.com/nft/${nftAddress}`;
      case 'ton.diamonds':
      case 'tondiamonds':
        return `https://ton.diamonds/nft/${nftAddress}`;
      default:
        return `https://tonapi.io/nft/${nftAddress}`;
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
