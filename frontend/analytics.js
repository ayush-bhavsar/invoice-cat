// =========================================================================
// Analytics Dashboard — analytics.js
// =========================================================================

// --- Global State ---
let analyticsData = null;
let chartInstances = {};
let currentSortCol = null;
let currentSortAsc = true;

// --- Color Palette ---
const COLORS = [
    '#06b6d4', '#8b5cf6', '#f472b6', '#34d399', '#fbbf24',
    '#60a5fa', '#fb923c', '#a78bfa', '#38bdf8', '#f87171',
    '#4ade80', '#e879f9'
];

const COLORS_ALPHA = COLORS.map(c => c + '33');

// --- Chart.js Global Defaults ---
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.legend.labels.padding = 15;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.9)';
Chart.defaults.plugins.tooltip.titleColor = '#f8fafc';
Chart.defaults.plugins.tooltip.bodyColor = '#94a3b8';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.1)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.cornerRadius = 12;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.scale.grid = { color: 'rgba(255,255,255,0.06)' };
Chart.defaults.scale.border = { color: 'rgba(255,255,255,0.06)' };

// =========================================================================
// INIT
// =========================================================================
document.addEventListener('DOMContentLoaded', () => {
    loadBatchList();
    setupCSVUpload();
    setupPDFExport();
    setupTableControls();

    // Check URL params for auto-load
    const params = new URLSearchParams(window.location.search);
    const batchId = params.get('batch_id');

    if (batchId) {
        document.getElementById('batch-selector').value = batchId;
        loadAnalytics(batchId);
    } else {
        loadAnalytics('main');
    }
});

// =========================================================================
// DATA LOADING
// =========================================================================
async function loadBatchList() {
    try {
        const res = await fetch('/api/batch-list');
        const batches = await res.json();
        const selector = document.getElementById('batch-selector');
        selector.innerHTML = '';

        batches.forEach(b => {
            const opt = document.createElement('option');
            opt.value = b.id;
            opt.textContent = b.name;
            selector.appendChild(opt);
        });

        selector.addEventListener('change', () => {
            loadAnalytics(selector.value);
        });
    } catch (e) {
        console.error('Failed to load batch list:', e);
    }
}

async function loadAnalytics(batchId) {
    const loader = document.getElementById('analytics-loader');
    const dashboard = document.getElementById('dashboard-content');
    const csvUpload = document.getElementById('csv-upload-zone');

    loader.classList.remove('hidden');
    dashboard.classList.add('hidden');
    csvUpload.classList.add('hidden');

    try {
        const res = await fetch(`/api/analytics?batch_id=${batchId}`);

        if (!res.ok) {
            throw new Error('No data');
        }

        const data = await res.json();

        if (data.error) {
            throw new Error(data.error);
        }

        analyticsData = data;
        loader.classList.add('hidden');
        dashboard.classList.remove('hidden');
        renderDashboard(data);
    } catch (e) {
        console.warn('No analytics data available:', e.message);
        loader.classList.add('hidden');
        csvUpload.classList.remove('hidden');
    }
}

// =========================================================================
// CSV UPLOAD
// =========================================================================
function setupCSVUpload() {
    const dropZone = document.getElementById('csv-drop-zone');
    const fileInput = document.getElementById('csv-file-input');
    const browseLink = document.getElementById('csv-browse-link');

    if (!dropZone) return;

    browseLink.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary-cyan)';
        dropZone.style.transform = 'scale(1.01)';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--glass-border)';
        dropZone.style.transform = 'scale(1)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--glass-border)';
        dropZone.style.transform = 'scale(1)';
        const files = e.dataTransfer.files;
        if (files.length && files[0].name.endsWith('.csv')) {
            uploadCSVFile(files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            uploadCSVFile(fileInput.files[0]);
        }
    });
}

async function uploadCSVFile(file) {
    const loader = document.getElementById('analytics-loader');
    const csvUpload = document.getElementById('csv-upload-zone');

    csvUpload.classList.add('hidden');
    loader.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('/api/upload-csv', {
            method: 'POST',
            body: formData
        });
        const result = await res.json();

        if (result.batch_id) {
            // Update selector
            const selector = document.getElementById('batch-selector');
            const opt = document.createElement('option');
            opt.value = result.batch_id;
            opt.textContent = `Uploaded: ${file.name}`;
            selector.appendChild(opt);
            selector.value = result.batch_id;

            loadAnalytics(result.batch_id);
        }
    } catch (e) {
        console.error('CSV upload failed:', e);
        loader.classList.add('hidden');
        csvUpload.classList.remove('hidden');
    }
}

