import axios from 'axios';
import { CONFIG } from '../../config';
import { DB } from '../../db';

/**
 * MetadataResolver - резолвит IPFS URIs в HTTP URLs и кеширует metadata
 *
 * Функции:
 * 1. IPFS → HTTP через публичные gateway (с fallback)
 * 2. Кеширование metadata в PostgreSQL
 * 3. Парсинг JSON metadata
 */
export class MetadataResolver {
  /**
   * Resolve IPFS URI → HTTP URL
   * Пример: ipfs://QmXxxx → https://cloudflare-ipfs.com/ipfs/QmXxxx
   */
  async resolveIPFS(uri: string): Promise<string> {
    if (!uri.startsWith('ipfs://')) {
      return uri; // уже HTTP
    }

    // Извлекаем CID из ipfs://CID
    const cid = uri.replace('ipfs://', '');

    // Пробуем gateway в порядке приоритета
    for (const gateway of CONFIG.IPFS_GATEWAYS) {
      const httpUrl = `${gateway}/${cid}`;

      try {
        // Проверяем доступность (HEAD запрос)
        await axios.head(httpUrl, { timeout: 3000 });
        return httpUrl;
      } catch (error) {
        console.warn(`[MetadataResolver] Gateway failed: ${gateway}`);
        continue;
      }
    }

    // Fallback: первый gateway (даже если недоступен)
    return `${CONFIG.IPFS_GATEWAYS[0]}/${cid}`;
  }

  /**
   * Fetch и parse metadata JSON
   * С кешированием в БД
   */
  async fetchMetadata(uri: string): Promise<Record<string, any> | null> {
    // Проверяем кеш в БД
    const cached = await DB.queryOne<{ content: Record<string, any> }>(
      `SELECT content FROM metadata_cache WHERE uri = $1`,
      [uri]
    );

    if (cached) {
      return cached.content;
    }

    // Resolve IPFS if needed
    const httpUrl = await this.resolveIPFS(uri);

    try {
      const response = await axios.get(httpUrl, {
        timeout: 10000,
        headers: { Accept: 'application/json' },
      });

      const metadata = response.data;

      // Сохраняем в кеш
      await DB.query(
        `INSERT INTO metadata_cache (uri, content, cached_at)
         VALUES ($1, $2, NOW())
         ON CONFLICT (uri) DO UPDATE SET content = $2, cached_at = NOW()`,
        [uri, JSON.stringify(metadata)]
      );

      return metadata;
    } catch (error: any) {
      console.error(`[MetadataResolver] Failed to fetch metadata from ${httpUrl}:`, error.message);
      return null;
    }
  }

  /**
   * Batch resolve IPFS URIs
   * Полезно для превью изображений
   */
  async resolveIPFSBatch(uris: string[]): Promise<Map<string, string>> {
    const results = new Map<string, string>();

    await Promise.all(
      uris.map(async (uri) => {
        const resolved = await this.resolveIPFS(uri);
        results.set(uri, resolved);
      })
    );

    return results;
  }
}
