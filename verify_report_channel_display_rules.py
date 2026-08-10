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


short_channel = function_body("shortChannel")
expected_short_names = [
    'if (name.includes("挂图")) return "挂图";',
    'if (name.includes("公号")) return "公号";',
    'if (name.includes("回捞")) return "激活";',
    'if (name.includes("询课")) return "询课";',
    'if (name.includes("有赞")) return "有赞";',
    'if (name.includes("视频号")) return "视频号";',
]
for token in expected_short_names:
    assert token in short_channel, f"shortChannel missing rule: {token}"

dimension_report = function_body("dimensionReportHtml")
assert "options.short ? shortChannel : name => name" in dimension_report
assert "${label(row.name)}" in dimension_report

weekly = function_body("renderWeekly")
monthly = function_body("renderMonthly")

assert "isVisibleWeeklyOwner" in HTML, "weekly owner visibility helper missing"
assert ".filter(isVisibleWeeklyOwner)" in weekly, "weekly owners should be filtered"
assert "row.name === \"待补录\"" in function_body("isVisibleWeeklyOwner")
assert "row.orders > 0 || row.gmv > 0" in function_body("isVisibleWeeklyOwner")

assert "dimensionReportHtml(channelRows, current.gmv, averageDimension(prior, \"channels\"), { showOrders: true, short: true })" in weekly
assert "dimensionReportHtml(channelRows, current.gmv, averageDimension(prior, \"channels\"), { short: true })" in monthly

print("report channel display rule checks passed")