// =========================================================================
// RENDER ALL DASHBOARD COMPONENTS
// =========================================================================
function renderDashboard(data) {
    renderKPIs(data.summary);
    renderCategoryDistribution(data.category_distribution);
    renderCategorySpend(data.category_spend);
    renderMonthlyTrend(data.monthly_trends);
    renderCategoryTrend(data.category_trend);
    renderAmountDistribution(data.amount_distribution);
    renderTopSellers(data.top_sellers);
    renderTopClients(data.top_clients);
    renderIBANCountries(data.iban_countries);
    renderCompliance(data.missing_data);
    renderOutliers(data.outliers);
    renderDataTable(data.raw_data);
    populateCategoryFilter(data.category_distribution);

    // Trigger fade-in animations
    document.querySelectorAll('.fade-in-up').forEach((el, i) => {
        el.style.animationDelay = `${i * 0.08}s`;
        el.classList.add('visible');
    });
}

// =========================================================================
// KPI CARDS
// =========================================================================
function renderKPIs(summary) {
    animateValue('kpi-total-invoices', summary.total_invoices, false);
    animateValue('kpi-total-spend', summary.total_spend, true);
    animateValue('kpi-avg-invoice', summary.avg_invoice, true);
    animateValue('kpi-max-invoice', summary.max_invoice, true);
    animateValue('kpi-unique-sellers', summary.unique_sellers, false);
    animateValue('kpi-unique-clients', summary.unique_clients, false);
}

function animateValue(elementId, targetValue, isCurrency) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const duration = 1200;
    const start = performance.now();
    const startVal = 0;

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = startVal + (targetValue - startVal) * eased;

        if (isCurrency) {
            el.textContent = '$' + current.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        } else {
            el.textContent = Math.round(current).toLocaleString();
        }

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// =========================================================================
// CHARTS
// =========================================================================

function destroyChart(id) {
    if (chartInstances[id]) {
        chartInstances[id].destroy();
        delete chartInstances[id];
    }
}

// --- Category Distribution (Donut) ---
function renderCategoryDistribution(catData) {
    destroyChart('category-distribution');
    const ctx = document.getElementById('chart-category-distribution');
    if (!ctx || !catData) return;

    const labels = Object.keys(catData);
    const values = Object.values(catData);

    chartInstances['category-distribution'] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS.slice(0, labels.length),
                borderColor: 'rgba(11, 17, 32, 0.8)',
                borderWidth: 3,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        }
    });
}

// --- Category Spend (Horizontal Bar) ---
function renderCategorySpend(catSpend) {
    destroyChart('category-spend');
    const ctx = document.getElementById('chart-category-spend');
    if (!ctx || !catSpend) return;

    const labels = Object.keys(catSpend);
    const values = Object.values(catSpend);

    chartInstances['category-spend'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Total Spend',
                data: values,
                backgroundColor: createGradientBars(ctx, labels.length),
                borderRadius: 8,
                borderSkipped: false,
                barThickness: 30
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (c) => '$ ' + c.raw.toLocaleString()
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        callback: (v) => '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v)
                    }
                }
            }
        }
    });
}

function createGradientBars(ctx, count) {
    return COLORS.slice(0, count);
}

