async function fetchCsv() {
  const response = await fetch(
    "https://raw.githubusercontent.com/parklez/price-monitor-alerter/refs/heads/master/prices.csv"
  );
  const csvText = await response.text();
  return csvText;
}

function parseCsv(csvText) {
  return Papa.parse(csvText, { header: true }).data;
}

function stringfyPrice(price) {
  return Number(price).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/export#description
export { fetchCsv, parseCsv, stringfyPrice };