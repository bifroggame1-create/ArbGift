"""
Initial database schema for TON Gift Aggregator

Revision ID: 001_initial
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # MARKETS - Marketplace registry
    # ============================================================
    op.create_table(
        'markets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('slug', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('website_url', sa.String(255)),
        sa.Column('api_base_url', sa.String(255)),
        sa.Column('fee_buy_percent', sa.Numeric(5, 2), default=0),
        sa.Column('fee_sell_percent', sa.Numeric(5, 2), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('priority', sa.Integer(), default=0),  # For sorting
        sa.Column('config', postgresql.JSONB(), default={}),  # Adapter-specific config
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # ============================================================
    # COLLECTIONS - NFT Collections
    # ============================================================
    op.create_table(
        'collections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('address', sa.String(66), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, index=True),
        sa.Column('description', sa.Text()),
        sa.Column('image_url', sa.String(500)),
        sa.Column('cover_url', sa.String(500)),
        sa.Column('external_url', sa.String(500)),

        # Stats (updated by workers)
        sa.Column('total_items', sa.Integer(), default=0),
        sa.Column('owners_count', sa.Integer(), default=0),
        sa.Column('floor_price_ton', sa.Numeric(18, 9)),
        sa.Column('total_volume_ton', sa.Numeric(18, 9), default=0),
        sa.Column('volume_24h_ton', sa.Numeric(18, 9), default=0),

        # Metadata
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('is_telegram_gift', sa.Boolean(), default=False),
        sa.Column('raw_metadata', postgresql.JSONB()),

        # Indexing state
        sa.Column('last_indexed_at', sa.DateTime(timezone=True)),
        sa.Column('indexing_status', sa.String(20), default='pending'),  # pending, indexing, completed, failed

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Index for Telegram Gifts collections
    op.create_index('idx_collections_telegram_gift', 'collections', ['is_telegram_gift'])

    # ============================================================
    # NFTS - Individual NFT items
    # ============================================================
    op.create_table(
        'nfts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('address', sa.String(66), unique=True, nullable=False, index=True),
        sa.Column('collection_id', sa.Integer(), sa.ForeignKey('collections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('index', sa.Integer()),  # Index within collection

        # Basic info from metadata
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('description', sa.Text()),

        # Media (resolved URLs)
        sa.Column('image_url', sa.String(500)),
        sa.Column('image_cdn_url', sa.String(500)),  # Our CDN copy
        sa.Column('animation_url', sa.String(500)),
        sa.Column('animation_cdn_url', sa.String(500)),

        # Attributes (denormalized for search)
        sa.Column('rarity', sa.String(50), index=True),
        sa.Column('backdrop', sa.String(100)),
        sa.Column('model', sa.String(100)),
        sa.Column('symbol', sa.String(100)),
        sa.Column('pattern', sa.String(100)),

        # Full attributes array
        sa.Column('attributes', postgresql.JSONB(), default=[]),

        # Owner info
        sa.Column('owner_address', sa.String(66), index=True),

        # Sale status (denormalized for fast queries)
        sa.Column('is_on_sale', sa.Boolean(), default=False, index=True),
        sa.Column('lowest_price_ton', sa.Numeric(18, 9)),
        sa.Column('lowest_price_market', sa.String(50)),

        # Raw data
        sa.Column('raw_metadata', postgresql.JSONB()),
        sa.Column('metadata_url', sa.String(500)),
        sa.Column('metadata_resolved_at', sa.DateTime(timezone=True)),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Composite indexes for common queries
    op.create_index('idx_nfts_collection_sale', 'nfts', ['collection_id', 'is_on_sale'])
    op.create_index('idx_nfts_collection_rarity', 'nfts', ['collection_id', 'rarity'])
    op.create_index('idx_nfts_price', 'nfts', ['lowest_price_ton'], postgresql_where=sa.text('is_on_sale = true'))

    # Full-text search index
    op.execute("""
        CREATE INDEX idx_nfts_fts ON nfts
        USING gin(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '')))
    """)

    # ============================================================
    # LISTINGS - Active sale listings across markets
    # ============================================================
    op.create_table(
        'listings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nft_id', sa.Integer(), sa.ForeignKey('nfts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('market_id', sa.Integer(), sa.ForeignKey('markets.id', ondelete='CASCADE'), nullable=False),

        # Market-specific ID
        sa.Column('market_listing_id', sa.String(200), nullable=False),

        # Pricing
        sa.Column('price_raw', sa.Numeric(24, 9), nullable=False),  # Original price
        sa.Column('currency', sa.String(20), nullable=False, default='TON'),  # TON, STARS, USDT
        sa.Column('price_ton', sa.Numeric(18, 9), nullable=False, index=True),  # Normalized to TON

        # Seller
        sa.Column('seller_address', sa.String(66)),

        # URLs
        sa.Column('listing_url', sa.String(500)),

        # Status
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('listed_at', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),

        # Sync tracking
        sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), server_default=sa.func.now()),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Unique constraint: one listing per NFT per market
    op.create_unique_constraint(
        'uq_listings_market_nft',
        'listings',
        ['market_id', 'market_listing_id']
    )

    # Index for finding best prices
    op.create_index(
        'idx_listings_nft_price_active',
        'listings',
        ['nft_id', 'price_ton'],
        postgresql_where=sa.text('is_active = true')
    )

    # Index for market sync
    op.create_index('idx_listings_market_active', 'listings', ['market_id', 'is_active'])

    # ============================================================
    # SALES - Completed sales history
    # ============================================================
    op.create_table(
        'sales',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nft_id', sa.Integer(), sa.ForeignKey('nfts.id', ondelete='SET NULL')),
        sa.Column('collection_id', sa.Integer(), sa.ForeignKey('collections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('market_id', sa.Integer(), sa.ForeignKey('markets.id', ondelete='SET NULL')),

        # NFT snapshot (in case NFT is deleted)
        sa.Column('nft_address', sa.String(66), nullable=False, index=True),
        sa.Column('nft_name', sa.String(300)),

        # Pricing
        sa.Column('price_raw', sa.Numeric(24, 9), nullable=False),
        sa.Column('currency', sa.String(20), nullable=False),
        sa.Column('price_ton', sa.Numeric(18, 9), nullable=False, index=True),

        # Parties
        sa.Column('buyer_address', sa.String(66)),
        sa.Column('seller_address', sa.String(66)),

        # Transaction
        sa.Column('tx_hash', sa.String(66), unique=True, index=True),
        sa.Column('tx_lt', sa.BigInteger()),  # Logical time

        sa.Column('sold_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Index for volume calculations
    op.create_index('idx_sales_collection_time', 'sales', ['collection_id', 'sold_at'])

    # ============================================================
    # PRICE_HISTORY - Price tracking for charts
    # ============================================================
    op.create_table(
        'price_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nft_id', sa.Integer(), sa.ForeignKey('nfts.id', ondelete='CASCADE')),
        sa.Column('collection_id', sa.Integer(), sa.ForeignKey('collections.id', ondelete='CASCADE')),

        sa.Column('price_ton', sa.Numeric(18, 9), nullable=False),
        sa.Column('market_id', sa.Integer(), sa.ForeignKey('markets.id', ondelete='SET NULL')),

        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )

    # Partition by time for efficient queries (optional, for scale)
    op.create_index('idx_price_history_nft_time', 'price_history', ['nft_id', 'recorded_at'])

    # ============================================================
    # FX_RATES - Currency exchange rates
    # ============================================================
    op.create_table(
        'fx_rates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('from_currency', sa.String(20), nullable=False),
        sa.Column('to_currency', sa.String(20), nullable=False),
        sa.Column('rate', sa.Numeric(18, 9), nullable=False),
        sa.Column('source', sa.String(50)),  # coingecko, binance, etc
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_unique_constraint('uq_fx_rates_pair', 'fx_rates', ['from_currency', 'to_currency'])


def downgrade() -> None:
    op.drop_table('fx_rates')
    op.drop_table('price_history')
    op.drop_table('sales')
    op.drop_table('listings')
    op.drop_table('nfts')
    op.drop_table('collections')
    op.drop_table('markets')
