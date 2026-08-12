from pathlib import Path


root = Path(__file__).resolve().parent
html = (root / "dashboard-prototype.html").read_text(encoding="utf-8")

required_tokens = [
    "function reviewThreeDayWindow",
    "function cohortCarryUsers",
    "function reviewWindowActuals",
    "function reviewCurrentPrediction",
    "function distributePredictionToOwners",
    "function renderReviewCurrentLines",
    "function renderReviewFunnel",
    "review-current-predict-channel",
    "review-current-predict-owner",
    "review-current-actual-channel",
    "review-current-actual-owner",
    "review-predict-funnel",
    "review-actual-funnel",
    "当期预测",
    "往期预测",
    "当期实际",
    "往期实际",
    "追单预测",
    "直播间预测",
    "追单实际",
    "直播间实际",
    "D+2",
]

missing = [token for token in required_tokens if token not in html]
assert not missing, "Missing review three-day window tokens: " + ", ".join(missing)

for forbidden in [
    "review-channel-gap",
    "review-owner-gap",
    "渠道预测偏差",
    "销售预测偏差",
    "当期直播间预测",
    "当期直播间实际",
    "昨日追单预测",
    "昨日追单实际",
]:
    assert forbidden not in html, f"Forbidden old review token remains: {forbidden}"

assert "orderDate >= start && orderDate <= end" in html
assert "function userKeyForOrder(order)" in html
assert "text(order.wxid || order.userId)" in html
assert "const user = currentMeta.get(orderKey)" in html
assert "pastIds.has(orderKey)" in html
assert "predictionOwners[index].orders = allocation" in html

print("review three-day window checks passed")
