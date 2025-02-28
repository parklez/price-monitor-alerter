import { generateTable } from "./historical-data.js";

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
      continue;
    }

    // If it's the first time this product is encountered, create an empty array
    if (!datasets[product]) {
      datasets[product] = [];
    }
    // If it's the first timestamp ever, add the first price to the array and continue
    if (i == 0) {
      datasets[product].push(price);
      continue;
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

async function generateChart(parsedData) {
  const timestamps = getAllTimeStamps(parsedData);
  const datasets = extractDatasets(parsedData, timestamps);

  const data = {
    labels: timestamps,
    datasets: datasets,
  };

  const chart = await new Chart(document.getElementById("chart"), {
    type: "line",
    data: data,
    options: {
      // https://stackoverflow.com/questions/33385398/how-to-fix-blurry-chart-issue-in-chart-js
      devicePixelRatio: 4,
      plugins: {
        legend: {
          labels: {
            color: "hsl(221deg,14%,71%)",
            font: {
              size: 16,
            },
          },
          // https://www.chartjs.org/docs/latest/configuration/legend.html#custom-on-click-actions
          onClick: (_, legendItem, legend) => {
            const index = legendItem.datasetIndex;
            const ci = legend.chart;

            if (ci.isDatasetVisible(index)) {
              ci.hide(index);
              legendItem.hidden = true;
            } else {
              ci.show(index);
              legendItem.hidden = false;
            }
            const hiddenLabels = ci.data.datasets
              .filter((_, i) => !ci.isDatasetVisible(i))
              .map((dataset) => dataset.label);
            generateTable(parsedData, hiddenLabels);
          },
        },
        zoom: {
          pan: {
            enabled: true,
            mode: "x",
          },
          zoom: {
            wheel: {
              enabled: true,
            },
            pinch: {
              enabled: true,
            },
            drag: {
              enabled: true,
              modifierKey: "shift",
            },
            mode: "x",
          },
        },
      },
      scales: {
        x: {
          grid: {
            color: "rgb(67, 67, 67)",
          },
        },
        y: {
          grid: {
            color: "rgb(67, 67, 67)",
          },
        },
      },
    },
  });

  // Sets default zoom + panning all the way to right
  chart.zoom(1.8);
  chart.pan(
    {
      x: Number.MIN_SAFE_INTEGER,
    },
    undefined,
    "show"
  );
}

export { generateChart };
