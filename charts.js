/**
 * 图表管理工具
 */
class ChartManager {
    constructor() {
        this.charts = new Map();
    }
    
    initChart(chartId, options = {}) {
        const chartDom = document.getElementById(chartId);
        if (!chartDom) {
            console.error('图表容器不存在:', chartId);
            return null;
        }
        
        const chart = echarts.init(chartDom);
        chart.setOption(options);
        this.charts.set(chartId, chart);
        
        window.addEventListener('resize', () => {
            chart.resize();
        });
        
        return chart;
    }
    
    createSensorTrendChart(chartId, sensorData) {
        const option = {
            title: {
                text: '传感器数据趋势',
                left: 'center',
                textStyle: { color: 'var(--text-primary)' }
            },
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'var(--bg-primary)',
                borderColor: 'var(--border-light)',
                textStyle: { color: 'var(--text-primary)' }
            },
            xAxis: {
                type: 'time',
                axisLine: { lineStyle: { color: 'var(--border-light)' } },
                axisLabel: { color: 'var(--text-secondary)' }
            },
            yAxis: {
                type: 'value',
                axisLine: { lineStyle: { color: 'var(--border-light)' } },
                axisLabel: { color: 'var(--text-secondary)' },
                splitLine: { lineStyle: { color: 'var(--border-light)', opacity: 0.3 } }
            },
            series: []
        };
        
        if (sensorData && Object.keys(sensorData).length > 0) {
            Object.entries(sensorData).forEach(([sensorId, data]) => {
                if (data.history && data.history.length > 0) {
                    option.series.push({
                        name: data.name,
                        type: 'line',
                        data: data.history.map(item => [item.timestamp, item.value]),
                        smooth: true
                    });
                }
            });
        }
        
        return this.initChart(chartId, option);
    }
    
    resizeAll() {
        this.charts.forEach(chart => chart.resize());
    }
}

window.ChartManager = ChartManager;
