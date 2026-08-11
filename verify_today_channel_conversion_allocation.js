const fs = require("fs");
const vm = require("vm");

const html = fs.readFileSync("dashboard-prototype.html", "utf8");
const script = html.match(/<script>\s*([\s\S]*?)\s*<\/script>/)[1];
const payload = JSON.parse(fs.readFileSync("dist/data/dashboard.json", "utf8"));
const forecastDetails = JSON.parse(fs.readFileSync("dist/data/forecast-details.json", "utf8"));

const context = {
  console,
  payload,
  forecastDetails,
  window: { addEventListener() {} },
  document: {
    getElementById() {
      return {
        textContent: "",
        innerHTML: "",
        style: {},
        dataset: {},
        addEventListener() {},
        classList: { toggle() {} },
        querySelector() { return null; },
        querySelectorAll() { return []; }
      };
    },
    querySelector() { return null; },
  },
  echarts: { init() { return { resize() {}, setOption() {} }; } },
};

const testCode = [
  "normalizePayload(payload);",
  "normalizeForecastDetails(forecastDetails);",
  "const target = latestCarryDate() || latestOrderDate();",
  "const actualCarry = actualCarryDay(target);",
  "const model = historicalPredictionModel(target);",
  "const rows = channelPredictionRows(actualCarry, model);",
  "const fixedChannels = [",
  '  "2-企微-询课",',
  '  "2-有赞-下单",',
  '  "2-视频号-下单",',
  '  "2-企微-回捞",',
  '  "2-公号-引流",',
  '  "1-挂图承接【私域部】",',
  "];",
  "const fixedRows = rows.filter(row => fixedChannels.includes(row.name));",
  "const fixedTotal = fixedRows.reduce((sum, row) => sum + row.orders, 0);",
  "const fixedExpected = fixedChannels.reduce((sum, name) => sum + (actualCarry.channels.get(name)?.carry || 0) * CHANNEL_CONVERSION_RATE[name], 0);",
  "const roundedExpected = Math.round(fixedExpected);",
  "if (roundedExpected > 0) {",
  "  if (fixedTotal !== roundedExpected) {",
  "    throw new Error(`Fixed channel total mismatch: got ${fixedTotal}, expected ${roundedExpected}`);",
  "  }",
  "  if (fixedTotal <= 0) {",
  "    throw new Error(`Fixed channel total should not be zero when rounded expected is ${roundedExpected}`);",
  "  }",
  "}",
  "console.log(JSON.stringify({",
  "  target: formatDate(target),",
  "  fixedExpected,",
  "  roundedExpected,",
  "  fixedTotal,",
  "  rows: fixedRows.map(row => ({ name: row.name, carry: row.carry, orders: row.orders, gmv: row.gmv }))",
  "}, null, 2));",
].join("\n");

vm.runInNewContext([script, testCode].join("\n"), context);
