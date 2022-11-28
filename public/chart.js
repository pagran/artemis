let currentPlot = null;

const chartEl = document.getElementById('chart')
const pallete = ["#003f5c", "#374c80", "#7a5195", "#bc5090", "#ef5675", "#ff764a", "#ffa600"]

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

  const series = [{}]
  const data = [raw.timestamps]

  for (const name of raw.groups[group]) {
    series.push({
      label: name,
      show: true,
      stroke: pallete[series.length],
      width: 1 / devicePixelRatio,
    })
    data.push(raw.values[name])
  }

  const isDark = isDarkMode()
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