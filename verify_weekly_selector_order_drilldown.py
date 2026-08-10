import re
from pathlib import Path


HTML = Path("dashboard-prototype.html").read_text(encoding="utf-8")


def function_body(name: str) -> str:
    match = re.search(rf"function {name}\([^)]*\) \{{", HTML)
    assert match, f"Missing function {name}"
    start = match.end()
    depth = 1
    index = start
    while index < len(HTML) and depth:
        char = HTML[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1
    assert depth == 0, f"Could not parse function {name}"
    return HTML[start:index - 1]


assert 'id="week-selector"' in HTML, "weekly report should expose a week selector"
assert "selectedWeek" in HTML, "state should keep the selected week key"
assert "function renderWeekSelector(" in HTML, "missing weekly selector renderer"
assert "function selectedWeekRow(" in HTML, "missing selected-week resolver"
assert "function isHiddenZeroWeeklyChannel(" in HTML, "missing weekly zero-GMV channel filter"

weekly = function_body("renderWeekly")
assert 'latest("week")' not in weekly, "weekly report must not always use latest week"
assert 'previous("week")' not in weekly, "weekly previous row should be relative to selected week"
assert "renderWeekSelector(rows)" in weekly, "weekly report should refresh selector options"
assert "selectedWeekRow(rows)" in weekly, "weekly report should use selected week"
assert "currentIndex" in weekly, "weekly report should calculate selected week index"
assert "isHiddenZeroWeeklyChannel" in weekly, "weekly report should hide zero anomaly channels"
assert "dimensionReportHtml(channelRows" in weekly, "weekly channels should keep the complete report renderer"
assert "dimensionReportHtml(ownerRows" in weekly, "weekly owners should keep the complete report renderer"
assert "showOrders: true" in weekly, "weekly channel/owner rows should allow order number expansion"

dimension_report = function_body("dimensionReportHtml")
assert "showOrders" in dimension_report, "dimension report renderer should support order drilldown"
assert "data-review-order-row" in dimension_report, "dimension rows should become clickable when order drilldown is enabled"
assert "review-order-detail" in dimension_report, "dimension rows should render hidden order detail"

selector = function_body("renderWeekSelector")
assert "week-selector" in selector, "selector renderer should target #week-selector"
assert "state.selectedWeek" in selector, "selector should update selectedWeek"
assert "renderWeekly()" in selector, "selector changes should rerender weekly report"

drilldown = function_body("bindReviewOrderDrilldown")
assert "week-channel-rank" in drilldown, "order drilldown should bind weekly channel list"
assert "week-owner-rank" in drilldown, "order drilldown should bind weekly owner list"

print("weekly selector and order drilldown checks passed")