// --- Monthly Spending Trend (Line + Bar Combo) ---
function renderMonthlyTrend(monthlyData) {
    destroyChart('monthly-spend');
    const ctx = document.getElementById('chart-monthly-spend');
    if (!ctx || !monthlyData || !monthlyData.labels) return;

    const canvas = ctx.getContext('2d');
    const gradient = canvas.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(6, 182, 212, 0.3)');
    gradient.addColorStop(1, 'rgba(6, 182, 212, 0.01)');

    chartInstances['monthly-spend'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthlyData.labels,
            datasets: [
                {
                    label: 'Monthly Spend',
                    data: monthlyData.spend,
                    borderColor: '#06b6d4',
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    pointBackgroundColor: '#06b6d4',
                    pointBorderColor: '#0B1120',
                    pointBorderWidth: 3,
                    borderWidth: 3,
                    yAxisID: 'y'
                },
                {
                    label: 'Invoice Count',
                    data: monthlyData.count,
                    type: 'bar',
                    backgroundColor: 'rgba(139, 92, 246, 0.4)',
                    borderColor: '#8b5cf6',
                    borderWidth: 1,
                    borderRadius: 6,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (c) => {
                            if (c.datasetIndex === 0) return 'Spend: $' + c.raw.toLocaleString();
                            return 'Count: ' + c.raw;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: {
                        callback: (v) => '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v)
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// --- Category Trend (Stacked Area) ---
function renderCategoryTrend(catTrend) {
    destroyChart('category-trend');
    const ctx = document.getElementById('chart-category-trend');
    if (!ctx || !catTrend || !catTrend.labels) return;

    const datasets = Object.keys(catTrend.datasets).map((cat, i) => ({
        label: cat,
        data: catTrend.datasets[cat],
        backgroundColor: COLORS_ALPHA[i % COLORS.length],
        borderColor: COLORS[i % COLORS.length],
        borderWidth: 2,
        fill: true,
        tension: 0.4
    }));

    chartInstances['category-trend'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: catTrend.labels,
            datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index' },
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: (c) => c.dataset.label + ': $' + c.raw.toLocaleString()
                    }
                }
            },
            scales: {
                x: { stacked: true },
                y: {
                    stacked: true,
                    ticks: {
                        callback: (v) => '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v)
                    }
                }
            }
        }
    });
}

// --- Amount Distribution (Histogram) ---
function renderAmountDistribution(distData) {
    destroyChart('amount-distribution');
    const ctx = document.getElementById('chart-amount-distribution');
    if (!ctx || !distData || !distData.labels) return;

    chartInstances['amount-distribution'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: distData.labels,
            datasets: [{
                label: 'Invoices',
                data: distData.values,
                backgroundColor: COLORS.slice(0, distData.labels.length),
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// --- Top Sellers (Horizontal Bar) ---
function renderTopSellers(sellerData) {
    destroyChart('top-sellers');
    const ctx = document.getElementById('chart-top-sellers');
    if (!ctx || !sellerData || !sellerData.labels) return;

    chartInstances['top-sellers'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sellerData.labels,
            datasets: [{
                label: 'Revenue',
                data: sellerData.values,
                backgroundColor: 'rgba(6, 182, 212, 0.6)',
                borderColor: '#06b6d4',
                borderWidth: 1,
                borderRadius: 6,
                barThickness: 24
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (c) => '$ ' + c.raw.toLocaleString()
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        callback: (v) => '$' + (v >= 1000 ? (v / 1000).toFixed(1) + 'K' : v)
                    }
                }
            }
        }
    });
}

// --- Top Clients (Horizontal Bar) ---
function renderTopClients(clientData) {
    destroyChart('top-clients');
    const ctx = document.getElementById('chart-top-clients');
    if (!ctx || !clientData || !clientData.labels) return;

    chartInstances['top-clients'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: clientData.labels,
            datasets: [{
                label: 'Billing',
                data: clientData.values,
                backgroundColor: 'rgba(139, 92, 246, 0.6)',
                borderColor: '#8b5cf6',
                borderWidth: 1,
                borderRadius: 6,
                barThickness: 24
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (c) => '$ ' + c.raw.toLocaleString()
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        callback: (v) => '$' + (v >= 1000 ? (v / 1000).toFixed(1) + 'K' : v)
                    }
                }
            }
        }
    });
}

