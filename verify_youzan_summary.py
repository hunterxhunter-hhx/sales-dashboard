from __future__ import annotations

import sys
from pathlib import Path

from local_dashboard.data_store import DashboardStore


def main() -> int:
    root = Path(__file__).resolve().parent
    store = DashboardStore(root / "data" / "dashboard.sqlite3", root)
    summary = store.youzan_summary()

    cards = summary.get("cards") or {}
    charts = summary.get("charts") or {}
    sku_gmv = charts.get("sku_gmv") or []
    daily = charts.get("daily") or []

    checks = [
        (summary.get("available") is True, "有赞数据.xlsx should be available"),
        (cards.get("estimated_month_gmv", 0) > 0, "预估当月GMV should be greater than 0"),
        (cards.get("estimated_month_profit", 0) > 0, "预估当月毛利 should be greater than 0"),
        (any(row.get("value", 0) > 0 for row in sku_gmv), "各SKU GMV should contain non-zero values"),
        (any(row.get("gmv", 0) > 0 for row in daily), "每日GMV should contain non-zero values"),
    ]

    failed = [message for passed, message in checks if not passed]
    if failed:
        for message in failed:
            print(f"FAIL: {message}")
        print(f"cards={cards}")
        print(f"first_sku_rows={sku_gmv[:3]}")
        print(f"first_daily_rows={daily[:3]}")
        return 1

    print("PASS: 有赞数据聚合已接入真实金额")
    print(f"cards={cards}")
    print(f"first_sku_rows={sku_gmv[:3]}")
    print(f"first_daily_rows={daily[:3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
