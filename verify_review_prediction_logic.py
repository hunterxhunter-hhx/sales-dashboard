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


review_section = html[html.index('data-page="review"'):html.index('data-page="weekly"')]
render_review = function_body("renderReview")
review_actuals = function_body("reviewWindowActuals")
review_prediction = function_body("reviewCurrentPrediction")

required_dom = [
    'id="review-date-selector"',
    'id="review-conversion-date-selector"',
    'id="review-current-predicted"',
    'id="review-past-predicted"',
    'id="review-current-actual"',
    'id="review-past-actual"',
    'id="review-current-predict-channel"',
    'id="review-current-predict-owner"',
    'id="review-current-actual-channel"',
    'id="review-current-actual-owner"',
    'id="review-predict-funnel"',
    'id="review-actual-funnel"',
    "当期预测",
    "往期预测",
    "当期实际",
    "往期实际",
]
missing = [token for token in required_dom if token not in review_section]
assert not missing, "review prediction DOM missing: " + ", ".join(missing)

for token in [
    "renderReviewDateSelectors()",
    "forecastForDate(carryDate, conversionDate)",
    "reviewWindowActuals(carryDate, conversionDate)",
    "reviewCurrentPrediction(carryDate, conversionDate, forecast, reviewCarry)",
    "renderReviewCurrentLines(",
    "renderReviewFunnel(",
    "orderedReviewChannelNames(",
    "completeReviewRows(",
]:
    assert token in render_review, f"renderReview missing {token}"

assert "businessDayWindow(conversionDate, 3)" in review_actuals
assert "cohortCarryUsers(carryDate, \"current\")" in review_actuals
assert "cohortCarryUsers(carryDate, \"past\")" in review_actuals
assert "currentRows = forecast?.currentRows" in review_prediction
assert "forecast?.currentOrders" in review_prediction

for forbidden in [
    "review-predicted-chase",
    "review-predicted-live",
    "review-actual-chase",
    "review-actual-live",
    "review-predict-live-lines",
    "review-predict-chase-lines",
    "review-actual-live-lines",
    "review-actual-chase-lines",
    "review-channel-gap",
    "review-owner-gap",
    "渠道预测偏差",
    "销售预测偏差",
]:
    assert forbidden not in review_section, f"old review token remains: {forbidden}"

print("review prediction logic verification passed")
