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
      value: "",
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

const carryDates = datesFromKeys(state.selectedReviewCarryDates, reviewCarryFallbackDate());
const conversionDate = dateFromKey(state.selectedReviewConversionDate, reviewConversionFallbackDate());
const forecast = forecastForDate(carryDates, conversionDate);
const actuals = reviewWindowActuals(carryDates, conversionDate);
const parseOrders = id => Number(String(document.getElementById(id).textContent || "").match(/\\d+/)?.[0] || 0);

const displayedTotal = parseOrders("review-predicted-conversion");
const displayedCurrent = parseOrders("review-current-predicted");
const displayedPast = parseOrders("review-past-predicted");
const actualCurrent = parseOrders("review-current-actual");
const actualPast = parseOrders("review-past-actual");
const actualTotal = parseOrders("review-conv");

if (displayedTotal !== forecast.totalOrders) {
  throw new Error(\`Review predicted conversion mismatch: displayed=\${displayedTotal}, model=\${forecast.totalOrders}\`);
}
if (displayedCurrent !== forecast.currentOrders) {
  throw new Error(\`Review current prediction mismatch: displayed=\${displayedCurrent}, model=\${forecast.currentOrders}\`);
}
const predictedChannelOrders = (forecast.currentRows || []).reduce((sum, row) => sum + row.orders, 0);
if (displayedCurrent !== predictedChannelOrders) {
  throw new Error("Review current prediction must equal channel order sum: displayed=" + displayedCurrent + ", channelSum=" + predictedChannelOrders);
}
if (displayedPast !== forecast.pastOrders) {
  throw new Error(\`Review past prediction mismatch: displayed=\${displayedPast}, model=\${forecast.pastOrders}\`);
}
if (actualCurrent !== actuals.current.total.orders) {
  throw new Error(\`Review current actual mismatch: displayed=\${actualCurrent}, model=\${actuals.current.total.orders}\`);
}
if (actualPast !== actuals.past.total.orders) {
  throw new Error(\`Review past actual mismatch: displayed=\${actualPast}, model=\${actuals.past.total.orders}\`);
}
if (actualTotal !== actuals.total.total.orders) {
  throw new Error(\`Review total actual mismatch: displayed=\${actualTotal}, model=\${actuals.total.total.orders}\`);
}

const windowLabels = actuals.window.days.map(formatDate).join(",");
if (!windowLabels) throw new Error("Review conversion workday window is empty");
if (document.getElementById("review-current-actual-channel").innerHTML.includes("订单号") && !document.getElementById("review-current-actual-channel").innerHTML.includes("点击查看订单号")) {
  throw new Error("Review actual channel order drilldown copy is inconsistent");
}

console.log(JSON.stringify({
  carryDate: carryDateLabel(carryDates),
  conversionDate: formatDate(conversionDate),
  window: windowLabels,
  displayedTotal,
  actualTotal
}, null, 2));
`;

vm.runInNewContext([script, code].join("\n"), context);
