// assets/charts.js
(function () {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  var el = document.getElementById('chart-router');
  if (!el || typeof echarts === 'undefined') return;

  var chart = echarts.init(el, null, { renderer: 'svg' });

  chart.setOption({
    animation: false,
    color: [muted + '99', accent, accent2],
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      backgroundColor: bg2,
      borderColor: rule,
      textStyle: { color: ink, fontSize: 12 },
      valueFormatter: function (v) {
        return (v * 100).toFixed(1) + '%';
      }
    },
    legend: {
      top: 0,
      right: 0,
      itemWidth: 10,
      itemHeight: 10,
      textStyle: { color: muted, fontSize: 11 }
    },
    grid: { left: 52, right: 20, top: 44, bottom: 34 },
    xAxis: {
      type: 'category',
      data: ['意图准确率', '槽位 F1', '澄清准确率'],
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false },
      axisLabel: { color: ink, fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      min: 0.8,
      max: 1,
      interval: 0.05,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLabel: {
        color: muted,
        fontSize: 11,
        formatter: function (v) { return (v * 100).toFixed(0) + '%'; }
      }
    },
    series: [
      {
        name: '规则基线',
        type: 'bar',
        data: [0.94, 0.966, 0.903],
        barMaxWidth: 34,
        itemStyle: { color: muted + '66' }
      },
      {
        name: 'LLM 路由',
        type: 'bar',
        data: [0.98, 0.995, 0.968],
        barMaxWidth: 34,
        itemStyle: { color: accent }
      },
      {
        name: '门禁线',
        type: 'line',
        data: [0.95, 0.95, 0.9],
        symbol: 'circle',
        symbolSize: 7,
        lineStyle: { color: accent2, width: 2, type: 'dashed' },
        itemStyle: { color: accent2 },
        label: {
          show: true,
          position: 'top',
          color: accent2,
          fontSize: 10,
          formatter: function (p) { return (p.value * 100).toFixed(0) + '%'; }
        }
      }
    ]
  });

  window.addEventListener('resize', function () { chart.resize(); });
})();
