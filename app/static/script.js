let trafficChart, statusChart;

document.addEventListener('DOMContentLoaded', () => {
    // Init Flatpickr
    flatpickr("#date-range", {
        mode: "range",
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        defaultDate: [new Date(Date.now() - 24 * 60 * 60 * 1000), new Date()],
        onClose: function (selectedDates, dateStr, instance) {
            fetchData();
        }
    });

    document.getElementById('refresh-btn').addEventListener('click', fetchData);

    initCharts();
    fetchData();
    setInterval(fetchData, 5000); // Auto refresh
});

function initCharts() {
    const ctx1 = document.getElementById('trafficChart').getContext('2d');
    trafficChart = new Chart(ctx1, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Requests', data: [], borderColor: '#38bdf8', tension: 0.4, fill: true, backgroundColor: 'rgba(56, 189, 248, 0.1)' }] },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(255,255,255,0.05)' } } } }
    });

    const ctx2 = document.getElementById('statusChart').getContext('2d');
    statusChart = new Chart(ctx2, {
        type: 'doughnut',
        data: { labels: [], datasets: [{ data: [], backgroundColor: ['#22c55e', '#f43f5e', '#eab308'] }] },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } }, cutout: '70%' }
    });
}

async function fetchData() {
    const range = document.getElementById('date-range')._flatpickr.selectedDates;
    let url = '/api/stats';
    if (range.length === 2) {
        url += `?start=${range[0].toISOString()}&end=${range[1].toISOString()}`;
    }

    const res = await fetch(url);
    const data = await res.json();
    updateStats(data);
    updateCharts(data);

    const logsRes = await fetch('/api/logs?limit=20');
    const logs = await logsRes.json();
    updateLogs(logs);
}

function updateStats(data) {
    document.getElementById('total-req').innerText = data.length;

    const avgDur = data.length ? (data.reduce((acc, curr) => acc + curr.duration, 0) / data.length).toFixed(2) : 0;
    document.getElementById('avg-dur').innerText = `${avgDur}ms`;

    const errors = data.filter(d => d.status >= 400).length;
    const errorRate = data.length ? ((errors / data.length) * 100).toFixed(1) : 0;
    document.getElementById('error-rate').innerText = `${errorRate}%`;
}

function updateCharts(data) {
    // Process data for charts
    // Traffic: Bucket by minute
    const buckets = {};
    data.forEach(d => {
        const t = new Date(d.timestamp);
        const key = `${t.getHours()}:${t.getMinutes() < 10 ? '0' : ''}${t.getMinutes()}`;
        buckets[key] = (buckets[key] || 0) + 1;
    });

    // Sort keys
    const sortedKeys = Object.keys(buckets).sort();

    trafficChart.data.labels = sortedKeys;
    trafficChart.data.datasets[0].data = sortedKeys.map(k => buckets[k]);
    trafficChart.update();

    // Status
    const statuses = {};
    data.forEach(d => {
        const s = d.status;
        statuses[s] = (statuses[s] || 0) + 1;
    });

    statusChart.data.labels = Object.keys(statuses);
    statusChart.data.datasets[0].data = Object.values(statuses);
    statusChart.update();
}

function updateLogs(logs) {
    const tbody = document.getElementById('logs-body');
    tbody.innerHTML = logs.map(log => `
        <tr>
            <td>${new Date(log.timestamp).toLocaleTimeString()}</td>
            <td>${log.service}</td>
            <td>${log.method}</td>
            <td>${log.path}</td>
            <td class="status-${log.status >= 400 ? '400' : '200'}">${log.status}</td>
            <td>${log.duration.toFixed(2)}ms</td>
        </tr>
    `).join('');
}
