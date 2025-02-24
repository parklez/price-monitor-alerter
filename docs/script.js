async function fetchCsv() {
  const response = await fetch("https://raw.githubusercontent.com/parklez/price-monitor-alerter/refs/heads/master/prices.csv");
  const csvText = await response.text();
  return csvText;
}

function parseCsv(csvText) {
  return Papa.parse(csvText, { header: true }).data;
}

function getAllTimeStamps(parsedData) {
  return parsedData.map((entry) => entry.time);
}

function extractDatasets(parsedData) {
  const datasets = {};

  for (let i = 0; i < parsedData.length; i++) {
    const entry = parsedData[i];
    const product = entry.product;
    const price = entry.price;

    // if entry is an empty new line, skip it
    if (!product || !price) {
      continue
    }

    // If it's the first time this product is encountered, create an empty array
    if (!datasets[product]) {
      datasets[product] = [];
    }
    // If it's the first timestamp ever, add the first price to the array and continue
    if (i == 0) {
      datasets[product].push(price);
      continue
    }

    // current size of the array for this product
    const pricesArraySize = datasets[product].length;

    // get the last value, in case it's the first entry - mark as null
    const lastValue = datasets[product][pricesArraySize - 1] || null;

    // fulfill the gap between the lenght of the current product and the current i - 1
    if (pricesArraySize < i - 1) {
      for (let j = pricesArraySize; j < i - 1; j++) {
        datasets[product].push(lastValue);
      }
    }

    datasets[product].push(price);
  }
  // return datasets in the following format:
  // [{product: [price1, price2, price3, ...]}, {product: [price1, price2, price3, ...]}, ...]
  return Object.keys(datasets).map((product) => {
    return {
      label: product,
      data: datasets[product],
    };
  });

}

function generateTable(parsedData) {
  const table = document.getElementById("historical-data");
  const tableBody = document.createElement("tbody");

  for (let i = parsedData.length - 1; i >= 0; i--) {
    const entry = parsedData[i];
    const product = entry.product;
    const time = entry.time;
    const price = Number(entry.price).toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });

    // if entry is an empty new line, skip it
    if (!product || !price) {
      continue;
    }

    const row = document.createElement("tr");
    row.innerHTML = `
      <th>${i + 1}</th>
      <td>${product}</td>
      <td>${time}</td>
      <td>R$: ${price}</td>
    `;

    tableBody.appendChild(row);
  }

  table.appendChild(tableBody);
}

async function main() {
  const csvText =  await fetchCsv();
  const parsedData = parseCsv(csvText);
  const timestamps = getAllTimeStamps(parsedData);
  const datasets = extractDatasets(parsedData, timestamps);

  const data = {
    labels: timestamps,
    datasets: datasets,
  };

  new Chart(document.getElementById("acquisitions"), {
    type: "line",
    data: data,
    options: {
      plugins: {
        zoom: {
          pan: {
            enabled: true,
            mode: 'x'
          },
          zoom: {
            wheel: {
              enabled: true,
            },
            pinch: {
              enabled: true
            },
            drag: {
              enabled: true,
              modifierKey: 'shift'
            },
            mode: 'x'
          }
        }
      }
    }
  });

  generateTable(parsedData);
}

document.addEventListener('keydown', (ev) => {
  if (ev.key !== 'Shift') {
    return;
  }
  const element = document.querySelector(
      '[data-keyboard-key="SHIFT"]'
  );
  element.classList.add('active');
});

document.addEventListener('keyup', (ev) => {
  if (ev.key !== 'Shift') {
    return;
  }
  const element = document.querySelector(
      '[data-keyboard-key="SHIFT"]'
  );
  element.classList.remove('active');
});


(async () => {
  await main();
})();
