import axios, { AxiosInstance } from 'axios';
import { DB } from '../../db';

/**
 * PortalsAdapter - индексация через Portals.tg (portal-market.com API)
 *
 * Особенности:
 * - Требует Telegram Mini App (TMA) аутентификацию
 * - Endpoint: https://portal-market.com/api/
 * - Формат auth: WebAppInitData через header
 *
 * TMA Auth format:
 * {
 *   "initData": "query_id=AAH...&user=%7B%22id%22%3A12345...&auth_date=1234567890&hash=abc123..."
 * }
 */
export class PortalsAdapter {
  private api: AxiosInstance;
  private initData: string | null = null;

  constructor(initData?: string) {
    this.initData = initData || process.env.PORTALS_INIT_DATA || null;

    this.api = axios.create({
      baseURL: 'https://portal-market.com/api',
      timeout: 15000,
      headers: this.initData
        ? {
            'Content-Type': 'application/json',
            'X-Init-Data': this.initData,
          }
        : {},
    });
  }

  /**
   * Проверка аутентификации
   */
  async checkAuth(): Promise<boolean> {
    if (!this.initData) {
      console.warn('[PortalsAdapter] No initData provided, skipping Portals indexing');
      return false;
    }

    try {
      // Попытка запроса к API для проверки auth
      const response = await this.api.get('/user/me');
      console.log('[PortalsAdapter] ✅ Authentication successful');
      return true;
    } catch (error: any) {
      console.error('[PortalsAdapter] ❌ Authentication failed:', error.message);
      return false;
    }
  }

  /**
   * Получить все listings с Portals.tg
   *
   * Предполагаемый endpoint: GET /nft/list или /marketplace/listings
   * (точный endpoint нужно уточнить через reverse engineering)
   */
  async fetchAllListings(): Promise<number> {
    if (!(await this.checkAuth())) {
      return 0;
    }

    console.log('[PortalsAdapter] Fetching all listings from Portals.tg...');

    let totalListings = 0;
    let page = 1;
    const limit = 50;

    while (true) {
      try {
        // Попытка разных возможных endpoints
        const endpoints = [
          '/nft/list',
          '/marketplace/listings',
          '/gifts/list',
          '/api/nfts',
        ];

        let response = null;
        for (const endpoint of endpoints) {
          try {
            response = await this.api.get(endpoint, {
              params: { page, limit },
            });
            break;
          } catch (err) {
            continue;
          }
        }

        if (!response) {
          console.warn('[PortalsAdapter] No valid endpoint found');
          break;
        }

        const data = response.data;
        const items = data.results || data.items || data.listings || data.data || [];

        if (items.length === 0) break;

        for (const item of items) {
          await this.processListing(item);
          totalListings++;
        }

        console.log(`[PortalsAdapter] Processed ${totalListings} listings...`);

        // Проверка на последнюю страницу
        if (!data.next && items.length < limit) break;

        page++;
        await this.sleep(1000);
      } catch (error: any) {
        console.error(`[PortalsAdapter] Error at page ${page}:`, error.message);
        break;
      }
    }

    console.log(`[PortalsAdapter] ✅ Total listings indexed: ${totalListings}`);
    return totalListings;
  }

  /**
   * Получить listings для конкретной коллекции
   */
  async fetchCollectionListings(collectionAddress: string): Promise<number> {
    if (!(await this.checkAuth())) {
      return 0;
    }

    console.log(`[PortalsAdapter] Fetching listings for collection: ${collectionAddress}`);

    let totalListings = 0;

    try {
      const response = await this.api.get('/nft/list', {
        params: {
          collection: collectionAddress,
        },
      });

      const items = response.data.results || response.data.items || [];

      for (const item of items) {
        await this.processListing(item);
        totalListings++;
      }
    } catch (error: any) {
      console.error('[PortalsAdapter] Error fetching collection:', error.message);
    }

    console.log(`[PortalsAdapter] ✅ Collection listings indexed: ${totalListings}`);
    return totalListings;
  }

  /**
   * Обработка одного NFT listing
   */
  private async processListing(item: any): Promise<void> {
    try {
      const nftAddress = item.address || item.nft_address || item.nft?.address;
      const price = this.parsePrice(item.price || item.price_ton);
      const seller = item.seller || item.owner || item.seller_address;

      if (!nftAddress || !price || !seller) {
        console.warn('[PortalsAdapter] Skipping invalid listing:', item);
        return;
      }

      await DB.upsertListing({
        nft_address: nftAddress,
        market: 'portals',
        price: price.toString(),
        seller: seller,
        listing_url: `https://portals.tg/nft/${nftAddress}`,
        sale_contract_address: item.sale_contract || null,
      });
    } catch (error: any) {
      console.error('[PortalsAdapter] Error processing listing:', error.message);
    }
  }

  /**
   * Парсинг цены
   */
  private parsePrice(priceData: any): number | null {
    if (typeof priceData === 'number') {
      return priceData;
    }

    if (typeof priceData === 'string') {
      return parseFloat(priceData);
    }

    if (priceData?.value) {
      return parseInt(priceData.value) / 1e9;
    }

    return null;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Установить TMA initData для аутентификации
   */
  setInitData(initData: string): void {
    this.initData = initData;
    this.api.defaults.headers['X-Init-Data'] = initData;
  }
}

/**
 * ВАЖНО: Для использования PortalsAdapter нужно:
 *
 * 1. Получить Telegram WebApp initData:
 *    - Открыть Portals.tg как Telegram Mini App
 *    - В DevTools перехватить network request с заголовком Authorization
 *    - Скопировать значение WebAppInitData
 *
 * 2. Добавить в .env:
 *    PORTALS_INIT_DATA=query_id=AAH...&user=%7B%22id%22...&hash=abc123...
 *
 * 3. Использование:
 *    const adapter = new PortalsAdapter(process.env.PORTALS_INIT_DATA);
 *    await adapter.fetchAllListings();
 *
 * Альтернатива: Использовать Playwright для автоматической аутентификации через Telegram
 */
