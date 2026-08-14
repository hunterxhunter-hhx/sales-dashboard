from pathlib import Path


root = Path(__file__).resolve().parent
html = (root / "dashboard-prototype.html").read_text(encoding="utf-8")
dist_html = (root / "dist" / "index.html").read_text(encoding="utf-8")

required_tokens = [
    "OWNER_CONVERSION_RATE",
    "ownerForecastRowsByRate",
    "ownerPredictionFromCarry",
    "reviewDailyPerformanceRecord",
    "weeklyPerformanceRecordsSummary",
    "week-summary",
    "本周每日复盘记录",
    "本周GMV",
]

missing = [token for token in required_tokens if token not in html]
assert not missing, "Missing review owner / weekly summary tokens: " + ", ".join(missing)

for forbidden in [
    "renderOwnerVarianceRows",
    "review-owner-gap",
    "ownerPredictionRowsByConversionRate",
    "weeklyReviewRecords",
    "split-live",
    "split-chase",
]:
    assert forbidden not in html, f"Forbidden old token remains: {forbidden}"

for token in ["OWNER_CONVERSION_RATE", "weeklyPerformanceRecordsSummary", "week-summary", "本周每日复盘记录"]:
    assert token in dist_html, f"dist/index.html missing {token}"

print("review owner prediction and weekly summary checks passed")
