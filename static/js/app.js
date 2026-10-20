// =========================================================================
// StatVision State & Configuration
// =========================================================================
let currentTheme = localStorage.getItem("statvision_theme") || "light";
let currentData = null;
let chartHeight = 380;
let maxCategories = 10;
let corrThreshold = 0.75;

const MATH_PALETTE = ["#2563eb", "#0284c7", "#0d9488", "#7c3aed", "#d97706", "#dc2626"];

// =========================================================================
// Theme Switching
// =========================================================================
function setTheme(mode) {
    currentTheme = mode;
    localStorage.setItem("statvision_theme", mode);
    document.documentElement.setAttribute("data-theme", mode);

    const isLight = mode === "light";
    const btnL = document.getElementById("btn-theme-light");
    const btnD = document.getElementById("btn-theme-dark");
    if (btnL) btnL.classList.toggle("active", isLight);
    if (btnD) btnD.classList.toggle("active", !isLight);

    const mobileIcon = document.getElementById("mobile-theme-icon");
    if (mobileIcon) {
        mobileIcon.textContent = isLight ? "🌙" : "☀️";
    }

    if (currentData) {
        replotAllCharts();
    }
}

function toggleTheme() {
    setTheme(currentTheme === "dark" ? "light" : "dark");
}

function toggleMobileSidebar(forceState) {
    const sidebar = document.getElementById("sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (!sidebar || !backdrop) return;
    
    const isOpen = forceState !== undefined ? forceState : !sidebar.classList.contains("open");
    sidebar.classList.toggle("open", isOpen);
    backdrop.classList.toggle("open", isOpen);
    document.body.style.overflow = isOpen ? "hidden" : "";
}

function getPlotlyLayoutTheme() {
    const isDark = currentTheme === "dark";
    const fontColor = isDark ? "#f8fafc" : "#0f172a";
    const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";

    return {
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { family: "Inter, sans-serif", size: 12, color: fontColor },
        title: { font: { size: 14, family: "Space Grotesk, sans-serif", color: fontColor } },
        margin: { l: 45, r: 25, t: 45, b: 40 },
        height: chartHeight,
        xaxis: { gridcolor: gridColor, zerolinecolor: gridColor },
        yaxis: { gridcolor: gridColor, zerolinecolor: gridColor }
    };
}

// =========================================================================
// Sidebar Controls
// =========================================================================
function updateChartHeight(val) {
    chartHeight = parseInt(val, 10);
    document.getElementById("val-chart-height").textContent = `${chartHeight}px`;
    if (currentData) {
        replotAllCharts();
    }
}

function updateMaxCategories(val) {
    maxCategories = parseInt(val, 10);
    document.getElementById("val-max-categories").textContent = maxCategories;
    if (currentData && currentData.cat_cols.length > 0 && currentData.num_cols.length > 0) {
        renderBarChart();
    }
}

function updateCorrThreshold(val) {
    corrThreshold = parseFloat(val);
    document.getElementById("val-corr-threshold").textContent = corrThreshold.toFixed(2);
    if (currentData) {
        renderInsights();
    }
}

// =========================================================================
// Drag & Drop File Upload
// =========================================================================
const dropzone = document.getElementById("file-dropzone");
if (dropzone) {
    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });
    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });
    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }
        document.getElementById("select-sample").value = "none";
        renderDataset(data);
    } catch (err) {
        alert(`Failed to upload dataset: ${err}`);
    }
}

async function handleSampleChange(sampleKey) {
    if (sampleKey === "none") return;
    try {
        const res = await fetch(`/api/sample/${sampleKey}`);
        const data = await res.json();
        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }
        renderDataset(data);
    } catch (err) {
        alert(`Failed to load benchmark dataset: ${err}`);
    }
}

