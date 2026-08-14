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


required_functions = [
    "isBusinessDay",
    "reviewAnchorDate",
    "nextBusinessDayOnOrAfter",
    "businessDayWindow",
    "reviewWeekendCarryEnd",
    "cohortCarryUsers",
    "actualCarryForUsers",
    "reviewCurrentCarry",
    "reviewWindowActuals",
]
missing = [name for name in required_functions if f"function {name}" not in html]
assert not missing, "Missing review business-day helpers: " + ", ".join(missing)
assert html.count("function isBusinessDay") == 1

window = function_body("businessDayWindow")
assert "nextBusinessDayOnOrAfter(targetDate)" in window
assert "isBusinessDay(cursor)" in window
assert "days.length < count" in window
assert "return { start: days[0], end: days[days.length - 1], days }" in window

anchor = function_body("reviewAnchorDate")
assert "day === 6" in anchor
assert "day === 0" in anchor
assert "return addDays(target, -1)" in anchor
assert "return addDays(target, -2)" in anchor

cohort = function_body("cohortCarryUsers")
assert "const anchor = reviewAnchorDate(targetDate)" in cohort
assert "const carryEnd = reviewWeekendCarryEnd(anchor)" in cohort
assert "addTime >= anchor && addTime <= carryEnd" in cohort
assert "addTime < anchor" in cohort

actuals = function_body("reviewWindowActuals")
assert "function reviewWindowActuals(carryDate, conversionDate = carryDate)" in html
assert "const anchor = reviewAnchorDate(carryDate)" in actuals
assert "const window = businessDayWindow(conversionDate, 3)" in actuals
assert 'cohortCarryUsers(carryDate, "current")' in actuals
assert 'cohortCarryUsers(carryDate, "past")' in actuals

render_today = function_body("renderToday")
render_review = function_body("renderReview")
assert "businessDayWindow(conversionDate, 3)" in render_today
assert "window.days.map((date, index) => `day${index + 1}" in render_today
assert "windowActuals.window.days.map((date, index) => `day${index + 1}" in render_review
assert "工作日窗口" in html
assert "D~D+2" not in html[html.index('data-page="review"'):html.index('data-page="weekly"')]

print("review business-day window static checks passed")
