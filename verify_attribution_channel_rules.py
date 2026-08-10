import tempfile
from pathlib import Path

from local_dashboard.data_store import DashboardStore, classify_channel


HTML = Path("dashboard-prototype.html").read_text(encoding="utf-8")


def make_store() -> DashboardStore:
    temp_dir = tempfile.TemporaryDirectory()
    root = Path(temp_dir.name)
    store = DashboardStore(root / "dashboard.sqlite3", root)
    store.init_db()
    store._temp_dir = temp_dir
    return store


def first_order(store: DashboardStore) -> dict:
    rows = store.order_details(limit=10)
    assert rows, "expected at least one order detail"
    return rows[0]


assert classify_channel("客户标签包含 2-视频号-下单") == "2-视频号-下单"
assert classify_channel("客户标签包含 一转") == "一转"
assert '"一转"' in HTML.split("const CHANNELS =")[1].split(";")[0]
assert '"激活组"' in HTML.split("const CHANNELS =")[1].split(";")[0]
assert 'if (name.includes("一转")) return "一转";' in HTML
assert 'if (name.includes("激活组")) return "激活组";' in HTML

store = make_store()
store.import_carry_rows(
    [
        {
            "unionid": "u-video",
            "员工userid": "e-1",
            "添加时间": "2026-05-15 19:23:14",
            "所属员工": "135-徐佳莹",
            "客户标签": "旧标签",
        }
    ],
    filename="carry-old.xlsx",
)
store.import_carry_rows(
    [
        {
            "unionid": "u-video",
            "员工userid": "e-1",
            "添加时间": "2026-05-15 19:23:14",
            "所属员工": "135-徐佳莹",
            "客户标签": "新标签，2-视频号-下单",
        }
    ],
    filename="carry-new.xlsx",
)
store.import_order_rows(
    [
        {
            "订单ID": "order-video",
            "订单号": "no-video",
            "微信id": "u-video",
            "下单时间": "2026-08-04 20:37:07",
            "实付金额": "2980",
            "退款金额": "0",
            "商品名称": "直播课",
        }
    ],
    filename="orders.xlsx",
)
order = first_order(store)
assert order["channel"] == "2-视频号-下单", order

store = make_store()
store.import_carry_rows(
    [
        {
            "unionid": "u-transfer",
            "员工userid": "e-2",
            "添加时间": "2026-07-01 09:00:00",
            "所属员工": "586-赵宇欣",
            "客户标签": "课程标签，一转",
        }
    ],
    filename="carry.xlsx",
)
store.import_order_rows(
    [
        {
            "订单ID": "order-transfer",
            "订单号": "no-transfer",
            "微信id": "u-transfer",
            "下单时间": "2026-07-02 10:00:00",
            "实付金额": "2980",
            "退款金额": "0",
            "商品名称": "追单课",
        }
    ],
    filename="orders.xlsx",
)
order = first_order(store)
assert order["channel"] == "一转", order

store = make_store()
store.import_carry_rows(
    [
        {
            "unionid": "u-manual-missing",
            "员工userid": "589",
            "添加时间": "2026-07-01 09:00:00",
            "所属员工": "589-祁春如",
            "客户标签": "无业务渠道标签",
        }
    ],
    filename="carry.xlsx",
)
store.import_order_rows(
    [
        {
            "订单ID": "order-manual-missing",
            "订单号": "no-manual-missing",
            "微信id": "u-manual-missing",
            "下单时间": "2026-07-02 10:00:00",
            "实付金额": "2980",
            "退款金额": "0",
            "商品名称": "追单课",
            "手动备注": "一转",
        }
    ],
    filename="orders.xlsx",
)
order = first_order(store)
assert order["channel"] == "一转", order
assert order["attribution_type"] == "auto", order

store = make_store()
store.import_order_rows(
    [
        {
            "订单ID": "order-manual-pending",
            "订单号": "no-manual-pending",
            "微信id": "u-manual-pending",
            "下单时间": "2026-07-02 10:00:00",
            "实付金额": "2980",
            "退款金额": "0",
            "商品名称": "追单课",
            "手动备注": "一转",
        }
    ],
    filename="orders.xlsx",
)
order = first_order(store)
assert order["channel"] == "一转", order
assert order["attribution_type"] == "pending", order

store = make_store()
store.import_carry_rows(
    [
        {
            "unionid": "u-manual-explicit",
            "员工userid": "589",
            "添加时间": "2026-07-01 09:00:00",
            "所属员工": "589-祁春如",
            "客户标签": "2-视频号-下单",
        }
    ],
    filename="carry.xlsx",
)
store.import_order_rows(
    [
        {
            "订单ID": "order-manual-explicit",
            "订单号": "no-manual-explicit",
            "微信id": "u-manual-explicit",
            "下单时间": "2026-07-02 10:00:00",
            "实付金额": "2980",
            "退款金额": "0",
            "商品名称": "追单课",
            "手动备注": "一转",
        }
    ],
    filename="orders.xlsx",
)
order = first_order(store)
assert order["channel"] == "2-视频号-下单", order

store = make_store()
store.import_order_rows(
    [
        {
            "订单ID": "order-activation",
            "订单号": "no-activation",
            "微信id": "u-missing",
            "下单时间": "2026-07-02 10:00:00",
            "实付金额": "2980",
            "退款金额": "0",
            "商品名称": "追单课",
            "推广员（修改后）": "常丁健 ",
        }
    ],
    filename="orders.xlsx",
)
order = first_order(store)
assert order["owner_name"] == "激活组", order
assert order["channel"] == "激活组", order
assert order["attribution_type"] == "activation_group", order

print("attribution channel rule checks passed")
