import axios, { AxiosInstance } from 'axios';
import { DB } from '../../db';

/**
 * MajorAdapter - индексация через Major.tg публичный API
 *
 * Преимущества:
 * - NO AUTH required (самый простой доступ)
 * - Чистый JSON API
 * - Поддержка Fragment и GetGems NFT
 * - Pagination и фильтрация
 */
export class MajorAdapter {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: 'https://major.tg/api/v1',
      timeout: 15000,
    });
  }

  /**
   * Получить все listings с Major.tg
   * API: GET /nft/list/?order_by={sort}&limit={n}&offset={n}
   */
  async fetchAllListings(): Promise<number> {
    console.log('[MajorAdapter] Fetching all listings from Major.tg...');

    let totalListings = 0;
    let offset = 0;
    const limit = 100;

    while (true) {
      try {
        const response = await this.api.get('/nft/list/', {
          params: {
            order_by: 'price_asc',
            limit,
            offset,
          },
        });

        const { results, next } = response.data;

        if (!results || results.length === 0) break;

        // Обработка каждого NFT
        for (const item of results) {
          await this.processListing(item);
          totalListings++;
        }

        console.log(`[MajorAdapter] Processed ${totalListings} listings...`);

        // Проверяем есть ли еще данные
        if (!next) break;
        offset += limit;

        // Rate limiting (вежливость)
        await this.sleep(500);
      } catch (error: any) {
        console.error(`[MajorAdapter] Error at offset ${offset}:`, error.message);
        break;
      }
    }

    console.log(`[MajorAdapter] ✅ Total listings indexed: ${totalListings}`);
    return totalListings;
  }

  /**
   * Получить listings для конкретной коллекции
   */
  async fetchCollectionListings(collectionAddress: string): Promise<number> {
    console.log(`[MajorAdapter] Fetching listings for collection: ${collectionAddress}`);

    let totalListings = 0;
    let offset = 0;
    const limit = 100;

    while (true) {
      try {
        const response = await this.api.get('/nft/list/', {
          params: {
            collection: collectionAddress,
            order_by: 'price_asc',
            limit,
            offset,
          },
        });

        const { results, next } = response.data;

        if (!results || results.length === 0) break;

        for (const item of results) {
          await this.processListing(item);
          totalListings++;
        }

        if (!next) break;
        offset += limit;

        await this.sleep(500);
      } catch (error: any) {
        console.error(`[MajorAdapter] Error at offset ${offset}:`, error.message);
        break;
      }
    }

    console.log(`[MajorAdapter] ✅ Collection listings indexed: ${totalListings}`);
    return totalListings;
  }

  /**
   * Обработка одного NFT listing
   */
  private async processListing(item: any): Promise<void> {
    try {
      // Парсим данные из Major.tg формата
      const nftAddress = item.address || item.nft_address;
      const price = this.parsePrice(item.price);
      const market = this.parseMarket(item.market_type);
      const seller = item.seller || item.owner?.address;

      if (!nftAddress || !price || !seller) {
        console.warn('[MajorAdapter] Skipping invalid listing:', item);
        return;
      }

      // Сохраняем в БД
      await DB.upsertListing({
        nft_address: nftAddress,
        market: market || 'major',
        price: price.toString(),
        seller: seller,
        listing_url: this.buildListingURL(nftAddress, market),
        sale_contract_address: item.sale_contract || null,
      });
    } catch (error: any) {
      console.error('[MajorAdapter] Error processing listing:', error.message);
    }
  }

  /**
   * Парсинг цены из разных форматов
   */
  private parsePrice(priceData: any): number | null {
    if (typeof priceData === 'number') {
      // Если уже в TON
      return priceData;
    }

    if (typeof priceData === 'string') {
      return parseFloat(priceData);
    }

    if (priceData?.value) {
      // Если в nanotons
      return parseInt(priceData.value) / 1e9;
    }

    return null;
  }

  /**
   * Определение маркета из market_type
   */
  private parseMarket(marketType: string): string {
    if (!marketType) return 'major';

    const normalized = marketType.toLowerCase();

    if (normalized.includes('fragment')) return 'fragment';
    if (normalized.includes('getgems') || normalized.includes('gems')) return 'getgems';
    if (normalized.includes('diamonds')) return 'ton.diamonds';

    return 'major';
  }

  /**
   * Построение URL на listing
   */
  private buildListingURL(nftAddress: string, market: string | null): string {
    // Major.tg не имеет прямых ссылок на NFT, перенаправляем на реальный маркет
    switch (market) {
      case 'getgems':
        return `https://getgems.io/nft/${nftAddress}`;
      case 'fragment':
        return `https://fragment.com/nft/${nftAddress}`;
      case 'ton.diamonds':
        return `https://ton.diamonds/nft/${nftAddress}`;
      default:
        return `https://major.tg/marketplace`;
    }
  }

  /**
   * Получить статистику Major.tg
   */
  async getMarketStats(): Promise<{
    total_listings: number;
    markets: Record<string, number>;
  }> {
    console.log('[MajorAdapter] Fetching market stats...');

    try {
      const response = await this.api.get('/nft/list/', {
        params: { limit: 1 },
      });

      const { count } = response.data;

      // Подсчёт по маркетам (можно улучшить с API endpoints если есть)
      const markets: Record<string, number> = {};

      return {
        total_listings: count || 0,
        markets,
      };
    } catch (error: any) {
      console.error('[MajorAdapter] Error fetching stats:', error.message);
      return { total_listings: 0, markets: {} };
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
