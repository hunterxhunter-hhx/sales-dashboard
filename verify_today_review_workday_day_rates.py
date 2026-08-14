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


render_today = function_body("renderToday")
render_review = function_body("renderReview")
review_actuals = function_body("reviewWindowActuals")
window = function_body("businessDayWindow")
channel_forecast = function_body("forecastCurrentChannelRows")

assert 'id="today-conversion-date-selector"' in html
assert 'id="review-conversion-date-selector"' in html
assert "DAY_RATE_TABLE" in html
assert "PAST_AVERAGE_ORDER_COUNT = 1" in html

assert "businessDayWindow(conversionDate, 3)" in render_today
assert "forecastForDate(carryDate, conversionDate)" in render_today
assert "businessDayWindow(conversionDate, 3)" in review_actuals
assert "forecastForDate(carryDate, conversionDate)" in render_review
assert "nextBusinessDayOnOrAfter(targetDate)" in window
assert "isBusinessDay(cursor)" in window

assert "allocateInteger" not in channel_forecast, "Channel forecast must use each channel day1 rate directly, not allocation by overall total"
assert "expectedOrders = row.carry * number(rates.day1)" in channel_forecast
assert "Math.round(expectedOrders)" in channel_forecast
assert "对齐到当期预测总单数" not in html

print("today/review workday day-rate verification passed")
