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
    querySelector(selector) {
      if (selector === ".donut") return nodeFor("donut");
      return null;
    },
  },
  echarts: { init() { return { resize() {}, setOption() {} }; } },
};

const code = `
normalizePayload(payload);
normalizeForecastDetails(forecastDetails);
renderToday();

const carryDate = dateFromKey(state.selectedTodayCarryDate, todayCarryFallbackDate());
const conversionDate = dateFromKey(state.selectedTodayConversionDate, todayConversionFallbackDate());
const forecast = forecastForDate(carryDate, conversionDate);
const parseOrders = id => Number(String(document.getElementById(id).textContent || "").match(/\\d+/)?.[0] || 0);
const currentOrders = parseOrders("today-live-predicted-gmv");
const pastOrders = parseOrders("today-chase-predicted-gmv");

if (currentOrders !== forecast.currentOrders) {
  throw new Error(\`Current forecast card mismatch: card=\${currentOrders}, model=\${forecast.currentOrders}\`);
}
if (pastOrders !== forecast.pastOrders) {
  throw new Error(\`Past forecast card mismatch: card=\${pastOrders}, model=\${forecast.pastOrders}\`);
}

const saturdayWindow = businessDayWindow(new Date(2026, 7, 8), 3);
const saturdayLabels = saturdayWindow.days.map(formatDate).join(",");
if (saturdayLabels !== "2026-08-10,2026-08-11,2026-08-12") {
  throw new Error(\`Weekend conversion date should move to next workday window, got \${saturdayLabels}\`);
}

const channelRows = forecast.currentRows || [];
for (const row of channelRows) {
  const rates = dayRateForChannel(row.name);
  if (!rates) throw new Error(\`Forecast row without channel rate: \${row.name}\`);
  const expected = Math.round(row.carry * rates.day1);
  if (row.orders !== expected) {
    throw new Error(\`Channel day1 rate mismatch for \${row.name}: row=\${row.orders}, expected=\${expected}\`);
  }
}

console.log(JSON.stringify({
  carryDate: formatDate(carryDate),
  conversionDate: formatDate(conversionDate),
  currentOrders,
  pastOrders,
  channelRows: channelRows.length
}, null, 2));
`;

vm.runInNewContext([script, code].join("\n"), context);
