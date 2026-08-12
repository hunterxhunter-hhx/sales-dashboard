from pathlib import Path


root = Path(__file__).resolve().parent
html = (root / "dashboard-prototype.html").read_text(encoding="utf-8")

required_tokens = [
    "const OWNER_CONVERSION_RATE",
    '"吴秋禅": 0.0310',
    '"祁春如": 0.0104',
    '"万雪莲": 0.0086',
    '"辛雨薇": 0.0085',
    '"黄依婷": 0.0075',
    '"徐佳莹": 0.0073',
    '"石玉": 0.0067',
    '"赵宇欣": 0.0047',
    '"激活组": 0.0003',
    "function ownerForecastRowsByRate",
    "OWNER_CONVERSION_RATE[name]",
    "Math.round(carry * rate)",
    "row.name !== \"待补录\"",
    "承接人数",
    "function reviewDailyPerformanceRecord",
    "function weeklyPerformanceRecordsSummary",
    "本周每日复盘记录",
    "最佳销售",
    "最弱销售",
    "最佳渠道",
    "最弱渠道",
    "当期直播间预测",
    "当期直播间实际",
    "review-split-title live-title",
    "review-split-title chase-title",
    'class="form-control compact-conclusion" id="week-top-owner-conclusion"',
]

missing = [token for token in required_tokens if token not in html]
assert not missing, "Missing expected review/weekly update tokens: " + ", ".join(missing)

assert "const predictedOwnerRows = [...(forecast.prediction.owners?.values?.() || [])].map(compactMetric);" not in html
assert 'id="week-top-owner-conclusion" style="margin-top:12px"' not in html

print("review owner forecast and weekly summary checks passed")
