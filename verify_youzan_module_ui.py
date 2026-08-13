from __future__ import annotations

import sys
from pathlib import Path

from local_dashboard.data_store import DashboardStore


def main() -> int:
    root = Path(__file__).resolve().parent
    html = (root / "dashboard-prototype.html").read_text(encoding="utf-8")
    store = DashboardStore(root / "data" / "dashboard.sqlite3", root)
    summary = store.youzan_summary()

    tables = summary.get("tables") or {}
    sku_summary = tables.get("sku_summary") or []
    required_html = [
        "youzan-top-products",
        "GMV前五",
        "youzan-edit-note",
        'data-local-edit="youzan-note"',
        "youzan-sku-table",
        "youzan-type-gmv-list",
        "youzan-type-profit-list",
        "renderYouzanTopProducts",
        "renderYouzanSkuTable",
        "renderYouzanTypeList",
        'xAxis: { type: "value"',
        'yAxis: { type: "category"',
        "label: { show: true, position: \"right\"",
    ]

    failures = []
    for marker in required_html:
        if marker not in html:
            failures.append(f"missing HTML/JS marker: {marker}")

    if len(sku_summary) < 2:
        failures.append("sku_summary should include product rows and a total row")
    if not any(row.get("is_total") for row in sku_summary):
        failures.append("sku_summary should include an is_total row")
    if not any(row.get("gmv", 0) > 0 and row.get("profit", 0) > 0 for row in sku_summary):
        failures.append("sku_summary should include non-zero GMV/profit rows")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: Youzan module UI and summary data are wired")
    return 0


if __name__ == "__main__":
    sys.exit(main())
