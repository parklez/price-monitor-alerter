import "./keyboard.js";
import { fetchCsv, parseCsv } from "./utils.js";
import { generateTable } from "./historical-data.js";
import { generateChart } from "./line-chart.js";

async function main() {
  const csvText = await fetchCsv();
  const parsedData = parseCsv(csvText);

  generateChart(parsedData);
  generateTable(parsedData, []);
}

(async () => {
  await main();
})();
