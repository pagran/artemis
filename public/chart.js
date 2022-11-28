let currentPlot = null;

const chartEl = document.getElementById('chart')
const palleteDark = ["#8a3ffc", "#33b1ff", "#007d79", "#ff7eb6", "#fa4d56", "#fff1f1", "#6fdc8c"]
const palleteLight = ["#6929c4", "#1192e8", "#005d5d", "#9f1853", "#fa4d56", "#570408", "#198038"]

function isDarkMode() {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
}

// TODO: Rewrite this
function getHeight() {
  return document.documentElement.clientHeight - document.body.offsetHeight - 50
}

function render(raw, group) {
  if (currentPlot !== null) {
    currentPlot.destroy()
  }
  const isDark = isDarkMode()

  const series = [{}]
  const data = [raw.timestamps]

  const pallete = isDark ? palleteDark : palleteLight
  for (const name of raw.groups[group]) {
    series.push({
      label: name,
      show: true,
      stroke: pallete[series.length],
      width: 1 / devicePixelRatio,
    })
    data.push(raw.values[name])
  }


  const axe = {
    stroke: isDark ? "#c7d0d9" : null,
    grid: {
      width: 1 / devicePixelRatio,
      stroke: isDark ? "#2c3235" : null,
    },
  }
  const opts = {
    id: group,
    width: chartEl.offsetWidth,
    height: getHeight(),
    series,
    axes: [axe, axe],
  }

  currentPlot = new uPlot(opts, data, chartEl)
}

function init(data) {
  document.getElementById('update-time').textContent = new Date(data.last_time * 1000).toLocaleString()

  const chartType = document.getElementById('chart-type')
  chartType.options.remove(0)
  for (let [value, desc] of Object.entries(data.groups_desc)) {
    chartType.options.add(new Option(desc, value))
  }

  const rerender = () => render(data, chartType.value)

  chartType.addEventListener('change', rerender)
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', rerender)

  let resizeTimeout = null;
  window.addEventListener('resize', function () {
    clearInterval(resizeTimeout);
    resizeTimeout = setTimeout(rerender, 250);
  })

  rerender()
}

fetch('data.json')
  .then(resp => resp.json())
  .then(init)
  .catch(err => console.error('data load failed', err))