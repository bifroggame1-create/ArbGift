"""Add user, referral, quest, leaderboard models

Revision ID: 002_add_user_social
Revises: 001_initial
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002_add_user_social'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # USERS - Main user table
    # ============================================================
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),

        # Telegram integration
        sa.Column('telegram_id', sa.BigInteger(), unique=True, nullable=False, index=True),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('first_name', sa.String(255), nullable=True),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('language_code', sa.String(10), nullable=True),
        sa.Column('is_premium', sa.Boolean(), default=False),

        # TON Connect wallet
        sa.Column('wallet_address', sa.String(66), unique=True, nullable=True, index=True),
        sa.Column('wallet_connected_at', sa.DateTime(timezone=True), nullable=True),

        # Balances
        sa.Column('balance_ton', sa.Numeric(18, 9), default=0),
        sa.Column('balance_stars', sa.Integer(), default=0),

        # Referral system
        sa.Column('referral_code', sa.String(20), unique=True, nullable=False, index=True),
        sa.Column('referred_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('referral_earnings_ton', sa.Numeric(18, 9), default=0),
        sa.Column('referrals_count', sa.Integer(), default=0),

        # Gamification
        sa.Column('level', sa.Integer(), default=1),
        sa.Column('xp', sa.Integer(), default=0),
        sa.Column('badges_earned', postgresql.JSONB(), default=[]),

        # Game stats
        sa.Column('games_played', sa.Integer(), default=0),
        sa.Column('games_won', sa.Integer(), default=0),
        sa.Column('current_win_streak', sa.Integer(), default=0),
        sa.Column('best_win_streak', sa.Integer(), default=0),
        sa.Column('total_wagered_ton', sa.Numeric(18, 9), default=0),
        sa.Column('total_won_ton', sa.Numeric(18, 9), default=0),
        sa.Column('total_lost_ton', sa.Numeric(18, 9), default=0),
        sa.Column('biggest_win_ton', sa.Numeric(18, 9), default=0),

        # Staking stats
        sa.Column('total_staked_value_ton', sa.Numeric(18, 9), default=0),
        sa.Column('active_stakes_count', sa.Integer(), default=0),
        sa.Column('total_staking_rewards_ton', sa.Numeric(18, 9), default=0),

        # Status
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_banned', sa.Boolean(), default=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ============================================================
    # REFERRALS - Referral relationships
    # ============================================================
    op.create_table(
        'referrals',
        sa.Column('id', sa.Integer(), primary_key=True),

        # Relationships
        sa.Column('referrer_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('referred_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),

        # Commission
        sa.Column('commission_percent', sa.Numeric(5, 2), default=5.0),

        # Stats
        sa.Column('total_earned_ton', sa.Numeric(18, 9), default=0),
        sa.Column('total_commission_paid_ton', sa.Numeric(18, 9), default=0),
        sa.Column('referral_activities_count', sa.Integer(), default=0),

        # Activity
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index('ix_referral_referrer_referred', 'referrals', ['referrer_id', 'referred_id'], unique=True)

    # ============================================================
    # REFERRAL_REWARDS - Reward payment history
    # ============================================================
    op.create_table(
        'referral_rewards',
        sa.Column('id', sa.Integer(), primary_key=True),

        # Relationships
        sa.Column('referral_id', sa.Integer(), sa.ForeignKey('referrals.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('recipient_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),

        # Reward details
        sa.Column('amount_ton', sa.Numeric(18, 9), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),  # stake, game_win, deposit
        sa.Column('source_amount_ton', sa.Numeric(18, 9), nullable=False),

        # Timestamp
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index('ix_reward_recipient_created', 'referral_rewards', ['recipient_id', 'created_at'])

    # ============================================================
    # QUESTS - Quest templates
    # ============================================================
    op.create_table(
        'quests',
        sa.Column('id', sa.Integer(), primary_key=True),

        # Quest identification
        sa.Column('quest_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('type', sa.Enum('DAILY', 'WEEKLY', 'ACHIEVEMENT', name='questtype'), nullable=False, index=True),

        # Details
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(100), nullable=True),

        # Requirements
        sa.Column('target_action', sa.String(100), nullable=False),
        sa.Column('target_count', sa.Integer(), default=1),
        sa.Column('requirements', postgresql.JSONB(), default={}),

        # Rewards
        sa.Column('reward_ton', sa.Numeric(18, 9), default=0),
        sa.Column('reward_stars', sa.Integer(), default=0),
        sa.Column('reward_xp', sa.Integer(), default=0),
        sa.Column('reward_items', postgresql.JSONB(), default=[]),

        # Availability
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reset_period', sa.String(20), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ============================================================
    # USER_QUESTS - User quest progress
    # ============================================================
    op.create_table(
        'user_quests',
        sa.Column('id', sa.Integer(), primary_key=True),

        # Relationships
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('quest_id', sa.Integer(), sa.ForeignKey('quests.id', ondelete='CASCADE'), nullable=False, index=True),

        # Progress
        sa.Column('current_progress', sa.Integer(), default=0),
        sa.Column('target_progress', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'COMPLETED', 'CLAIMED', name='queststatus'), default='ACTIVE', index=True),

        # Dates
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reset_at', sa.DateTime(timezone=True), nullable=True),

        # Metadata
        sa.Column('metadata', postgresql.JSONB(), default={}),
    )

    op.create_index('ix_user_quests_user_status', 'user_quests', ['user_id', 'status'])
    op.create_unique_constraint('uq_user_quest_active', 'user_quests', ['user_id', 'quest_id'])

    # ============================================================
    # BADGES - Badge templates
    # ============================================================
    op.create_table(
        'badges',
        sa.Column('id', sa.Integer(), primary_key=True),

        # Badge identification
        sa.Column('badge_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),

        # Visual
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('rarity', sa.String(50), nullable=True, index=True),
        sa.Column('color', sa.String(20), nullable=True),

        # Requirements
        sa.Column('requirements', postgresql.JSONB(), default={}),

        # Metadata
        sa.Column('category', sa.String(50), nullable=True, index=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('display_order', sa.Integer(), default=0),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ============================================================
    # USER_BADGES - User earned badges
    # ============================================================
    op.create_table(
        'user_badges',
        sa.Column('id', sa.Integer(), primary_key=True),

        # Relationships
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('badge_id', sa.Integer(), sa.ForeignKey('badges.id', ondelete='CASCADE'), nullable=False, index=True),

        # Earning details
        sa.Column('earned_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('progress_snapshot', postgresql.JSONB(), default={}),
    )

    op.create_unique_constraint('uq_user_badge', 'user_badges', ['user_id', 'badge_id'])
    op.create_index('ix_user_badges_earned', 'user_badges', ['user_id', 'earned_at'])

    # ============================================================
    # LEADERBOARD_ENTRIES - Leaderboard rankings
    # ============================================================
    op.create_table(
        'leaderboard_entries',
        sa.Column('id', sa.Integer(), primary_key=True),

        # User info (denormalized for performance)
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(255), nullable=True),

        # Leaderboard type
        sa.Column('leaderboard_type', sa.Enum('ALL_TIME', 'WEEKLY', 'MONTHLY', 'DAILY', name='leaderboardtype'), nullable=False, index=True),
        sa.Column('category', sa.Enum('TOTAL_PROFIT', 'BIGGEST_WIN', 'WIN_STREAK', 'TOTAL_WAGERED', 'STAKING_REWARDS', 'REFERRAL_EARNINGS', name='leaderboardcategory'), nullable=False, index=True),

        # Position
        sa.Column('rank', sa.Integer(), nullable=False, index=True),
        sa.Column('previous_rank', sa.Integer(), nullable=True),

        # Value
        sa.Column('score_value', sa.Numeric(18, 9), nullable=False),

        # Period
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_index('ix_leaderboard_type_category_rank', 'leaderboard_entries', ['leaderboard_type', 'category', 'rank'])
    op.create_unique_constraint('uq_leaderboard_user_type_category', 'leaderboard_entries', ['user_id', 'leaderboard_type', 'category'])

    # ============================================================
    # GAME_HISTORY - Game history for statistics
    # ============================================================
    op.create_table(
        'game_history',
        sa.Column('id', sa.Integer(), primary_key=True),

        # User
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),

        # Game
        sa.Column('game_type', sa.String(50), nullable=False, index=True),
        sa.Column('game_id', sa.String(100), nullable=True),

        # Bet
        sa.Column('bet_amount_ton', sa.Numeric(18, 9), nullable=False),
        sa.Column('bet_currency', sa.String(20), default='TON'),

        # Payout
        sa.Column('payout_amount_ton', sa.Numeric(18, 9), default=0),
        sa.Column('multiplier', sa.Numeric(10, 2), default=0),
        sa.Column('profit_ton', sa.Numeric(18, 9), nullable=False),

        # Result
        sa.Column('is_win', sa.Boolean(), nullable=False),

        # Provably Fair
        sa.Column('server_seed_hash', sa.String(128), nullable=True),
        sa.Column('client_seed', sa.String(128), nullable=True),
        sa.Column('nonce', sa.Integer(), nullable=True),

        # Timestamp
        sa.Column('played_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )

    op.create_index('ix_game_history_user_played', 'game_history', ['user_id', 'played_at'])
    op.create_index('ix_game_history_type_played', 'game_history', ['game_type', 'played_at'])


def downgrade() -> None:
    op.drop_table('game_history')
    op.drop_table('leaderboard_entries')
    op.drop_table('user_badges')
    op.drop_table('badges')
    op.drop_table('user_quests')
    op.drop_table('quests')
    op.drop_table('referral_rewards')
    op.drop_table('referrals')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS leaderboardcategory')
    op.execute('DROP TYPE IF EXISTS leaderboardtype')
    op.execute('DROP TYPE IF EXISTS queststatus')
    op.execute('DROP TYPE IF EXISTS questtype')
