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


def function_source(name: str) -> str:
    match = re.search(rf"function {name}\([^)]*\) \{{", html)
    assert match, f"Missing function {name}"
    start = match.start()
    depth = 1
    index = match.end()
    while index < len(html) and depth:
        char = html[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1
    assert depth == 0, f"Could not parse function {name}"
    return html[start:index]


required_functions = [
    "isBusinessDay",
    "reviewAnchorDate",
    "businessDayWindow",
    "reviewWeekendCarryEnd",
    "actualCarryForUsers",
    "reviewCurrentCarry",
]
missing = [name for name in required_functions if f"function {name}" not in html]
assert not missing, "Missing review business-day helpers: " + ", ".join(missing)
assert html.count("function isBusinessDay") == 1

window = function_body("businessDayWindow")
assert "isBusinessDay(cursor)" in window
assert "days.length < count" in window
assert "return { start: days[0], end: days[days.length - 1], days }" in window

anchor = function_body("reviewAnchorDate")
assert "day === 6" in anchor
assert "day === 0" in anchor
assert "return addDays(target, -1)" in anchor
assert "return addDays(target, -2)" in anchor

weekend = function_body("reviewWeekendCarryEnd")
assert "anchor.getDay() !== 5" in weekend
assert "addDays(anchor, 2)" in weekend

cohort = function_body("cohortCarryUsers")
assert "const anchor = reviewAnchorDate(targetDate)" in cohort
assert "const carryEnd = reviewWeekendCarryEnd(anchor)" in cohort
assert "addTime >= anchor && addTime <= carryEnd" in cohort
assert "addTime < anchor" in cohort

actuals = function_body("reviewWindowActuals")
assert "const anchor = reviewAnchorDate(targetDate)" in actuals
assert "const window = businessDayWindow(anchor, 3)" in actuals
assert "cohortCarryUsers(anchor, \"current\")" in actuals
assert "cohortCarryUsers(anchor, \"past\")" in actuals

prediction = function_body("reviewCurrentPrediction")
assert "predictionWithActualCarry(anchor, actualCarry" in prediction
assert "const anchorForecast = sameDate(anchor, forecast.target) ? forecast : forecastForDate(anchor)" in prediction
assert "anchorForecast.model" in prediction

render_review = function_body("renderReview")
assert "const reviewCarry = reviewCurrentCarry(target)" in render_review
assert "reviewCurrentPrediction(target, forecast, reviewCarry)" in render_review
assert "const day = actualDay(target)" in render_review
assert "const forecast = forecastForDate(target)" in render_review
assert "actualCarryDay(target)" in render_review
assert "3个工作日" in render_review

assert "D~D+2" not in html[html.index('data-page="review"'):html.index('data-page="weekly"')]
assert "reviewThreeDayWindow" not in html


def js_date(year: int, month: int, day: int) -> str:
    return f"new Date({year}, {month - 1}, {day})"


snippet = "\n".join([
    function_source("dateOnly"),
    function_source("sameDate"),
    function_source("addDays"),
    function_source("isBusinessDay"),
    function_source("reviewAnchorDate"),
    function_source("businessDayWindow"),
    function_source("reviewWeekendCarryEnd"),
    "const state = { carry: [] };",
    function_source("cohortCarryUsers"),
    "function fmt(date) { return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`; }",
    "function assert(condition, message) { if (!condition) throw new Error(message); }",
    f"const fridayWindow = businessDayWindow(reviewAnchorDate({js_date(2026, 8, 7)}), 3);",
    "assert(fmt(fridayWindow.start) === '2026-08-07', 'Friday window starts Friday');",
    "assert(fmt(fridayWindow.end) === '2026-08-11', 'Friday window skips weekend and ends Tuesday');",
    f"assert(fmt(reviewWeekendCarryEnd(reviewAnchorDate({js_date(2026, 8, 7)}))) === '2026-08-09', 'Friday carry includes Sunday');",
    f"assert(fmt(reviewAnchorDate({js_date(2026, 8, 8)})) === '2026-08-07', 'Saturday anchors Friday');",
    f"assert(fmt(reviewAnchorDate({js_date(2026, 8, 9)})) === '2026-08-07', 'Sunday anchors Friday');",
    f"const thursdayWindow = businessDayWindow(reviewAnchorDate({js_date(2026, 8, 6)}), 3);",
    "assert(fmt(thursdayWindow.start) === '2026-08-06', 'Thursday window starts Thursday');",
    "assert(fmt(thursdayWindow.end) === '2026-08-10', 'Thursday window skips weekend and ends Monday');",
    "state.carry = [",
    "  { unionid: 'thu', addTime: new Date(2026, 7, 6) },",
    "  { unionid: 'fri', addTime: new Date(2026, 7, 7) },",
    "  { unionid: 'sat', addTime: new Date(2026, 7, 8) },",
    "  { unionid: 'sun', addTime: new Date(2026, 7, 9) },",
    "  { unionid: 'mon', addTime: new Date(2026, 7, 10) }",
    "];",
    f"const fridayCohort = cohortCarryUsers({js_date(2026, 8, 7)}, 'current').map(user => user.unionid).sort().join(',');",
    "assert(fridayCohort === 'fri,sat,sun', 'Friday cohort includes Friday through Sunday carry');",
    f"const saturdayCohort = cohortCarryUsers({js_date(2026, 8, 8)}, 'current').map(user => user.unionid).sort().join(',');",
    "assert(saturdayCohort === 'fri,sat,sun', 'Saturday cohort resolves to Friday through Sunday carry');",
    f"const pastCohort = cohortCarryUsers({js_date(2026, 8, 7)}, 'past').map(user => user.unionid).sort().join(',');",
    "assert(pastCohort === 'thu', 'Past cohort excludes Friday through Sunday carry');",
])

Path("tmp_review_business_day_window_check.js").write_text(snippet, encoding="utf-8")
assert "function assert" in snippet
print("review business-day window static checks passed")
