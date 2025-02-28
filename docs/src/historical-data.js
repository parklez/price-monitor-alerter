import { stringfyPrice } from "./utils.js";

function generateTable(parsedData, productsToHide) {
  const table = document.getElementById("historical-data");
  const oldTableBody = table.querySelector("tbody");
  if (oldTableBody) {
    oldTableBody.remove();
  }
  const tableBody = document.createElement("tbody");
  const lastPrices = {};

  for (let i = 0; i < parsedData.length; i++) {
    const entry = parsedData[i];
    const product = entry.product;
    const time = entry.time;
    const price = stringfyPrice(entry.price);

    // if entry is an empty new line, skip it
    if (!product || !price) {
      continue;
    }

    if (productsToHide.includes(product)) {
      continue;
    }

    if (!lastPrices[product]) {
      lastPrices[product] = entry.price;
    }

    const difference = entry.price - lastPrices[product];

    lastPrices[product] = entry.price;

    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${i + 1}</td>
        <td>${product}</td>
        <td>${time}</td>
        <td>R$: ${price}</td>
        <td ${
          difference > 0
            ? 'style="color: var(--price-decrease)"'
            : difference < 0
            ? 'style="color: var(--price-increase)"'
            : ""
        }> ${
      difference > 0 ? "▲ +" : difference < 0 ? "▼ " : ""
    }${stringfyPrice(difference)}</td>
      `;

    tableBody.appendChild(row);
  }

  tableBody.append(...Array.from(tableBody.children).reverse());
  table.appendChild(tableBody);
}

export { generateTable };
