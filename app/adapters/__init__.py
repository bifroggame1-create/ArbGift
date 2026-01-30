"""
Market adapter registry.

All marketplace adapters for the TON Gift Aggregator.
"""
from app.adapters.base import BaseMarketAdapter
from app.adapters.getgems import GetGemsAdapter
from app.adapters.fragment import FragmentAdapter
from app.adapters.mrkt import MRKTAdapter
from app.adapters.tonnel import TonnelAdapter
from app.adapters.tonapi_sales import TONAPISalesAdapter

__all__ = [
    "BaseMarketAdapter",
    "GetGemsAdapter",
    "FragmentAdapter",
    "MRKTAdapter",
    "TonnelAdapter",
    "TONAPISalesAdapter",
    "get_all_adapters",
    "get_adapter_by_slug",
]


def get_all_adapters() -> list[BaseMarketAdapter]:
    """
    Get instances of all available market adapters.

    Returns:
        List of initialized adapter instances.
    """
    return [
        GetGemsAdapter(),
        FragmentAdapter(),
        MRKTAdapter(),
        TonnelAdapter(),
        TONAPISalesAdapter(),
    ]


def get_adapter_by_slug(slug: str) -> BaseMarketAdapter | None:
    """
    Get adapter instance by market slug.

    Args:
        slug: Market slug (e.g., "getgems", "fragment")

    Returns:
        Adapter instance or None if not found.
    """
    adapters = get_all_adapters()
    for adapter in adapters:
        if adapter.slug == slug:
            return adapter
    return None
