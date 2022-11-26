let currentPlot = null;

const chartEl = document.getElementById('chart')
const pallete = ["#b30000", "#7c1158", "#4421af", "#1a53ff", "#0d88e6", "#00b7c7", "#5ad45a", "#8be04e", "#ebdc78"]

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


  const opts = {
    id: group,
    width: chartEl.offsetWidth,
    height: getHeight(),
    series
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

  chartType.addEventListener('change', function () {
    render(data, this.value)
  })

  render(data, chartType.value)

  let resizeTimeout = null;
  window.addEventListener('resize', function () {
    clearInterval(resizeTimeout);
    resizeTimeout = setTimeout(() => render(data, chartType.value), 250);
  })
}

fetch('data.json')
  .then(resp => resp.json())
  .then(init)
  .catch(err => console.error('data load failed', err))