// --- IBAN Country Distribution (Donut) ---
function renderIBANCountries(ibanData) {
    destroyChart('iban-countries');
    const ctx = document.getElementById('chart-iban-countries');
    if (!ctx || !ibanData) return;

    const labels = Object.keys(ibanData);
    const values = Object.values(ibanData);

    if (labels.length === 0) {
        ctx.parentElement.innerHTML = '<p style="text-align:center; color: var(--text-muted); padding: 40px;">No IBAN data available</p>';
        return;
    }

    chartInstances['iban-countries'] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(l => getCountryName(l)),
            datasets: [{
                data: values,
                backgroundColor: COLORS.slice(0, labels.length),
                borderColor: 'rgba(11, 17, 32, 0.8)',
                borderWidth: 3,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function getCountryName(code) {
    const map = {
        'GB': '🇬🇧 United Kingdom',
        'DE': '🇩🇪 Germany',
        'FR': '🇫🇷 France',
        'US': '🇺🇸 United States',
        'IN': '🇮🇳 India',
        'PL': '🇵🇱 Poland',
        'NL': '🇳🇱 Netherlands',
        'ES': '🇪🇸 Spain',
        'IT': '🇮🇹 Italy'
    };
    return map[code] || `🌍 ${code}`;
}

// =========================================================================
// COMPLIANCE / DATA COMPLETENESS
// =========================================================================
function renderCompliance(missing) {
    const grid = document.getElementById('compliance-grid');
    if (!grid || !missing) return;

    const total = missing.total;

    const items = [
        { label: 'Seller Tax ID', missing: missing.missing_seller_tax, icon: 'fa-id-card' },
        { label: 'Client Tax ID', missing: missing.missing_client_tax, icon: 'fa-id-badge' },
        { label: 'Seller IBAN', missing: missing.missing_iban, icon: 'fa-building-columns' },
    ];

    grid.innerHTML = items.map(item => {
        const complete = total - item.missing;
        const pct = total > 0 ? Math.round((complete / total) * 100) : 100;
        const color = pct === 100 ? '#34d399' : pct >= 80 ? '#fbbf24' : '#f87171';

        return `
            <div class="compliance-item">
                <div class="compliance-header">
                    <i class="fa-solid ${item.icon}" style="color: ${color}"></i>
                    <span>${item.label}</span>
                </div>
                <div class="compliance-bar-wrapper">
                    <div class="compliance-bar" style="width: ${pct}%; background: ${color};"></div>
                </div>
                <div class="compliance-stats">
                    <span style="color: ${color}; font-weight: 700;">${pct}%</span>
                    <span class="text-muted">${complete}/${total} complete</span>
                </div>
            </div>
        `;
    }).join('');
}

// =========================================================================
// OUTLIERS
// =========================================================================
function renderOutliers(outliers) {
    const section = document.getElementById('outliers-section');
    const list = document.getElementById('outlier-list');
    if (!section || !list) return;

    if (!outliers || outliers.length === 0) {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');
    list.innerHTML = outliers.map(o => `
        <div class="outlier-item">
            <div class="outlier-indicator"></div>
            <div class="outlier-info">
                <strong>Invoice #${o.invoice_no}</strong>
                <span class="text-muted">${o.seller} · ${o.category}</span>
            </div>
            <div class="outlier-amount">$${o.amount.toLocaleString()}</div>
        </div>
    `).join('');
}

// =========================================================================
// DATA TABLE
// =========================================================================
let tableData = [];

function renderDataTable(rawData) {
    tableData = rawData || [];
    renderTableRows(tableData);
}

function renderTableRows(data) {
    const tbody = document.getElementById('data-table-body');
    if (!tbody) return;

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 40px;">No data to display</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(row => `
        <tr>
            <td>${row.invoice_no}</td>
            <td>${row.date}</td>
            <td>${row.seller_name}</td>
            <td>${row.client_name}</td>
            <td class="price">$${row.total_amount.toLocaleString()}</td>
            <td><span class="category-badge">${row.category}</span></td>
        </tr>
    `).join('');
}

function setupTableControls() {
    // Search
    const searchInput = document.getElementById('table-search');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            filterTable();
        });
    }

    // Category Filter
    const catFilter = document.getElementById('table-category-filter');
    if (catFilter) {
        catFilter.addEventListener('change', () => {
            filterTable();
        });
    }

    // Sortable Headers
    document.querySelectorAll('#data-table th[data-sort]').forEach(th => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-sort');
            if (currentSortCol === col) {
                currentSortAsc = !currentSortAsc;
            } else {
                currentSortCol = col;
                currentSortAsc = true;
            }
            sortAndRender();
        });
    });
}

function filterTable() {
    const search = (document.getElementById('table-search').value || '').toLowerCase();
    const catFilter = document.getElementById('table-category-filter').value;

    let filtered = tableData;

    if (search) {
        filtered = filtered.filter(row =>
            Object.values(row).some(v =>
                String(v).toLowerCase().includes(search)
            )
        );
    }

    if (catFilter) {
        filtered = filtered.filter(row => row.category === catFilter);
    }

    renderTableRows(filtered);
}

function sortAndRender() {
    const sorted = [...tableData].sort((a, b) => {
        let valA = a[currentSortCol];
        let valB = b[currentSortCol];

        if (currentSortCol === 'total_amount') {
            valA = parseFloat(valA) || 0;
            valB = parseFloat(valB) || 0;
        } else {
            valA = String(valA).toLowerCase();
            valB = String(valB).toLowerCase();
        }

        if (valA < valB) return currentSortAsc ? -1 : 1;
        if (valA > valB) return currentSortAsc ? 1 : -1;
        return 0;
    });

    renderTableRows(sorted);
}

function populateCategoryFilter(catData) {
    const filter = document.getElementById('table-category-filter');
    if (!filter || !catData) return;

    filter.innerHTML = '<option value="">All Categories</option>';
    Object.keys(catData).forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat;
        opt.textContent = `${cat} (${catData[cat]})`;
        filter.appendChild(opt);
    });
}

// =========================================================================
// PDF EXPORT
// =========================================================================
function setupPDFExport() {
    const btn = document.getElementById('export-pdf-btn');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';

        try {
            const dashboard = document.getElementById('dashboard-content');
            const canvas = await html2canvas(dashboard, {
                backgroundColor: '#0B1120',
                scale: 1.5,
                logging: false,
                useCORS: true
            });

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF('p', 'mm', 'a4');
            const imgWidth = 210;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;
            const pageHeight = 297;

            let yOffset = 0;
            while (yOffset < imgHeight) {
                if (yOffset > 0) doc.addPage();
                doc.addImage(
                    canvas.toDataURL('image/jpeg', 0.95),
                    'JPEG',
                    0,
                    -yOffset,
                    imgWidth,
                    imgHeight
                );
                yOffset += pageHeight;
            }

            doc.save('invoice_analytics_report.pdf');
        } catch (e) {
            console.error('PDF generation failed:', e);
            alert('PDF export failed. Please try again.');
        }

        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-file-pdf"></i> Export PDF';
    });
}