// =========================================================================
// Master Dataset Renderer
// =========================================================================
function renderDataset(data) {
    currentData = data;

    if (window.innerWidth <= 992) {
        toggleMobileSidebar(false);
    }

    // Show analytics, hide landing
    document.getElementById("landing-section").style.display = "none";
    document.getElementById("analytics-section").style.display = "block";

    // 1. Metric Cards
    document.getElementById("metric-rows").textContent = data.rows.toLocaleString();
    document.getElementById("metric-cols").textContent = data.cols.toLocaleString();
    document.getElementById("metric-num").textContent = data.num_cols.length;
    document.getElementById("metric-cat").textContent = data.cat_cols.length;
    document.getElementById("metric-nulls").textContent = data.nulls.toLocaleString();

    // 2. Sample Vectors Table
    renderSampleTable(data.sample_vectors, data.columns);

    // 3. Mathematical Moments Table
    renderMomentsTable(data.moments);

    // 4. Insights & Diagnostics
    renderInsights();

    // 5. Populate Dropdowns
    populateDropdowns(data.num_cols, data.cat_cols);

    // 6. Section Visibility & Render Visualizations
    const hasNum = data.num_cols.length > 0;
    const hasMultiNum = data.num_cols.length >= 2;
    const hasCatAndNum = data.cat_cols.length > 0 && data.num_cols.length > 0;

    document.getElementById("sec-dist-wrap").style.display = hasNum ? "block" : "none";
    document.getElementById("sec-corr-wrap").style.display = hasMultiNum ? "block" : "none";
    document.getElementById("sec-bivariate-wrap").style.display = hasMultiNum ? "block" : "none";
    document.getElementById("sec-cat-wrap").style.display = hasCatAndNum ? "block" : "none";

    if (hasNum) renderDistributionCharts();
    if (hasMultiNum) {
        renderCorrelationHeatmap();
        renderScatterPlot();
    }
    if (hasCatAndNum) renderBarChart();
}

