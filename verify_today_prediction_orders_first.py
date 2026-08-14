import re
from pathlib import Path


html = Path("dashboard-prototype.html").read_text(encoding="utf-8")


def function_body(name: str) -> str:
    match = re.search(rf"function {name}\([^)]*\) \{{", html)
    assert match, f"Missing function {name}"
    start = match.end()
    depth = 1
    index = start
    while index < len(html) and depth:
        char = html[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1
    assert depth == 0, f"Could not parse function {name}"
    return html[start:index - 1]


today_section = html[html.index('data-page="today"'):html.index('data-page="review"')]
assert "往期预测" in today_section
assert "当期预测" in today_section
assert "today-target-meta-1" in today_section
assert "today-target-meta-2" in today_section
assert "today-target-meta-3" in today_section
assert 'id="today-conversion-date-selector"' in today_section
assert "DAY_RATE_TABLE" in html
assert "PAST_AVERAGE_ORDER_COUNT" in html
assert "const ORDER_UNIT_PRICE = 2980;" in html
assert "1980" not in html

forecast_totals = function_body("forecastRateTotals")
channel_forecast = function_body("forecastCurrentChannelRows")
render_today = function_body("renderToday")

for token in [
    "currentOrders",
    "pastOrders",
    "currentGmv",
    "pastGmv",
    "totalGmv",
    "ORDER_UNIT_PRICE",
]:
    assert token in forecast_totals, f"forecastRateTotals missing {token}"

assert "pastBase = carry + PAST_AVERAGE_ORDER_COUNT" in forecast_totals
assert "number(overall.day2) + number(overall.day3)" in forecast_totals
assert "expectedOrders = row.carry * number(rates.day1)" in channel_forecast
assert "orders = Math.max(0, Math.round(expectedOrders))" in channel_forecast
assert "gmv = orders * ORDER_UNIT_PRICE" in channel_forecast
assert "renderCurrentPastSummary(" in render_today
assert "day1" in render_today and "day2/day3" in render_today
assert "renderCurrentPastSummary(" in render_today

monthly_targets = function_body("renderMonthlyTargets")
assert "today-target-meta-${tier}" in monthly_targets
assert "completionPercent" in monthly_targets
assert "已完成" in monthly_targets

print("today prediction orders-first checks passed")
