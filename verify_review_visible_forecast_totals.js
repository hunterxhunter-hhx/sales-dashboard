const fs = require("fs");
const vm = require("vm");

const html = fs.readFileSync("dashboard-prototype.html", "utf8");
const script = html.match(/<script>\s*([\s\S]*?)\s*<\/script>/)[1];
const payload = JSON.parse(fs.readFileSync("dist/data/dashboard.json", "utf8"));
const forecastDetails = JSON.parse(fs.readFileSync("dist/data/forecast-details.json", "utf8"));

const nodes = new Map();
function nodeFor(id = "") {
  if (!nodes.has(id)) {
    nodes.set(id, {
      id,
      textContent: "",
      innerHTML: "",
      style: {},
      dataset: {},
      addEventListener() {},
      classList: { toggle() {} },
      querySelector() { return null; },
      querySelectorAll() { return []; }
    });
  }
  return nodes.get(id);
}

const context = {
  console,
  payload,
  forecastDetails,
  window: { addEventListener() {} },
  document: {
    getElementById(id) { return nodeFor(id); },
    querySelector() { return null; },
  },
  echarts: { init() { return { resize() {}, setOption() {} }; } },
};

const code = `
normalizePayload(payload);
normalizeForecastDetails(forecastDetails);
renderReview();
const target = previousOrderDate(latestCarryDate() || latestOrderDate());
const actualCarry = actualCarryDay(target);
const model = historicalPredictionModel(target);
const predictedChannelRows = channelPredictionRows(actualCarry, model);
const visibleRows = predictedChannelRows.filter(row => !isTailChannel(row.name));
const visibleOrders = visibleRows.reduce((sum, row) => sum + row.orders, 0);
const visibleGmv = visibleRows.reduce((sum, row) => sum + row.gmv, 0);
const displayedOrders = Number(String(document.getElementById("review-predicted-conversion").textContent || "").replace(/[^0-9.-]/g, "")) || 0;
const displayedGmv = Number(String(document.getElementById("review-predicted-gmv").textContent || "").replace(/[^0-9.-]/g, "")) || 0;
const predictedHtml = document.getElementById("review-predict-lines").innerHTML;
if (displayedOrders !== visibleOrders) {
  throw new Error(\`Review predicted conversion mismatch: displayed=\${displayedOrders}, visible channel orders=\${visibleOrders}\`);
}
if (displayedGmv !== visibleGmv) {
  throw new Error(\`Review predicted GMV mismatch: displayed=\${displayedGmv}, visible channel GMV=\${visibleGmv}\`);
}
if (/缺失渠道|冲突渠道|待补录|待归因/.test(predictedHtml)) {
  throw new Error("Review predicted lines should hide tail channels");
}
console.log(JSON.stringify({
  target: formatDate(target),
  displayedOrders,
  visibleOrders,
  displayedGmv,
  visibleGmv
}, null, 2));
`;

vm.runInNewContext([script, code].join("\n"), context);
