import axios, { AxiosInstance } from 'axios';
import { CONFIG } from '../../config';
import { DB } from '../../db';
import { MetadataResolver } from './MetadataResolver';

/**
 * TON API Response Types (tonapi.io/v2)
 */
interface TonApiNFTItem {
  address: string;
  index: number;
  owner: {
    address: string;
    is_scam: boolean;
  };
  collection?: {
    address: string;
    name: string;
    description?: string;
  };
  verified: boolean;
  metadata: {
    name?: string;
    description?: string;
    image?: string;
    attributes?: Array<{
      trait_type: string;
      value: string;
    }>;
  };
  previews?: Array<{
    resolution: string;
    url: string;
  }>;
  sale?: {
    address: string;
    market: {
      name: string;
      address: string;
    };
    owner: {
      address: string;
    };
    price: {
      token_name: string;
      value: string; // in nanotons
    };
  };
}

interface TonApiCollectionItems {
  nft_items: TonApiNFTItem[];
  next_from?: number;
}

/**
 * NFTIndexer - индексирует NFT коллекции через TON API
 *
 * Использует tonapi.io для получения:
 * 1. Всех NFT в коллекции
 * 2. Владельцев
 * 3. Metadata
 * 4. Активных sale (GetGems, Fragment, etc)
 */
export class NFTIndexer {
  private api: AxiosInstance;
  private metadataResolver: MetadataResolver;

  constructor() {
    this.api = axios.create({
      baseURL: CONFIG.TONAPI_BASE_URL,
      headers: CONFIG.TONAPI_KEY
        ? { Authorization: `Bearer ${CONFIG.TONAPI_KEY}` }
        : {},
      timeout: 15000,
    });

    this.metadataResolver = new MetadataResolver();
  }

  /**
   * Индексировать всю коллекцию
   */
  async indexCollection(collectionAddress: string): Promise<void> {
    console.log(`[NFTIndexer] Indexing collection: ${collectionAddress}`);

    let indexed = 0;
    let offset = 0;
    const limit = 1000; // tonapi.io максимум 1000 за запрос

    // Получаем коллекцию и сохраняем в БД
    const collectionData = await this.fetchCollectionInfo(collectionAddress);
    const collection = await DB.upsertCollection({
      address: collectionAddress,
      name: collectionData.name,
      description: collectionData.description,
      image_url: collectionData.image,
    });

    console.log(`[NFTIndexer] Collection: ${collection.name || collectionAddress}`);

    // Постраничная загрузка всех NFT
    while (true) {
      try {
        const response = await this.api.get<TonApiCollectionItems>(
          `/nfts/collections/${collectionAddress}/items`,
          { params: { limit, offset } }
        );

        const { nft_items, next_from } = response.data;

        if (!nft_items || nft_items.length === 0) break;

        // Обрабатываем батч NFT
        await this.processNFTBatch(nft_items, collection.id);

        indexed += nft_items.length;
        console.log(`[NFTIndexer] Indexed ${indexed} NFTs...`);

        // Проверяем есть ли еще страницы
        if (!next_from) break;
        offset = next_from;

        // Rate limiting (tonapi.io free tier = 1 req/sec)
        await this.sleep(1100);
      } catch (error: any) {
        console.error(`[NFTIndexer] Error fetching NFTs at offset ${offset}:`, error.message);
        break;
      }
    }

    // Обновляем total_supply
    await DB.query(
      `UPDATE collections SET total_supply = $1 WHERE id = $2`,
      [indexed, collection.id]
    );

    console.log(`[NFTIndexer] ✅ Indexed ${indexed} NFTs from collection ${collection.name}`);
  }

  /**
   * Обработать батч NFT (вставка в БД + resolve metadata)
   */
  private async processNFTBatch(nfts: TonApiNFTItem[], collectionId: number): Promise<void> {
    for (const nft of nfts) {
      try {
        // Resolve IPFS image → HTTP URL
        let imageUrl = nft.metadata.image;
        if (imageUrl && imageUrl.startsWith('ipfs://')) {
          imageUrl = await this.metadataResolver.resolveIPFS(imageUrl);
        }

        // Превью (если есть)
        const preview = nft.previews?.find((p) => p.resolution === '500x500')?.url;

        // Сохраняем NFT в БД
        await DB.upsertNFT({
          address: nft.address,
          collection_id: collectionId,
          token_id: String(nft.index),
          owner: nft.owner.address,
          name: nft.metadata.name,
          description: nft.metadata.description,
          image_url: imageUrl,
          content_uri: nft.metadata.image, // оригинальный URI
          metadata: {
            attributes: nft.metadata.attributes || [],
            verified: nft.verified,
          },
        });

        // Если есть активная продажа — сохраняем listing
        if (nft.sale) {
          const priceInTON = (parseInt(nft.sale.price.value) / 1e9).toFixed(9);

          await DB.upsertListing({
            nft_address: nft.address,
            market: nft.sale.market.name.toLowerCase(), // 'getgems', 'fragment', etc
            price: priceInTON,
            seller: nft.sale.owner.address,
            sale_contract_address: nft.sale.address,
            listing_url: this.buildMarketplaceURL(nft.sale.market.name, nft.address),
          });
        }
      } catch (error: any) {
        console.error(`[NFTIndexer] Error processing NFT ${nft.address}:`, error.message);
      }
    }
  }

  /**
   * Получить информацию о коллекции
   */
  private async fetchCollectionInfo(address: string) {
    try {
      const response = await this.api.get(`/nfts/collections/${address}`);
      return {
        name: response.data.metadata?.name || 'Unknown Collection',
        description: response.data.metadata?.description,
        image: response.data.metadata?.image,
      };
    } catch (error) {
      console.warn(`[NFTIndexer] Could not fetch collection info for ${address}`);
      return { name: 'Unknown Collection', description: null, image: null };
    }
  }

  /**
   * Построить URL маркетплейса
   */
  private buildMarketplaceURL(market: string, nftAddress: string): string {
    const marketLower = market.toLowerCase();
    switch (marketLower) {
      case 'getgems':
        return `https://getgems.io/nft/${nftAddress}`;
      case 'fragment':
        return `https://fragment.com/nft/${nftAddress}`;
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
