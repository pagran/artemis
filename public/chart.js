let currentPlots = [];

const chartContainer = document.getElementById('chart')
const chartType = document.getElementById('chart-type')
const multiselect = document.getElementById('multiselect')

const palleteDark = ["#8a3ffc", "#33b1ff", "#007d79", "#ff7eb6", "#fa4d56", "#fff1f1", "#6fdc8c"]
const palleteLight = ["#6929c4", "#1192e8", "#005d5d", "#9f1853", "#fa4d56", "#570408", "#198038"]
const chartHeightPad = 50
const syncPlot = uPlot.sync('artemis')

function isDarkMode() {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
}

// TODO: Rewrite this
function getHeight() {
  return document.documentElement.clientHeight - document.body.offsetHeight - chartHeightPad
}

function render(raw, groups) {
  for (const currentPlot of currentPlots) {
    currentPlot.destroy()
  }
  currentPlots.length = 0
  chartContainer.innerHTML = ''

  const isDark = isDarkMode()
  const height = Math.floor(getHeight() / groups.length - chartHeightPad / groups.length)

  const cursorOpts = {
    lock: true,
    focus: {
      prox: 16,
    },
    sync: {
      key: syncPlot.key,
      setSeries: true
    },
  };


  for (const group of groups) {
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
      cursor: cursorOpts,
      width: chartContainer.offsetWidth,
      axes: [axe, axe],
      height,
      series
    }

    const chartEl = document.createElement('div')
    chartContainer.appendChild(chartEl)

    const currentPlot = new uPlot(opts, data, chartEl)
    currentPlots.push(currentPlot)
  }
}
function init(data) {
  document.getElementById('update-time').textContent = new Date(data.last_time * 1000).toLocaleString()

  chartType.options.remove(0)
  for (let [value, desc] of Object.entries(data.groups_desc)) {
    chartType.options.add(new Option(desc, value))
  }
  chartType.options[0].selected = true

  const rerender = () => render(data, [...chartType.selectedOptions].map(opt => opt.value))

  chartType.addEventListener('change', rerender)
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', rerender)

  let resizeTimeout = null;
  window.addEventListener('resize', function () {
    clearInterval(resizeTimeout);
    resizeTimeout = setTimeout(rerender, 250);
  })

  multiselect.addEventListener('change', () => {
    if (multiselect.checked === true) {
      chartType.setAttribute('multiple', 'multiple')
    } else {
      chartType.removeAttribute('multiple')
    }
    rerender()
  })

  rerender()
}

fetch('data.json')
  .then(resp => resp.json())
  .then(init)
  .catch(err => console.error('data load failed', err))