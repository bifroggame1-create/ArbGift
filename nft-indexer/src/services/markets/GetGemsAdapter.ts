import axios, { AxiosInstance } from 'axios';
import { CONFIG } from '../../config';
import { DB } from '../../db';

/**
 * GetGems GraphQL Response Types
 */
interface GetGemsNFTSale {
  nft: {
    address: string;
    name: string;
    owner: {
      address: string;
    };
    collection?: {
      address: string;
      name: string;
    };
    sale?: {
      fullPrice: string; // в nanotons
      seller: {
        address: string;
      };
      saleContract: string;
    };
  };
}

interface GetGemsCollectionSales {
  data: {
    alphaNftItemsByCollection: {
      items: GetGemsNFTSale[];
    };
  };
}

/**
 * GetGemsAdapter - адаптер для маркетплейса GetGems
 *
 * Методы:
 * 1. GraphQL API для получения listings
 * 2. TON API (tonapi.io) уже включает GetGems sales — используем как fallback
 */
export class GetGemsAdapter {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: CONFIG.GETGEMS_GRAPHQL_URL,
      timeout: 15000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Получить все активные listings для коллекции через GraphQL
   *
   * ВАЖНО: GetGems GraphQL может требовать авторизацию или rate-limit.
   * В production лучше использовать tonapi.io который уже парсит GetGems.
   */
  async fetchCollectionListings(collectionAddress: string): Promise<void> {
    console.log(`[GetGemsAdapter] Fetching listings for collection: ${collectionAddress}`);

    try {
      const query = `
        query GetCollectionSales($collectionAddress: String!) {
          alphaNftItemsByCollection(
            address: $collectionAddress
            saleType: ON_SALE
            first: 1000
          ) {
            items {
              nft {
                address
                name
                owner {
                  address
                }
                sale {
                  fullPrice
                  seller {
                    address
                  }
                  saleContract
                }
              }
            }
          }
        }
      `;

      const response = await this.api.post<GetGemsCollectionSales>('', {
        query,
        variables: { collectionAddress },
      });

      const items = response.data?.data?.alphaNftItemsByCollection?.items || [];

      console.log(`[GetGemsAdapter] Found ${items.length} listings on GetGems`);

      // Сохраняем в БД
      for (const item of items) {
        if (!item.nft.sale) continue;

        const priceInTON = (parseInt(item.nft.sale.fullPrice) / 1e9).toFixed(9);

        await DB.upsertListing({
          nft_address: item.nft.address,
          market: 'getgems',
          price: priceInTON,
          seller: item.nft.sale.seller.address,
          sale_contract_address: item.nft.sale.saleContract,
          listing_url: `https://getgems.io/nft/${item.nft.address}`,
        });
      }

      console.log(`[GetGemsAdapter] ✅ Saved ${items.length} GetGems listings`);
    } catch (error: any) {
      console.error(`[GetGemsAdapter] Error fetching GetGems listings:`, error.message);

      // Fallback: используем tonapi.io (уже включает GetGems sales)
      console.log('[GetGemsAdapter] Falling back to TON API for GetGems data');
      await this.fetchListingsViaTonAPI(collectionAddress);
    }
  }

  /**
   * Fallback: получить GetGems listings через TON API
   * tonapi.io парсит GetGems sale contracts и возвращает их в nft.sale
   */
  private async fetchListingsViaTonAPI(collectionAddress: string): Promise<void> {
    try {
      const tonapi = axios.create({
        baseURL: CONFIG.TONAPI_BASE_URL,
        headers: CONFIG.TONAPI_KEY
          ? { Authorization: `Bearer ${CONFIG.TONAPI_KEY}` }
          : {},
      });

      let offset = 0;
      const limit = 1000;

      while (true) {
        const response = await tonapi.get(`/nfts/collections/${collectionAddress}/items`, {
          params: { limit, offset },
        });

        const { nft_items, next_from } = response.data;

        if (!nft_items || nft_items.length === 0) break;

        // Фильтруем только те, у которых есть sale на GetGems
        for (const nft of nft_items) {
          if (nft.sale && nft.sale.market.name.toLowerCase() === 'getgems') {
            const priceInTON = (parseInt(nft.sale.price.value) / 1e9).toFixed(9);

            await DB.upsertListing({
              nft_address: nft.address,
              market: 'getgems',
              price: priceInTON,
              seller: nft.sale.owner.address,
              sale_contract_address: nft.sale.address,
              listing_url: `https://getgems.io/nft/${nft.address}`,
            });
          }
        }

        if (!next_from) break;
        offset = next_from;

        // Rate limiting
        await new Promise((r) => setTimeout(r, 1100));
      }

      console.log('[GetGemsAdapter] ✅ Fetched GetGems listings via TON API');
    } catch (error: any) {
      console.error(`[GetGemsAdapter] TON API fallback failed:`, error.message);
    }
  }

  /**
   * Деактивировать старые listings которых больше нет на GetGems
   */
  async deactivateStaleListings(activeNFTAddresses: Set<string>): Promise<void> {
    const allListings = await DB.query<{ nft_address: string }>(
      `SELECT nft_address FROM listings WHERE market = 'getgems' AND is_active = true`
    );

    for (const listing of allListings) {
      if (!activeNFTAddresses.has(listing.nft_address)) {
        await DB.deactivateListings(listing.nft_address, 'getgems');
      }
    }
  }
}
