// Быстрая индексация через Major.tg API
const { Client } = require('pg');
const axios = require('axios');

async function quickIndex() {
  const client = new Client({
    connectionString: 'postgresql://postgres:postgres@localhost:5432/nft_indexer'
  });

  await client.connect();
  console.log('✅ Connected to database');

  // Create collection first
  await client.query(`
    INSERT INTO collections (id, address, name, description)
    VALUES (1, 'MAJOR_AGGREGATED', 'Major.tg Aggregated Gifts', 'Gifts aggregated from Major.tg marketplace')
    ON CONFLICT (id) DO NOTHING
  `);
  console.log('✅ Collection created');

  // Fetch from Major.tg
  const response = await axios.get('https://major.tg/api/v1/nft/list/?order_by=price_asc&limit=50');
  const items = response.data.items;

  console.log(`📦 Fetched ${items.length} NFTs from Major.tg`);

  for (const item of items) {
    // Insert NFT
    await client.query(`
      INSERT INTO nfts (address, name, description, image_url, collection_id, owner)
      VALUES ($1, $2, $3, $4, 1, $5)
      ON CONFLICT (address) DO NOTHING
    `, [
      item.address,
      item.name,
      item.description,
      item.image,
      item.owner
    ]);

    // Insert listing
    const price = (item.min_bid || item.max_bid || 0).toFixed(2);
    await client.query(`
      INSERT INTO listings (nft_address, market, price, seller, listing_url, sale_contract_address, is_active, indexed_at)
      VALUES ($1, $2, $3, $4, $5, $6, true, NOW())
      ON CONFLICT (nft_address, market, sale_contract_address) DO UPDATE
      SET price = $3, is_active = true, indexed_at = NOW()
    `, [
      item.address,
      item.market_type || 'major',
      price,
      item.owner,
      `https://major.tg/nft/${item.slug}`,
      item.address // Use NFT address as sale contract placeholder
    ]);
  }

  console.log('✅ Indexed all NFTs to database');
  await client.end();
}

quickIndex().catch(console.error);
