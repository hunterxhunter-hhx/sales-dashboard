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
review_section = html[html.index('data-page="review"'):html.index('data-page="weekly"')]

required = [
    'id="today-date-selector"',
    'id="today-conversion-date-selector"',
    'id="review-date-selector"',
    'id="review-conversion-date-selector"',
    "往期预测",
    "当期预测",
    "DAY_RATE_TABLE",
    "PAST_AVERAGE_ORDER_COUNT",
    "function renderTodayDateSelectors(",
    "function renderReviewDateSelectors(",
    "function forecastRateTotals(",
    "function forecastCurrentChannelRows(",
    "function renderCurrentPastSummary(",
    "function businessDayWindow(",
]
missing = [token for token in required if token not in html]
assert not missing, "today prediction model verification failed; missing=" + ", ".join(missing)

forecast_for_date = function_body("forecastForDate")
render_today = function_body("renderToday")
render_review = function_body("renderReview")
channel_forecast = function_body("forecastCurrentChannelRows")

for token in [
    "currentOrders",
    "pastOrders",
    "totalOrders",
    "currentGmv",
    "pastGmv",
    "totalGmv",
    "rateModel",
]:
    assert token in forecast_for_date, f"forecastForDate missing {token}"

for forbidden in [
    "review-predicted-chase",
    "review-predicted-live",
    "review-actual-chase",
    "review-actual-live",
    "review-predict-live-lines",
    "review-predict-chase-lines",
    "review-channel-gap",
    "review-owner-gap",
]:
    assert forbidden not in today_section
    assert forbidden not in review_section

assert "forecastFlowValues(row, \"total\")" in render_today
assert "renderCurrentPastSummary(" in render_today
assert "businessDayWindow(conversionDate, 3)" in render_today
assert "forecastForDate(carryDate, conversionDate)" in render_review
assert "reviewWindowActuals(carryDate, conversionDate)" in render_review
assert "reviewCurrentPrediction(carryDate, conversionDate, forecast, reviewCarry)" in render_review
assert "expectedOrders = row.carry * number(rates.day1)" in channel_forecast

print("today prediction model verification passed")
