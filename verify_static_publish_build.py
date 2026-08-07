import json
import subprocess
import sys
from pathlib import Path


root = Path(__file__).resolve().parent
build_script = root / "build_static_site.py"
build_bat = root / "build_static_site.bat"
requirements = root / "requirements.txt"
workflow = root / ".github" / "workflows" / "deploy-pages.yml"
gitignore = root / ".gitignore"
dist_dir = root / "dist"
index_html = dist_dir / "index.html"
dashboard_json = dist_dir / "data" / "dashboard.json"
forecast_json = dist_dir / "data" / "forecast-details.json"

assert build_script.exists(), "Missing build_static_site.py"
assert build_bat.exists(), "Missing build_static_site.bat"
assert requirements.exists(), "Missing requirements.txt"
assert workflow.exists(), "Missing .github/workflows/deploy-pages.yml"
assert gitignore.exists(), "Missing .gitignore"

script = build_script.read_text(encoding="utf-8")
required_script_tokens = [
    "DashboardStore",
    "sync_source_files",
    "sanitize_dashboard_payload",
    "privacy_mode",
    "dashboard.json",
    "forecast-details.json",
    "dashboard-prototype.html",
    "dist",
]
missing_script_tokens = [token for token in required_script_tokens if token not in script]
assert not missing_script_tokens, "Static build script missing tokens: " + ", ".join(missing_script_tokens)

requirements_text = requirements.read_text(encoding="utf-8")
assert "openpyxl" in requirements_text, "requirements.txt should include openpyxl"

workflow_text = workflow.read_text(encoding="utf-8")
workflow_tokens = [
    "pages: write",
    "actions/upload-pages-artifact",
    "actions/deploy-pages",
    "dist",
]
missing_workflow_tokens = [token for token in workflow_tokens if token not in workflow_text]
assert not missing_workflow_tokens, "Deploy workflow missing tokens: " + ", ".join(missing_workflow_tokens)
assert "build_static_site.py" not in workflow_text, "Workflow should deploy prebuilt dist and not require Excel on GitHub"
assert "pip install" not in workflow_text, "Workflow should not install Excel parsing dependencies"

gitignore_text = gitignore.read_text(encoding="utf-8")
for ignored in ["*.xlsx", "data/source/*.xlsx", "data/*.sqlite3", "*.log"]:
    assert ignored in gitignore_text, f".gitignore should include {ignored}"

result = subprocess.run(
    [sys.executable, str(build_script)],
    cwd=root,
    text=True,
    capture_output=True,
    check=False,
)
assert result.returncode == 0, result.stderr or result.stdout

assert index_html.exists(), "Missing dist/index.html"
assert (dist_dir / ".nojekyll").exists(), "Missing dist/.nojekyll"
assert dashboard_json.exists(), "Missing dist/data/dashboard.json"
assert forecast_json.exists(), "Missing dist/data/forecast-details.json"

published_html = index_html.read_text(encoding="utf-8")
assert 'apiGet("./data/dashboard.json")' in published_html
assert 'apiGet("./data/forecast-details.json")' in published_html
assert 'apiGet("/api/dashboard")' not in published_html
assert 'apiGet("/api/forecast-details")' not in published_html
assert "showOrders: true" in published_html
assert "点击查看订单号" in published_html

dashboard_payload = json.loads(dashboard_json.read_text(encoding="utf-8"))
forecast_payload = json.loads(forecast_json.read_text(encoding="utf-8"))

for key in ["sync", "summary", "owners", "carry", "orders"]:
    assert key in dashboard_payload, f"dashboard.json missing {key}"
assert "rows" in forecast_payload, "forecast-details.json missing rows"
assert isinstance(dashboard_payload["carry"], list), "dashboard carry should be a list"
assert isinstance(dashboard_payload["orders"], list), "dashboard orders should be a list"
assert isinstance(forecast_payload["rows"], list), "forecast rows should be a list"
assert dashboard_payload.get("privacy_mode") == "public_sanitized"
assert dashboard_json.stat().st_size < 50 * 1024 * 1024, "dashboard.json should stay below GitHub's 50MB recommendation"

carry_forbidden_keys = {"id", "employee_user_id", "owner_raw"}
order_forbidden_keys = {"employee_user_id", "owner_raw", "customer_tags", "attribution_reason"}
for row in dashboard_payload["carry"]:
    assert not carry_forbidden_keys.intersection(row), f"carry row exposes sensitive keys: {carry_forbidden_keys.intersection(row)}"
    assert str(row.get("union_id", "")).startswith("public_user_") or row.get("union_id", "") == ""
    assert row.get("customer_tags", "") in ("", "螳螂到课")

for row in dashboard_payload["orders"]:
    assert not order_forbidden_keys.intersection(row), f"order row exposes sensitive keys: {order_forbidden_keys.intersection(row)}"
    assert str(row.get("order_id", "")).startswith("public_order_")
    assert row.get("order_no", ""), "order_no should be kept for review drilldown"
    assert str(row.get("wxid", "")).startswith("public_user_") or row.get("wxid", "") == ""
    assert str(row.get("user_id", "")).startswith("public_user_") or row.get("user_id", "") == ""
    assert row.get("product_name", "") == ""

raw_markers = [
    "1-挂图承接【私域部】",
    "2-公号-引流",
    "2-企微-回捞",
    "2-企微-询课",
    "2-有赞-下单",
    "2-视频号-下单",
]
for row in dashboard_payload["carry"]:
    tags = row.get("customer_tags", "")
    for marker in raw_markers:
        assert marker not in tags, f"carry customer_tags exposes raw customer tag marker: {marker}"

serialized_dashboard = dashboard_json.read_text(encoding="utf-8")
for marker in ["D:\\", "codex agent", "data/source", "employee_user_id", "owner_raw"]:
    assert marker not in serialized_dashboard, f"dashboard.json exposes local or internal marker: {marker}"

print("static publish build verification passed")
