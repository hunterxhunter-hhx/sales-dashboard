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


weekly_section = html[html.index('data-page="weekly"'):html.index('data-page="monthly"')]
render_weekly = function_body("renderWeekly")
daily_targets = function_body("renderWeeklyDailyTargets")

required_tokens = [
    "后续单日目标",
    'id="week-channel-conclusion"',
    'id="week-channel-trends"',
    'id="week-owner-conclusion"',
    'id="week-owner-rank"',
    "function coefficientOfVariation",
    "function renderWeeklyChannelTrendCards",
    "function renderWeeklyOwnerMtdBars",
    "function renderWeeklyOwnerConclusion",
    "较上周单周",
    "本周",
    "非本周",
]

missing = [token for token in required_tokens if token not in html]
assert not missing, "Missing weekly redesign tokens: " + ", ".join(missing)

for forbidden in [
    "单日GMV目标完成情况",
    'id="week-daily-target-date"',
    'id="week-top-owner-conclusion"',
    "renderWeeklyTopOwnerConclusion(current)",
    "预计差",
    "预计超",
]:
    assert forbidden not in weekly_section and forbidden not in daily_targets and forbidden not in render_weekly, f"Forbidden token remains: {forbidden}"

assert "const weekHistoryRows = weekWindowRows(current)" in render_weekly
assert "renderWeeklyChannelConclusion(current, weekHistoryRows, channelRows)" in render_weekly
assert "renderWeeklyChannelTrendCards(current, weekHistoryRows, channelRows)" in render_weekly
assert "renderWeeklyOwnerConclusion(current, prev, ownerMtdRows)" in render_weekly
assert "renderWeeklyOwnerMtdBars(ownerRows, current.gmv)" in render_weekly
assert "renderSegmentedReportHtml(channelRows" not in render_weekly
assert "renderSegmentedReportHtml(ownerRows" not in render_weekly
assert "history-mark" not in function_body("renderWeeklyOwnerMtdBars")
assert "直播/追单" in function_body("renderWeeklyOwnerMtdBars")
assert "承接 " in function_body("renderWeeklyOwnerMtdBars")
assert "本周贡献" not in function_body("renderWeeklyOwnerMtdBars")

print("weekly report redesign checks passed")
