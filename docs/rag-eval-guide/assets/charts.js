(function () {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg = style.getPropertyValue('--bg').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var fontFamily = getComputedStyle(document.body).fontFamily;

  // --- Mermaid diagrams ---
  if (window.mermaid) {
    window.mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'loose',
      theme: 'base',
      themeVariables: {
        primaryColor: bg2,
        primaryTextColor: ink,
        primaryBorderColor: accent,
        lineColor: muted,
        secondaryColor: bg2,
        tertiaryColor: bg,
        background: bg,
        mainBkg: bg2,
        nodeBorder: accent,
        clusterBkg: bg,
        clusterBorder: rule,
        titleColor: ink,
        edgeLabelBackground: bg,
        fontFamily: fontFamily
      }
    });
    window.mermaid.run({ querySelector: '.mermaid' }).catch(function () {
      // 渲染失败时保留源码，避免整页脚本中断
    });
  }

  // --- Chart: router baseline vs gate ---
  var el = document.getElementById('chart-router');
  if (el && window.echarts) {
    var chart = window.echarts.init(el, null, { renderer: 'svg' });

    chart.setOption({
      animation: false,
      textStyle: { fontFamily: fontFamily, color: ink },
      tooltip: {
        trigger: 'axis',
        appendToBody: true,
        backgroundColor: bg,
        borderColor: rule,
        textStyle: { color: ink, fontFamily: fontFamily },
        valueFormatter: function (value) {
          return (value * 100).toFixed(1) + '%';
        }
      },
      legend: {
        top: 0,
        left: 0,
        itemWidth: 12,
        itemHeight: 8,
        textStyle: { color: muted, fontSize: 12, fontFamily: fontFamily }
      },
      grid: { left: 46, right: 18, top: 58, bottom: 42 },
      xAxis: {
        type: 'category',
        data: ['意图准确率', '槽位 F1', '澄清准确率'],
        axisTick: { show: false },
        axisLine: { lineStyle: { color: rule } },
        axisLabel: { color: muted, fontSize: 12, fontFamily: fontFamily }
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 1.08,
        interval: 0.2,
        axisLabel: {
          color: muted,
          fontSize: 11,
          formatter: function (value) { return Math.round(value * 100) + '%'; }
        },
        splitLine: { lineStyle: { color: rule, type: 'dashed' } }
      },
      series: [
        {
          name: '规则基线',
          type: 'bar',
          data: [0.94, 0.966, 0.903],
          barMaxWidth: 34,
          itemStyle: { color: accent, borderRadius: [3, 3, 0, 0] },
          label: {
            show: true,
            position: 'top',
            color: ink,
            fontSize: 11,
            formatter: function (p) { return (p.value * 100).toFixed(1) + '%'; }
          }
        },
        {
          name: 'LLM 基线',
          type: 'bar',
          data: [0.98, 0.995, 0.968],
          barMaxWidth: 34,
          itemStyle: { color: accent2, borderRadius: [3, 3, 0, 0] },
          label: {
            show: true,
            position: 'top',
            color: ink,
            fontSize: 11,
            formatter: function (p) { return (p.value * 100).toFixed(1) + '%'; }
          }
        },
        {
          name: '门禁线',
          type: 'line',
          data: [0.90, 0.85, 0.85],
          symbol: 'diamond',
          symbolSize: 9,
          lineStyle: { color: muted, type: 'dashed', width: 1.5 },
          itemStyle: { color: muted },
          label: {
            show: false
          }
        }
      ]
    });

    window.addEventListener('resize', function () { chart.resize(); });
  }
})();
