from pathlib import Path
import re


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


required_tokens = [
    "const ORDER_UNIT_PRICE = 2980;",
    "const CHANNEL_CONVERSION_RATE =",
    '"2-企微-询课"',
    "0.0202",
    "0.0188",
    "0.0175",
    "0.0108",
    "0.0049",
    "0.0016",
    "function channelConversionExpectedOrders(",
    "function channelConversionPredictedOrders(",
]

missing = [token for token in required_tokens if token not in html]
assert not missing, "Missing conversion forecast tokens: " + ", ".join(missing)

predicted_order = function_body("predictedOrderCount")
assert "ORDER_UNIT_PRICE" in predicted_order
assert "2980" not in predicted_order

dimension_forecast = function_body("dimensionForecastRows")
assert 'dimension === "channels"' in dimension_forecast
assert "channelConversionExpectedOrders(row.name, row.carry)" in dimension_forecast
assert "Math.round(row.expectedOrders || 0)" in dimension_forecast
assert "targetOrders" in dimension_forecast
assert "ORDER_UNIT_PRICE" in dimension_forecast
assert "2980" not in dimension_forecast

split_forecast = function_body("splitForecastRows")
assert "ORDER_UNIT_PRICE" in split_forecast
assert "2980" not in split_forecast

render_today = function_body("renderToday")
forecast_for_date = function_body("forecastForDate")
assert "predictedChaseOrders * ORDER_UNIT_PRICE" in forecast_for_date
assert "predictedLiveOrders * ORDER_UNIT_PRICE" in forecast_for_date
assert "2980" in render_today

render_review = function_body("renderReview")
assert "forecastForDate(target)" in render_review
assert "forecast.prediction.owners" in render_review

assert "1980" not in html, "Forecast page should not keep the old 1980 unit price marker"

print("conversion forecast model verification passed")
