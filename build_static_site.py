from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from local_dashboard.data_store import DashboardStore


ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist"
DIST_DATA_DIR = DIST_DIR / "data"
DB_PATH = ROOT_DIR / "data" / "dashboard.sqlite3"
SOURCE_HTML = ROOT_DIR / "dashboard-prototype.html"


def json_text(payload) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str, separators=(",", ":"))


def published_html(source: str) -> str:
    replacements = {
        'apiGet("/api/dashboard")': 'apiGet("./data/dashboard.json")',
        'apiGet("/api/forecast-details")': 'apiGet("./data/forecast-details.json")',
        "正在读取本地数据...": "正在读取静态发布数据...",
        "读取本地数据失败": "读取静态数据失败",
    }
    html = source
    for old, new in replacements.items():
        html = html.replace(old, new)
    return html


class PublicIdMapper:
    def __init__(self, prefix: str):
        self.prefix = prefix
        self.values: dict[str, str] = {}

    def get(self, value: Any, fallback: Any = "") -> str:
        raw = str(value or fallback or "").strip()
        if not raw:
            return ""
        if raw not in self.values:
            self.values[raw] = f"{self.prefix}_{len(self.values) + 1:06d}"
        return self.values[raw]


def public_tags(value: Any) -> str:
    tags = str(value or "")
    return "螳螂到课" if "螳螂到课" in tags else ""


def public_scenario(row: dict[str, Any]) -> str:
    scenario = str(row.get("scenario") or "").strip()
    if scenario:
        return scenario
    product_name = str(row.get("product_name") or "")
    return "直播间转化" if "直播" in product_name else "追单转化"


def sanitize_sync(sync: dict[str, Any]) -> dict[str, Any]:
    status = sync.get("status") or {}
    files = []
    for item in status.get("files") or []:
        files.append(
            {
                "data_type": item.get("data_type", ""),
                "filename": item.get("filename", ""),
                "exists": bool(item.get("exists")),
                "size": int(item.get("size") or 0),
                "changed": bool(item.get("changed")),
                "last_imported_at": item.get("last_imported_at", ""),
                "last_result": item.get("last_result", {}),
            }
        )
    return {
        "changed": bool(sync.get("changed")),
        "imports": [
            {
                "data_type": item.get("data_type", ""),
                "filename": item.get("filename", ""),
                "result": item.get("result", {}),
            }
            for item in sync.get("imports") or []
        ],
        "status": {
            "ready": bool(status.get("ready")),
            "files": files,
        },
    }


def sanitize_dashboard_payload(payload: dict[str, Any]) -> dict[str, Any]:
    user_ids = PublicIdMapper("public_user")
    order_ids = PublicIdMapper("public_order")

    sanitized_carry = []
    for row in payload.get("carry") or []:
        sanitized_carry.append(
            {
                "union_id": user_ids.get(row.get("union_id")),
                "add_time": row.get("add_time", ""),
                "owner_name": row.get("owner_name", ""),
                "channel": row.get("channel", "") or "一转",
                "customer_tags": public_tags(row.get("customer_tags")),
            }
        )

    sanitized_orders = []
    for row in payload.get("orders") or []:
        user_key = row.get("wxid") or row.get("user_id") or row.get("order_id") or row.get("order_no")
        sanitized_orders.append(
            {
                "order_id": order_ids.get(row.get("order_id") or row.get("order_no")),
                "order_no": row.get("order_no", ""),
                "wxid": user_ids.get(user_key),
                "user_id": user_ids.get(user_key),
                "order_time": row.get("order_time", ""),
                "paid_amount": row.get("paid_amount", 0),
                "refund_amount": row.get("refund_amount", 0),
                "net_sales": row.get("net_sales", 0),
                "order_status": row.get("order_status", ""),
                "product_name": "",
                "scenario": public_scenario(row),
                "owner_name": row.get("owner_name", ""),
                "channel": row.get("channel", "") or "待补录",
                "attribution_type": row.get("attribution_type", ""),
                "add_time": row.get("add_time", ""),
            }
        )

    return {
        **payload,
        "privacy_mode": "public_sanitized",
        "sync": sanitize_sync(payload.get("sync") or {}),
        "carry": sanitized_carry,
        "orders": sanitized_orders,
    }


def build_static_site() -> dict[str, int | str]:
    store = DashboardStore(DB_PATH, ROOT_DIR)
    store.init_db()
    sync = store.sync_source_files()

    dashboard_payload = sanitize_dashboard_payload({
        "sync": sync,
        "summary": store.summary(),
        "owners": store.owner_breakdown(),
        "carry": store.carry_details(),
        "orders": store.order_details(limit=100000),
        "youzan": store.youzan_summary(),
        "static_built_at": datetime.now().isoformat(timespec="seconds"),
    })
    forecast_payload = {
        "rows": store.forecast_detail_rows(),
        "static_built_at": dashboard_payload["static_built_at"],
    }

    DIST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "index.html").write_text(published_html(SOURCE_HTML.read_text(encoding="utf-8")), encoding="utf-8")
    (DIST_DIR / ".nojekyll").write_text("", encoding="utf-8")
    (DIST_DATA_DIR / "dashboard.json").write_text(json_text(dashboard_payload), encoding="utf-8")
    (DIST_DATA_DIR / "forecast-details.json").write_text(json_text(forecast_payload), encoding="utf-8")

    return {
        "dist": str(DIST_DIR),
        "carry": len(dashboard_payload["carry"]),
        "orders": len(dashboard_payload["orders"]),
        "forecast_rows": len(forecast_payload["rows"]),
    }


if __name__ == "__main__":
    result = build_static_site()
    print(
        "Static site built: "
        f"{result['dist']} "
        f"(carry={result['carry']}, orders={result['orders']}, forecast_rows={result['forecast_rows']})"
    )
