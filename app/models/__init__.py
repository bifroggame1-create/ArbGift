"""
SQLAlchemy ORM models for TON Gift Aggregator.
"""
from app.models.collection import Collection
from app.models.nft import NFT
from app.models.listing import Listing
from app.models.market import Market
from app.models.sale import Sale
from app.models.user import User
from app.models.referral import Referral, ReferralReward, ReferralTier
from app.models.quest import Quest, UserQuest, Badge, UserBadge, QuestType, QuestStatus
from app.models.leaderboard import LeaderboardEntry, GameHistory, LeaderboardType, LeaderboardCategory

__all__ = [
    # NFT Models
    "Collection",
    "NFT",
    "Listing",
    "Market",
    "Sale",
    # User & Social
    "User",
    "Referral",
    "ReferralReward",
    "ReferralTier",
    # Quests & Badges
    "Quest",
    "UserQuest",
    "Badge",
    "UserBadge",
    "QuestType",
    "QuestStatus",
    # Leaderboards
    "LeaderboardEntry",
    "GameHistory",
    "LeaderboardType",
    "LeaderboardCategory",
]