function renderSampleTable(records, columns) {
    const container = document.getElementById("sample-table-container");
    if (!records || records.length === 0) {
        container.innerHTML = "<p style='color: var(--muted-text);'>No records available.</p>";
        return;
    }

    let html = '<table class="stat-table"><thead><tr>';
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';

    records.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const val = row[col] !== undefined && row[col] !== null ? row[col] : '-';
            html += `<td>${val}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';

    container.innerHTML = html;
}

function renderMomentsTable(moments) {
    const container = document.getElementById("moments-table-container");
    if (!moments || moments.length === 0) {
        container.innerHTML = "<p style='color: var(--muted-text);'>No numeric features detected in dataset.</p>";
        return;
    }

    let html = `
    <table class="stat-table">
        <thead>
            <tr>
                <th>Feature</th>
                <th>Sample n</th>
                <th>Mean &mu;</th>
                <th>Std Dev &sigma;</th>
                <th>Std Error SE</th>
                <th>Min (x&#8320;)</th>
                <th>Q&#8321; (25%)</th>
                <th>Median Q&#8322;</th>
                <th>Q&#8323; (75%)</th>
                <th>Max (x&#8321;)</th>
            </tr>
        </thead>
        <tbody>
    `;

    moments.forEach(m => {
        html += `
        <tr>
            <td style="font-weight: 600; color: var(--primary-color);">${m.feature}</td>
            <td>${m.count.toLocaleString()}</td>
            <td>${m.mean}</td>
            <td>${m.std}</td>
            <td>${m.std_error}</td>
            <td>${m.min}</td>
            <td>${m.q1}</td>
            <td>${m.median}</td>
            <td>${m.q3}</td>
            <td>${m.max}</td>
        </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderInsights() {
    const container = document.getElementById("insights-container");
    if (!currentData) return;

    let items = [];

    // Missing values
    if (currentData.nulls > 0) {
        const nullsInfo = currentData.insights.find(i => i.pill.includes("NULL"));
        if (nullsInfo) items.push(nullsInfo);
    }

    // Skewness
    const skewInsights = currentData.insights.filter(i => i.pill.includes("SKEW"));
    items = items.concat(skewInsights);

    // Dynamic correlations based on slider threshold
    if (currentData.all_corrs && currentData.all_corrs.length > 0) {
        const matched = currentData.all_corrs.filter(c => Math.abs(c.r) >= corrThreshold);
        matched.forEach(c => {
            const relType = c.r > 0 ? "positive" : "negative";
            items.push({
                type: "info",
                pill: "CORR ~ r",
                text: `Strong ${relType} linear dependence between <b>${c.col1}</b> and <b>${c.col2}</b> (r = ${c.r.toFixed(2)} &ge; ${corrThreshold.toFixed(2)}).`
            });
        });
    }

    if (items.length === 0) {
        items.push({
            type: "success",
            pill: "STATUS ~ ✓",
            text: "Dataset appears well-conditioned: zero missing entries and low cross-collinearity observed."
        });
    }

    let html = "";
    items.forEach(item => {
        const pillClass = `pill-${item.type || 'info'}`;
        html += `
        <div class="insight-card">
            <span class="insight-pill ${pillClass}">${item.pill}</span>
            <span>${item.text}</span>
        </div>
        `;
    });

    container.innerHTML = html;
}

function populateDropdowns(numCols, catCols) {
    const distSelect = document.getElementById("select-dist-feature");
    const scatterX = document.getElementById("select-scatter-x");
    const scatterY = document.getElementById("select-scatter-y");
    const scatterColor = document.getElementById("select-scatter-color");
    const barGroup = document.getElementById("select-bar-group");
    const barVal = document.getElementById("select-bar-val");

    // Clear options
    [distSelect, scatterX, scatterY, scatterColor, barGroup, barVal].forEach(el => el.innerHTML = "");

    numCols.forEach((col, idx) => {
        distSelect.add(new Option(col, col, idx === 0, idx === 0));
        scatterX.add(new Option(col, col, idx === 0, idx === 0));
        scatterY.add(new Option(col, col, idx === Math.min(1, numCols.length - 1), idx === Math.min(1, numCols.length - 1)));
        barVal.add(new Option(col, col, idx === 0, idx === 0));
    });

    scatterColor.add(new Option("None", "none", true, true));
    [...catCols, ...numCols].forEach(col => {
        scatterColor.add(new Option(col, col));
    });

    catCols.forEach((col, idx) => {
        barGroup.add(new Option(col, col, idx === 0, idx === 0));
    });
}

// =========================================================================
// Plotly Chart Renderers
// =========================================================================
function replotAllCharts() {
    if (!currentData) return;
    if (currentData.num_cols.length > 0) renderDistributionCharts();
    if (currentData.num_cols.length >= 2) {
        renderCorrelationHeatmap();
        renderScatterPlot();
    }
    if (currentData.cat_cols.length > 0 && currentData.num_cols.length > 0) {
        renderBarChart();
    }
}

// § 4 Distribution Histogram & Outlier Boxplot
function renderDistributionCharts() {
    const col = document.getElementById("select-dist-feature").value;
    if (!col || !currentData.records[col]) return;

    const values = currentData.records[col].filter(v => v !== null && v !== undefined);
    const m = currentData.moments.find(item => item.feature === col);
    const meanVal = m ? m.mean : (values.reduce((a, b) => a + b, 0) / values.length);
    const medianVal = m ? m.median : meanVal;

    const baseLayout = getPlotlyLayoutTheme();

    // 1. Histogram
    const histData = [{
        type: "histogram",
        x: values,
        opacity: 0.88,
        marker: { color: "#2563eb" }
    }];

    const histLayout = {
        ...baseLayout,
        title: { text: `Probability Density & Empirical Histogram • ${col}`, font: baseLayout.title.font },
        xaxis: { ...baseLayout.xaxis, title: col },
        yaxis: { ...baseLayout.yaxis, title: "Count" },
        shapes: [
            {
                type: "line",
                x0: meanVal, x1: meanVal,
                y0: 0, y1: 1,
                yref: "paper",
                line: { color: "#d97706", width: 2, dash: "dash" }
            },
            {
                type: "line",
                x0: medianVal, x1: medianVal,
                y0: 0, y1: 1,
                yref: "paper",
                line: { color: "#059669", width: 2, dash: "dot" }
            }
        ],
        annotations: [
            {
                x: meanVal, y: 1, yref: "paper",
                text: `Mean &mu;: ${meanVal.toFixed(2)}`,
                showarrow: false,
                font: { color: "#d97706", size: 11, family: "Fira Code, monospace" },
                xanchor: "left", yanchor: "top"
            },
            {
                x: medianVal, y: 0.9, yref: "paper",
                text: `Median Q2: ${medianVal.toFixed(2)}`,
                showarrow: false,
                font: { color: "#059669", size: 11, family: "Fira Code, monospace" },
                xanchor: "right", yanchor: "top"
            }
        ]
    };

    Plotly.react("chart-hist", histData, histLayout, { responsive: true, displayModeBar: false });

    // 2. Boxplot
    const boxData = [{
        type: "box",
        y: values,
        boxpoints: "all",
        jitter: 0.35,
        pointpos: -1.8,
        marker: { color: "#0284c7", size: 4 },
        line: { color: "#0284c7" }
    }];

    const boxLayout = {
        ...baseLayout,
        title: { text: `Quantile Outlier Boxplot • ${col}`, font: baseLayout.title.font },
        yaxis: { ...baseLayout.yaxis, title: col }
    };

    Plotly.react("chart-box", boxData, boxLayout, { responsive: true, displayModeBar: false });
}

// § 5 Correlation Heatmap
function renderCorrelationHeatmap() {
    if (!currentData.corr_matrix) return;
    const { columns, values } = currentData.corr_matrix;

    const baseLayout = getPlotlyLayoutTheme();
    const isDark = currentTheme === "dark";

    const textValues = values.map(row => row.map(v => v.toFixed(2)));

    const data = [{
        type: "heatmap",
        z: values,
        x: columns,
        y: columns,
        colorscale: "RdBu",
        reversescale: true,
        zmin: -1.0,
        zmax: 1.0,
        text: textValues,
        texttemplate: "%{text}",
        textfont: { family: "Fira Code, monospace", size: 13, color: isDark ? "#ffffff" : "#000000" },
        colorbar: {
            tickfont: { family: "Fira Code, monospace", size: 11, color: baseLayout.font.color }
        }
    }];

    const layout = {
        ...baseLayout,
        title: { text: "Pearson Correlation Matrix (r)", font: baseLayout.title.font },
        xaxis: { ...baseLayout.xaxis, tickfont: { family: "Fira Code, monospace", size: 12 } },
        yaxis: { ...baseLayout.yaxis, tickfont: { family: "Fira Code, monospace", size: 12 } }
    };

    Plotly.react("chart-corr", data, layout, { responsive: true, displayModeBar: false });
}

// § 6 Bivariate Scatter & Linear Regression
function renderScatterPlot() {
    const xCol = document.getElementById("select-scatter-x").value;
    const yCol = document.getElementById("select-scatter-y").value;
    const colorCol = document.getElementById("select-scatter-color").value;
    const fitOls = document.getElementById("check-scatter-ols").checked;

    if (!xCol || !yCol || !currentData.records[xCol] || !currentData.records[yCol]) return;

    const xVals = currentData.records[xCol];
    const yVals = currentData.records[yCol];
    const colorVals = colorCol !== "none" ? currentData.records[colorCol] : null;

    // Filter valid pairs
    const validPoints = [];
    for (let i = 0; i < xVals.length; i++) {
        if (xVals[i] !== null && yVals[i] !== null && !isNaN(xVals[i]) && !isNaN(yVals[i])) {
            validPoints.push({
                x: xVals[i],
                y: yVals[i],
                c: colorVals ? colorVals[i] : null
            });
        }
    }

    const baseLayout = getPlotlyLayoutTheme();
    const traces = [];

    if (colorVals && currentData.cat_cols.includes(colorCol)) {
        // Group by category
        const groups = {};
        validPoints.forEach(p => {
            if (!groups[p.c]) groups[p.c] = { x: [], y: [] };
            groups[p.c].x.push(p.x);
            groups[p.c].y.push(p.y);
        });

        let colorIdx = 0;
        for (const [grpName, grpPts] of Object.entries(groups)) {
            traces.push({
                type: "scatter",
                mode: "markers",
                name: grpName,
                x: grpPts.x,
                y: grpPts.y,
                marker: { color: MATH_PALETTE[colorIdx % MATH_PALETTE.length], size: 7, opacity: 0.85 }
            });
            colorIdx++;
        }
    } else {
        traces.push({
            type: "scatter",
            mode: "markers",
            name: "Observations",
            x: validPoints.map(p => p.x),
            y: validPoints.map(p => p.y),
            marker: { color: "#2563eb", size: 7, opacity: 0.8 }
        });
    }

    // OLS Line calculation
    let trendInfo = "";
    if (fitOls && validPoints.length > 1) {
        let n = validPoints.length;
        let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0, sumYY = 0;
        validPoints.forEach(p => {
            sumX += p.x;
            sumY += p.y;
            sumXY += p.x * p.y;
            sumXX += p.x * p.x;
            sumYY += p.y * p.y;
        });

        const denom = (n * sumXX - sumX * sumX);
        if (denom !== 0) {
            const slope = (n * sumXY - sumX * sumY) / denom;
            const intercept = (sumY - slope * sumX) / n;
            const rNumerator = (n * sumXY - sumX * sumY);
            const rDenominator = Math.sqrt((n * sumXX - sumX * sumX) * (n * sumYY - sumY * sumY));
            const r = rDenominator !== 0 ? rNumerator / rDenominator : 0;
            const r2 = r * r;

            const minX = Math.min(...validPoints.map(p => p.x));
            const maxX = Math.max(...validPoints.map(p => p.x));

            traces.push({
                type: "scatter",
                mode: "lines",
                name: `OLS: ŷ=${slope.toFixed(2)}x+${intercept.toFixed(2)}`,
                x: [minX, maxX],
                y: [slope * minX + intercept, slope * maxX + intercept],
                line: { color: "#dc2626", width: 2.5, dash: "dash" }
            });

            trendInfo = `Linear Fit: OLS Model: ŷ = ${slope.toFixed(3)}x + (${intercept.toFixed(3)}) | Pearson r = ${r.toFixed(3)} | R² = ${r2.toFixed(3)}`;
        }
    }

    const layout = {
        ...baseLayout,
        title: { text: `Bivariate Scatter: ${xCol} vs ${yCol}`, font: baseLayout.title.font },
        xaxis: { ...baseLayout.xaxis, title: xCol },
        yaxis: { ...baseLayout.yaxis, title: yCol }
    };

    Plotly.react("chart-scatter", traces, layout, { responsive: true, displayModeBar: false });

    const callout = document.getElementById("scatter-trend-callout");
    if (trendInfo) {
        callout.style.display = "block";
        callout.innerHTML = `<b>Linear Fit:</b> <code>${trendInfo}</code>`;
    } else {
        callout.style.display = "none";
    }
}

// § 7 Categorical Factor Projections
function renderBarChart() {
    const groupCol = document.getElementById("select-bar-group").value;
    const valCol = document.getElementById("select-bar-val").value;
    const aggOp = document.getElementById("select-bar-agg").value;

    if (!groupCol || !valCol || !currentData.records[groupCol] || !currentData.records[valCol]) return;

    const gVals = currentData.records[groupCol];
    const vVals = currentData.records[valCol];

    // Grouping & Aggregation
    const grouped = {};
    for (let i = 0; i < gVals.length; i++) {
        const g = gVals[i];
        const v = vVals[i];
        if (g !== null && v !== null && !isNaN(v)) {
            if (!grouped[g]) grouped[g] = [];
            grouped[g].push(v);
        }
    }

    const labels = [];
    const scores = [];

    for (const [g, arr] of Object.entries(grouped)) {
        labels.push(g);
        if (aggOp === "mean") {
            scores.push(arr.reduce((a, b) => a + b, 0) / arr.length);
        } else if (aggOp === "median") {
            const sorted = [...arr].sort((a, b) => a - b);
            const mid = Math.floor(sorted.length / 2);
            scores.push(sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2);
        } else if (aggOp === "sum") {
            scores.push(arr.reduce((a, b) => a + b, 0));
        } else if (aggOp === "std") {
            const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
            const variance = arr.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / (arr.length > 1 ? arr.length - 1 : 1);
            scores.push(Math.sqrt(variance));
        }
    }

    // Sort descending and limit to maxCategories
    const combined = labels.map((l, i) => ({ label: l, val: scores[i] }))
        .sort((a, b) => b.val - a.val)
        .slice(0, maxCategories);

    const baseLayout = getPlotlyLayoutTheme();
    const data = [{
        type: "bar",
        x: combined.map(c => c.label),
        y: combined.map(c => c.val),
        marker: {
            color: combined.map(c => c.val),
            colorscale: "Blues"
        }
    }];

    const opSymbols = { mean: "Mean μ", median: "Median Q2", sum: "Sum Σ", std: "Std Dev σ" };
    const layout = {
        ...baseLayout,
        title: { text: `${opSymbols[aggOp]} of ${valCol} partitioned by ${groupCol}`, font: baseLayout.title.font },
        xaxis: { ...baseLayout.xaxis, title: groupCol },
        yaxis: { ...baseLayout.yaxis, title: valCol }
    };

    Plotly.react("chart-bar", data, layout, { responsive: true, displayModeBar: false });
}

// § 8 Moments Download
function downloadMomentsCSV() {
    if (!currentData || !currentData.moments || currentData.moments.length === 0) {
        alert("No moments data available to download.");
        return;
    }

    const keys = ["feature", "count", "mean", "std", "std_error", "min", "q1", "median", "q3", "max"];
    const headers = ["Feature", "Sample n", "Mean μ", "Std Dev σ", "Std Error SE", "Min x0", "Q1 (25%)", "Median Q2", "Q3 (75%)", "Max x1"];

    let csv = headers.join(",") + "\n";
    currentData.moments.forEach(m => {
        csv += keys.map(k => m[k]).join(",") + "\n";
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "statvision_moments.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Initial Theme Check
document.addEventListener("DOMContentLoaded", () => {
    setTheme(currentTheme);
});


// Responsive Plotly Resize on Screen or Orientation Change
let resizeTimeout;
window.addEventListener("resize", () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        ["chart-hist", "chart-box", "chart-corr", "chart-scatter", "chart-bar"].forEach(id => {
            const el = document.getElementById(id);
            if (el && el.data) {
                Plotly.Plots.resize(el);
            }
        });
    }, 120);
});
