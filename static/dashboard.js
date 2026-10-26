/**
 * Behaviour Insights - Modern Interactive Dashboard Script
 * Handles state, API communication, Chart.js lifecycle, and dynamic updates
 */

document.addEventListener('DOMContentLoaded', () => {
    // Current Application State
    const state = {
        platform: 'Netflix',
        dataSource: 'preset',      // 'preset', 'manual', 'synthetic'
        presetKey: 'balanced',     // 'low', 'balanced', 'high', 'zero_var'
        threshold: 150.0,
        manualInput: '',
        chartInstance: null,
        currentPlatformInfo: null
    };

    // DOM Elements Cache
    const elements = {
        platformButtons: document.querySelectorAll('.btn-platform'),
        heroPlatformName: document.getElementById('hero-platform-name'),
        heroPlatformMath: document.getElementById('hero-platform-math'),
        heroPlatformIcon: document.getElementById('hero-platform-icon'),
        
        modeTabs: document.querySelectorAll('.tab-btn'),
        presetsSection: document.getElementById('presets-section'),
        presetChips: document.querySelectorAll('.chip-btn'),
        manualInputSection: document.getElementById('manual-input-section'),
        activityTextarea: document.getElementById('activity-textarea'),
        obsCounter: document.getElementById('obs-counter'),
        
        unitTag: document.getElementById('unit-tag'),
        unitSuffix: document.getElementById('unit-suffix'),
        thresholdSlider: document.getElementById('threshold-slider'),
        thresholdValBadge: document.getElementById('threshold-val-badge'),
        thresholdInput: document.getElementById('threshold-input'),
        
        btnAnalyze: document.getElementById('btn-analyze'),
        btnReset: document.getElementById('btn-reset'),
        alertError: document.getElementById('alert-error'),
        errorMessage: document.getElementById('error-message'),
        
        // Metrics
        metricObs: document.getElementById('metric-obs'),
        metricObsSource: document.getElementById('metric-obs-source'),
        metricMean: document.getElementById('metric-mean'),
        metricMeanParam: document.getElementById('metric-mean-param'),
        metricStd: document.getElementById('metric-std'),
        metricVariance: document.getElementById('metric-variance'),
        metricProbEmp: document.getElementById('metric-prob-emp'),
        metricProbModel: document.getElementById('metric-prob-model'),
        metricTierBadge: document.getElementById('metric-tier-badge'),
        metricScoreText: document.getElementById('metric-score-text'),
        
        // Chart Header
        chartTitle: document.getElementById('chart-title'),
        chartSubtitle: document.getElementById('chart-subtitle'),
        chartLegendModel: document.getElementById('chart-legend-model'),
        
        // Insights
        insightMean: document.getElementById('insight-mean'),
        insightVariance: document.getElementById('insight-variance'),
        insightProbability: document.getElementById('insight-probability'),
        
        // Recommendations
        recommendationsList: document.getElementById('recommendations-list'),
        recTierLabel: document.getElementById('rec-tier-label')
    };

    // Preset Data Repository for immediate UI response
    const defaultPresets = {
        Netflix: {
            low: "30, 45, 50, 40, 35, 60, 55, 45, 50, 40, 35, 48, 52, 38, 42",
            balanced: "95, 110, 120, 130, 140, 125, 135, 115, 105, 150, 120, 128, 132, 118, 122",
            high: "180, 210, 240, 195, 225, 260, 270, 205, 230, 290, 215, 245, 255, 220, 280",
            zero_var: "120, 120, 120, 120, 120, 120, 120, 120, 120, 120"
        },
        Spotify: {
            low: "15, 20, 25, 30, 22, 18, 28, 35, 24, 20, 19, 27, 31, 23, 26",
            balanced: "65, 75, 80, 85, 90, 95, 70, 88, 92, 100, 78, 82, 86, 74, 98",
            high: "140, 155, 170, 185, 160, 200, 210, 175, 190, 220, 165, 180, 195, 172, 205",
            zero_var: "80, 80, 80, 80, 80, 80, 80, 80, 80, 80"
        },
        Amazon: {
            low: "3, 5, 4, 6, 2, 5, 7, 3, 4, 6, 5, 3, 4, 2, 5",
            balanced: "14, 16, 18, 20, 17, 19, 15, 21, 18, 22, 16, 17, 19, 15, 20",
            high: "32, 38, 42, 35, 45, 39, 48, 36, 41, 50, 37, 43, 46, 34, 40",
            zero_var: "15, 15, 15, 15, 15, 15, 15, 15, 15, 15"
        }
    };

    // Platform Specific Defaults
    const platformDefaults = {
        Netflix: { threshold: 150, min: 0, max: 350, step: 5, unit: "minutes/day", math: "X ~ Normal(μ, σ²)", icon: "🎬" },
        Spotify: { threshold: 90, min: 0, max: 250, step: 5, unit: "minutes/day", math: "X ~ Normal(μ, σ²)", icon: "🎧" },
        Amazon:  { threshold: 20, min: 0, max: 60, step: 1, unit: "clicks/session", math: "X ~ Poisson(λ)", icon: "📦" }
    };

    // Initialize UI on page load
    function init() {
        setupEventListeners();
        applyPlatformDefaults(state.platform);
        fetchAnalysis();
    }

    // Set slider and threshold defaults when changing platforms
    function applyPlatformDefaults(platform) {
        const def = platformDefaults[platform];
        state.threshold = def.threshold;
        
        elements.thresholdSlider.min = def.min;
        elements.thresholdSlider.max = def.max;
        elements.thresholdSlider.step = def.step;
        elements.thresholdSlider.value = def.threshold;
        
        elements.thresholdInput.value = def.threshold;
        elements.thresholdValBadge.textContent = `${def.threshold} ${def.unit}`;
        elements.unitTag.textContent = def.unit;
        elements.unitSuffix.textContent = def.unit;
        
        elements.heroPlatformName.textContent = platform;
        elements.heroPlatformMath.textContent = def.math;
        elements.heroPlatformIcon.textContent = def.icon;

        // Populate textarea with current platform preset
        if (state.dataSource === 'preset') {
            elements.activityTextarea.value = defaultPresets[platform][state.presetKey] || '';
            updateObservationCount();
        }
    }

    // Bind all user events
    function setupEventListeners() {
        // Platform switcher buttons
        elements.platformButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const plat = btn.getAttribute('data-platform');
                if (plat === state.platform) return;
                
                elements.platformButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                state.platform = plat;
                hideError();
                applyPlatformDefaults(plat);
                fetchAnalysis();
            });
        });

        // Data mode tabs
        elements.modeTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const mode = tab.getAttribute('data-mode');
                elements.modeTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                state.dataSource = mode;
                hideError();
                
                if (mode === 'preset') {
                    elements.presetsSection.style.display = 'flex';
                    elements.manualInputSection.style.display = 'block';
                    elements.activityTextarea.value = defaultPresets[state.platform][state.presetKey] || '';
                    elements.activityTextarea.readOnly = true;
                } else if (mode === 'manual') {
                    elements.presetsSection.style.display = 'none';
                    elements.manualInputSection.style.display = 'block';
                    elements.activityTextarea.readOnly = false;
                    elements.activityTextarea.placeholder = "Enter custom values e.g. 110, 125, 140, 95 (separated by comma, space or newline)";
                } else if (mode === 'synthetic') {
                    elements.presetsSection.style.display = 'none';
                    elements.manualInputSection.style.display = 'none';
                }
                
                updateObservationCount();
                fetchAnalysis();
            });
        });

        // Preset chips
        elements.presetChips.forEach(chip => {
            chip.addEventListener('click', () => {
                elements.presetChips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                
                const presetKey = chip.getAttribute('data-preset');
                state.presetKey = presetKey;
                
                elements.activityTextarea.value = defaultPresets[state.platform][presetKey] || '';
                updateObservationCount();
                fetchAnalysis();
            });
        });

        // Manual textarea live count
        elements.activityTextarea.addEventListener('input', () => {
            updateObservationCount();
        });

        // Threshold Slider & Input sync
        elements.thresholdSlider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            state.threshold = val;
            elements.thresholdInput.value = val;
            elements.thresholdValBadge.textContent = `${val} ${platformDefaults[state.platform].unit}`;
        });

        elements.thresholdSlider.addEventListener('change', () => {
            fetchAnalysis();
        });

        elements.thresholdInput.addEventListener('change', (e) => {
            let val = parseFloat(e.target.value);
            if (isNaN(val) || val < 0) val = platformDefaults[state.platform].threshold;
            state.threshold = val;
            elements.thresholdSlider.value = val;
            elements.thresholdValBadge.textContent = `${val} ${platformDefaults[state.platform].unit}`;
            fetchAnalysis();
        });

        // Primary Action Button
        elements.btnAnalyze.addEventListener('click', () => {
            fetchAnalysis();
        });

        // Reset Button
        elements.btnReset.addEventListener('click', () => {
            state.presetKey = 'balanced';
            elements.presetChips.forEach(c => {
                c.classList.toggle('active', c.getAttribute('data-preset') === 'balanced');
            });
            applyPlatformDefaults(state.platform);
            hideError();
            fetchAnalysis();
        });
    }

    // Count observations in textarea
    function updateObservationCount() {
        const text = elements.activityTextarea.value.trim();
        if (!text) {
            elements.obsCounter.textContent = '0 items';
            return;
        }
        const tokens = text.split(/[,;\s]+/).filter(t => t.length > 0);
        elements.obsCounter.textContent = `${tokens.length} items`;
    }

    function showError(msg) {
        elements.errorMessage.textContent = msg;
        elements.alertError.style.display = 'flex';
    }

    function hideError() {
        elements.alertError.style.display = 'none';
        elements.errorMessage.textContent = '';
    }

    // Call Flask Backend API
    function fetchAnalysis() {
        hideError();
        
        const payload = {
            platform: state.platform,
            data_source: state.dataSource,
            preset_key: state.presetKey,
            threshold: state.threshold,
            manual_input: elements.activityTextarea.value
        };

        elements.btnAnalyze.innerHTML = `<span>⏳</span> Calculating...`;

        fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => {
            elements.btnAnalyze.innerHTML = `<span>⚡</span> Analyse Behaviour`;
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || 'Server calculation error occurred.');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                renderDashboard(data);
            } else {
                showError(data.error || 'Failed to process dataset.');
            }
        })
        .catch(err => {
            elements.btnAnalyze.innerHTML = `<span>⚡</span> Analyse Behaviour`;
            showError(err.message);
        });
    }

    // Update entire dashboard view
    function renderDashboard(data) {
        state.currentPlatformInfo = data.platform;
        const analysis = data.analysis;
        const stats = analysis.stats;
        const insights = data.insights;

        // 1. Metric Cards
        elements.metricObs.textContent = stats.n;
        elements.metricObsSource.textContent = 
            data.data_source === 'synthetic' ? 'Random Synthetic (N=500)' :
            data.data_source === 'preset' ? `Preset: ${state.presetKey}` : 'Manual Input';

        elements.metricMean.textContent = stats.mean.toFixed(1);
        elements.metricMeanParam.textContent = `${stats.parameter_name} [${data.platform.unit}]`;

        elements.metricStd.textContent = `σ = ${stats.pop_std.toFixed(2)}`;
        elements.metricVariance.textContent = `Var σ² = ${stats.pop_variance.toFixed(2)} (Sample s = ${stats.sample_std.toFixed(2)})`;

        const empPct = (stats.empirical_prob * 100).toFixed(1);
        const theoPct = (stats.theoretical_prob * 100).toFixed(1);
        elements.metricProbEmp.textContent = `${empPct}%`;
        elements.metricProbModel.textContent = `P(X ≥ ${stats.threshold}): Model ${theoPct}% vs Empirical ${empPct}%`;

        // Tier badge
        elements.metricTierBadge.textContent = insights.tier;
        elements.metricTierBadge.className = `tier-badge ${insights.tier_class}`;
        elements.metricScoreText.textContent = `Engagement Score: ${insights.score}/100`;

        // 2. Chart Header Labels
        if (analysis.model_type === 'continuous') {
            elements.chartTitle.textContent = `${data.platform.name}: Observed Histogram & Fitted Normal PDF`;
            elements.chartSubtitle.textContent = `Continuous Random Variable X = ${data.platform.activity_label} (${data.platform.unit}). Left: User Counts. Right: Probability Density f(x).`;
            elements.chartLegendModel.textContent = `Fitted Normal PDF (μ=${stats.mean}, σ=${stats.pop_std})`;
        } else {
            elements.chartTitle.textContent = `${data.platform.name}: Observed Frequency & Theoretical Poisson PMF`;
            elements.chartSubtitle.textContent = `Discrete Random Variable X = ${data.platform.activity_label} (${data.platform.unit}). Left: User Counts. Right: Poisson PMF P(X=k).`;
            elements.chartLegendModel.textContent = `Theoretical Poisson PMF (λ=${stats.mean})`;
        }

        // 3. Render Chart
        renderChart(analysis, data.platform);

        // 4. Statistical Insights
        elements.insightMean.textContent = insights.expected_value_text;
        elements.insightVariance.textContent = insights.variance_text;
        elements.insightProbability.textContent = insights.probability_text;

        // 5. Recommendations
        elements.recTierLabel.textContent = `Tier: ${insights.tier} (Score ${insights.score}/100)`;
        elements.recommendationsList.innerHTML = '';
        insights.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.className = 'rec-item';
            li.innerHTML = `<span class="rec-bullet">✦</span><span>${rec}</span>`;
            elements.recommendationsList.appendChild(li);
        });
    }

    // Chart.js Visualization Rendering
    function renderChart(analysis, platform) {
        const ctx = document.getElementById('analyticsChart').getContext('2d');

        // Destroy previous instance to ensure fresh rendering and avoid stale values
        if (state.chartInstance) {
            state.chartInstance.destroy();
            state.chartInstance = null;
        }

        const isContinuous = analysis.model_type === 'continuous';

        if (isContinuous) {
            // Continuous Normal Chart
            const hist = analysis.chart_data.histogram;
            const pdf = analysis.chart_data.pdf_curve;

            // Map histogram labels and counts
            const labels = hist.labels;
            const barData = hist.counts;

            // Compute expected counts at bin centers to plot smooth overlay curve
            // Expected count in bin i = N * bin_width * norm.pdf(bin_center)
            const n = analysis.stats.n;
            const binWidth = hist.bin_width;
            const mu = analysis.stats.mean;
            const sigma = analysis.stats.pop_std;

            const expectedCountsAtBins = hist.bin_centers.map(center => {
                if (sigma < 1e-6) return 0;
                // Normal pdf evaluated at center
                const exponent = -0.5 * Math.pow((center - mu) / sigma, 2);
                const density = (1.0 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(exponent);
                return Number((density * n * binWidth).toFixed(2));
            });

            // Density values for secondary right axis
            const densityAtBins = hist.bin_centers.map(center => {
                if (sigma < 1e-6) return 0;
                const exponent = -0.5 * Math.pow((center - mu) / sigma, 2);
                return Number(((1.0 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(exponent)).toFixed(5));
            });

            state.chartInstance = new Chart(ctx, {
                data: {
                    labels: labels,
                    datasets: [
                        {
                            type: 'bar',
                            label: 'Observed Users (Count)',
                            data: barData,
                            backgroundColor: 'rgba(59, 130, 246, 0.65)',
                            borderColor: 'rgba(59, 130, 246, 1)',
                            borderWidth: 1.5,
                            borderRadius: 6,
                            yAxisID: 'y'
                        },
                        {
                            type: 'line',
                            label: `Fitted Normal Curve (Expected Users)`,
                            data: expectedCountsAtBins,
                            borderColor: '#a855f7',
                            backgroundColor: 'rgba(168, 85, 247, 0.12)',
                            borderWidth: 2.5,
                            tension: 0.35,
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: '#a855f7',
                            pointHoverRadius: 6,
                            yAxisID: 'y'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    plugins: {
                        legend: {
                            display: true,
                            labels: {
                                color: '#94a3b8',
                                font: { family: 'Inter', size: 12 }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            titleColor: '#fff',
                            bodyColor: '#cbd5e1',
                            borderColor: 'rgba(148, 163, 184, 0.2)',
                            borderWidth: 1,
                            padding: 10,
                            callbacks: {
                                afterBody: function(tooltipItems) {
                                    const idx = tooltipItems[0].dataIndex;
                                    const center = hist.bin_centers[idx];
                                    const dens = densityAtBins[idx];
                                    return `Bin Center: ${center} ${platform.unit}\nNormal PDF Density: ${dens}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: `${platform.activity_label} Intervals (${platform.unit})`,
                                color: '#94a3b8',
                                font: { size: 12, weight: '600' }
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)'
                            },
                            ticks: { color: '#cbd5e1' }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'User Count (Frequency)',
                                color: '#93c5fd',
                                font: { size: 12, weight: '600' }
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.06)'
                            },
                            ticks: { color: '#93c5fd', precision: 0 },
                            beginAtZero: true
                        }
                    }
                }
            });

        } else {
            // Discrete Poisson Chart (Amazon)
            const kVals = analysis.chart_data.k_values;
            const labels = analysis.chart_data.labels;
            const obsCounts = analysis.chart_data.observed_counts;
            const poissonPMF = analysis.chart_data.poisson_pmf;
            const expectedCounts = analysis.chart_data.expected_counts;

            state.chartInstance = new Chart(ctx, {
                data: {
                    labels: labels,
                    datasets: [
                        {
                            type: 'bar',
                            label: 'Observed Click Frequency (Users)',
                            data: obsCounts,
                            backgroundColor: 'rgba(245, 158, 11, 0.65)',
                            borderColor: 'rgba(245, 158, 11, 1)',
                            borderWidth: 1.5,
                            borderRadius: 4,
                            yAxisID: 'y'
                        },
                        {
                            type: 'line',
                            label: 'Theoretical Poisson PMF: P(X=k)',
                            data: poissonPMF,
                            borderColor: '#a855f7',
                            backgroundColor: 'rgba(168, 85, 247, 0.15)',
                            borderWidth: 2.5,
                            tension: 0.2,
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: '#a855f7',
                            pointHoverRadius: 6,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    plugins: {
                        legend: {
                            display: true,
                            labels: {
                                color: '#94a3b8',
                                font: { family: 'Inter', size: 12 }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            titleColor: '#fff',
                            bodyColor: '#cbd5e1',
                            borderColor: 'rgba(148, 163, 184, 0.2)',
                            borderWidth: 1,
                            padding: 10,
                            callbacks: {
                                afterBody: function(tooltipItems) {
                                    const idx = tooltipItems[0].dataIndex;
                                    const k = kVals[idx];
                                    const expCount = expectedCounts[idx];
                                    return `Click Count k = ${k}\nExpected Users: ${expCount}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Product Click Count (k)',
                                color: '#94a3b8',
                                font: { size: 12, weight: '600' }
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)'
                            },
                            ticks: { color: '#cbd5e1' }
                        },
                        y: {
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Observed User Count',
                                color: '#fcd34d',
                                font: { size: 12, weight: '600' }
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.06)'
                            },
                            ticks: { color: '#fcd34d', precision: 0 },
                            beginAtZero: true
                        },
                        y1: {
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Poisson Probability P(X=k)',
                                color: '#c4b5fd',
                                font: { size: 12, weight: '600' }
                            },
                            grid: {
                                drawOnChartArea: false // prevent grid clash
                            },
                            ticks: {
                                color: '#c4b5fd',
                                callback: function(val) {
                                    return (val * 100).toFixed(1) + '%';
                                }
                            },
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    // Launch!
    init();
});
