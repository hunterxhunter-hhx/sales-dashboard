from pathlib import Path


root = Path(__file__).resolve().parent
html = (root / "dashboard-prototype.html").read_text(encoding="utf-8")

required_tokens = [
    "function businessDayWindow",
    "function reviewAnchorDate",
    "function cohortCarryUsers",
    "function reviewWindowActuals",
    "function reviewCurrentPrediction",
    "function renderReviewCurrentLines",
    "function renderReviewFunnel",
    "review-current-predict-channel",
    "review-current-predict-owner",
    "review-current-actual-channel",
    "review-current-actual-owner",
    "review-predict-funnel",
    "review-actual-funnel",
    "review-conversion-date-selector",
    "当期预测",
    "往期预测",
    "当期实际",
    "往期实际",
    "工作日窗口",
]

missing = [token for token in required_tokens if token not in html]
assert not missing, "Missing review workday window tokens: " + ", ".join(missing)

for forbidden in [
    "review-channel-gap",
    "review-owner-gap",
    "渠道预测偏差",
    "销售预测偏差",
    "当期直播间预测",
    "当期直播间实际",
    "昨日追单预测",
    "昨日追单实际",
    "review-predicted-chase",
    "review-predicted-live",
    "review-actual-chase",
    "review-actual-live",
]:
    assert forbidden not in html, f"Forbidden old review token remains: {forbidden}"

assert "orderDate >= start && orderDate <= end" not in html
assert "window.days.some(day => sameDate(orderDate, day))" in html
assert "function userKeyForOrder(order)" in html
assert "text(order.wxid || order.userId)" in html
assert "const window = businessDayWindow(conversionDate, 3)" in html
assert "const currentUsers = cohortCarryUsersForDates(carryDates, \"current\")" in html
assert "const pastUsers = cohortCarryUsersForDates(carryDates, \"past\")" in html

print("review workday window compatibility checks passed")
