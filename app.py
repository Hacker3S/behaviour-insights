"""
Behaviour Insights - B.Tech Micro Project 04
User Behaviour Modelling Using Random Variables and Probability Density Functions
Backend: Flask, NumPy, SciPy
"""

import json
import math
import numpy as np
from scipy import stats
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

PLATFORMS = {
    "Netflix": {
        "name": "Netflix",
        "type": "continuous",
        "unit": "minutes/day",
        "activity_label": "Daily Watch Time",
        "distribution_name": "Normal Distribution",
        "symbol": "X ~ N(μ, σ²)",
        "default_threshold": 150.0,
        "synthetic_params": {"loc": 125.0, "scale": 32.0, "size": 500, "clip_min": 5.0},
        "presets": {
            "low": [30, 45, 50, 40, 35, 60, 55, 45, 50, 40, 35, 48, 52, 38, 42],
            "balanced": [95, 110, 120, 130, 140, 125, 135, 115, 105, 150, 120, 128, 132, 118, 122],
            "high": [180, 210, 240, 195, 225, 260, 270, 205, 230, 290, 215, 245, 255, 220, 280],
            "zero_var": [120, 120, 120, 120, 120, 120, 120, 120, 120, 120]
        }
    },
    "Spotify": {
        "name": "Spotify",
        "type": "continuous",
        "unit": "minutes/day",
        "activity_label": "Daily Listening Time",
        "distribution_name": "Normal Distribution",
        "symbol": "X ~ N(μ, σ²)",
        "default_threshold": 90.0,
        "synthetic_params": {"loc": 85.0, "scale": 26.0, "size": 500, "clip_min": 2.0},
        "presets": {
            "low": [15, 20, 25, 30, 22, 18, 28, 35, 24, 20, 19, 27, 31, 23, 26],
            "balanced": [65, 75, 80, 85, 90, 95, 70, 88, 92, 100, 78, 82, 86, 74, 98],
            "high": [140, 155, 170, 185, 160, 200, 210, 175, 190, 220, 165, 180, 195, 172, 205],
            "zero_var": [80, 80, 80, 80, 80, 80, 80, 80, 80, 80]
        }
    },
    "Amazon": {
        "name": "Amazon",
        "type": "discrete",
        "unit": "clicks/session",
        "activity_label": "Product Clicks per Session",
        "distribution_name": "Poisson Distribution",
        "symbol": "X ~ Poisson(λ)",
        "default_threshold": 20.0,
        "synthetic_params": {"lam": 18.0, "size": 500},
        "presets": {
            "low": [3, 5, 4, 6, 2, 5, 7, 3, 4, 6, 5, 3, 4, 2, 5],
            "balanced": [14, 16, 18, 20, 17, 19, 15, 21, 18, 22, 16, 17, 19, 15, 20],
            "high": [32, 38, 42, 35, 45, 39, 48, 36, 41, 50, 37, 43, 46, 34, 40],
            "zero_var": [15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
        }
    }
}

np.random.seed(42)

def generate_synthetic_data(platform_key: str):
    config = PLATFORMS.get(platform_key, PLATFORMS["Netflix"])
    params = config["synthetic_params"]
    if config["type"] == "continuous":
        data = np.random.normal(loc=params["loc"], scale=params["scale"], size=params["size"])
        data = np.clip(data, a_min=params["clip_min"], a_max=None)
        return [round(float(v), 1) for v in data]
    else:  # discrete Poisson
        data = np.random.poisson(lam=params["lam"], size=params["size"])
        return [int(v) for v in data]

def compute_continuous_analytics(activity, threshold, platform_info):
    arr = np.array(activity, dtype=float)
    n = len(arr)
    mean_val = float(np.mean(arr))
    pop_var = float(np.var(arr, ddof=0))
    sample_var = float(np.var(arr, ddof=1)) if n > 1 else 0.0
    pop_std = float(math.sqrt(pop_var))
    sample_std = float(math.sqrt(sample_var)) if n > 1 else 0.0
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))
    median_val = float(np.median(arr))

    # Empirical probability X >= threshold
    empirical_prob = float(np.sum(arr >= threshold) / n)

    # Theoretical probability using Normal Distribution
    if pop_std > 1e-6:
        # Survival function = 1 - CDF
        theoretical_prob = float(stats.norm.sf(threshold, loc=mean_val, scale=pop_std))
    else:
        theoretical_prob = 1.0 if mean_val >= threshold else 0.0

    # Build Histogram bins
    # For zero variance or very small range
    val_range = max_val - min_val
    if val_range < 1e-6:
        # Single spike case
        bins = [min_val - 5.0, min_val + 5.0]
        counts, edges = [n], bins
        bin_centers = [min_val]
        bin_labels = [f"{min_val:.1f}"]
        bin_width = 10.0
    else:
        # Decide number of bins using Sturges' rule, clamped between 6 and 20
        num_bins = min(max(int(math.ceil(math.log2(n) + 1)), 6), 20)
        counts, edges = np.histogram(arr, bins=num_bins)
        counts = counts.tolist()
        bin_centers = [(edges[i] + edges[i+1]) / 2.0 for i in range(len(counts))]
        bin_labels = [f"{edges[i]:.0f}-{edges[i+1]:.0f}" for i in range(len(counts))]
        bin_width = float(edges[1] - edges[0])

    # Normal PDF curve points for smooth plotting
    # Span across mean +- 3.5 std, or min to max
    if pop_std > 1e-6:
        curve_min = max(0.0, min(min_val - 0.5 * pop_std, mean_val - 3.2 * pop_std))
        curve_max = max(max_val + 0.5 * pop_std, mean_val + 3.2 * pop_std)
        curve_x = np.linspace(curve_min, curve_max, 80)
        curve_pdf = stats.norm.pdf(curve_x, loc=mean_val, scale=pop_std)
        # Expected counts matching the histogram bin width
        curve_expected_counts = curve_pdf * n * bin_width
        pdf_curve = {
            "x": [round(float(v), 1) for v in curve_x],
            "pdf_density": [round(float(v), 5) for v in curve_pdf],
            "expected_counts": [round(float(v), 2) for v in curve_expected_counts]
        }
    else:
        # Zero variance: theoretical delta representation
        pdf_curve = {
            "x": [round(min_val - 2.0, 1), round(min_val, 1), round(min_val + 2.0, 1)],
            "pdf_density": [0.0, 1.0, 0.0],
            "expected_counts": [0.0, float(n), 0.0]
        }

    return {
        "model_type": "continuous",
        "distribution_name": "Normal Distribution N(μ, σ²)",
        "stats": {
            "n": n,
            "mean": round(mean_val, 2),
            "pop_variance": round(pop_var, 2),
            "sample_variance": round(sample_var, 2),
            "pop_std": round(pop_std, 2),
            "sample_std": round(sample_std, 2),
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "median": round(median_val, 2),
            "threshold": round(threshold, 2),
            "empirical_prob": round(empirical_prob, 4),
            "theoretical_prob": round(theoretical_prob, 4),
            "parameter_name": "Mean (μ) & Std Dev (σ)",
            "parameter_values": f"μ = {mean_val:.2f}, σ = {pop_std:.2f}"
        },
        "chart_data": {
            "chart_type": "continuous_normal",
            "histogram": {
                "labels": bin_labels,
                "counts": counts,
                "bin_centers": [round(c, 1) for c in bin_centers],
                "bin_width": round(bin_width, 2)
            },
            "pdf_curve": pdf_curve
        }
    }

def compute_discrete_analytics(activity, threshold, platform_info):
    # Activity is discrete counts (e.g. integer click counts)
    arr = np.array([max(0, int(round(v))) for v in activity], dtype=int)
    n = len(arr)
    mean_val = float(np.mean(arr))
    pop_var = float(np.var(arr, ddof=0))
    sample_var = float(np.var(arr, ddof=1)) if n > 1 else 0.0
    pop_std = float(math.sqrt(pop_var))
    sample_std = float(math.sqrt(sample_var)) if n > 1 else 0.0
    min_val = int(np.min(arr))
    max_val = int(np.max(arr))
    median_val = float(np.median(arr))

    # Empirical probability X >= threshold
    empirical_prob = float(np.sum(arr >= threshold) / n)

    # Theoretical probability using Poisson Distribution
    # Parameter lambda = sample mean
    lam = max(1e-6, mean_val)
    # P(X >= threshold) = sum_{k=ceil(threshold)}^inf P(X=k) = poisson.sf(threshold - 1, mu=lam)
    # Note: sf(k) = P(X > k), so sf(threshold - 1) = P(X >= threshold) for integer threshold
    thresh_int = int(math.ceil(threshold))
    if thresh_int <= 0:
        theoretical_prob = 1.0
    else:
        theoretical_prob = float(stats.poisson.sf(thresh_int - 1, mu=lam))

    # Discrete integer frequency counts
    # Domain: from 0 up to max(max_val + 2, int(lam + 3 * sqrt(lam)) + 2)
    max_k = max(max_val + 1, int(lam + 3.0 * math.sqrt(lam)) + 2)
    max_k = min(max_k, 120)  # reasonable ceiling
    k_values = list(range(0, max_k + 1))

    # Observed counts for each integer k
    unique_vals, val_counts = np.unique(arr, return_counts=True)
    obs_dict = dict(zip(unique_vals.tolist(), val_counts.tolist()))
    observed_counts = [obs_dict.get(k, 0) for k in k_values]
    observed_rel_freq = [round(c / n, 4) for c in observed_counts]

    # Poisson Theoretical PMF
    poisson_pmf = [float(stats.poisson.pmf(k, mu=lam)) for k in k_values]
    expected_counts = [round(p * n, 2) for p in poisson_pmf]

    return {
        "model_type": "discrete",
        "distribution_name": "Poisson Distribution Pois(λ)",
        "stats": {
            "n": n,
            "mean": round(mean_val, 2),
            "pop_variance": round(pop_var, 2),
            "sample_variance": round(sample_var, 2),
            "pop_std": round(pop_std, 2),
            "sample_std": round(sample_std, 2),
            "min": min_val,
            "max": max_val,
            "median": round(median_val, 2),
            "threshold": round(threshold, 2),
            "empirical_prob": round(empirical_prob, 4),
            "theoretical_prob": round(theoretical_prob, 4),
            "parameter_name": "Rate Parameter (λ)",
            "parameter_values": f"λ = {mean_val:.2f} (clicks/session)"
        },
        "chart_data": {
            "chart_type": "discrete_poisson",
            "k_values": k_values,
            "labels": [str(k) for k in k_values],
            "observed_counts": observed_counts,
            "observed_rel_freq": observed_rel_freq,
            "poisson_pmf": [round(p, 5) for p in poisson_pmf],
            "expected_counts": expected_counts
        }
    }

def generate_insights_and_recommendations(platform_key, stats_data, model_type):
    mean_val = stats_data["mean"]
    std_val = stats_data["pop_std"]
    thresh = stats_data["threshold"]
    emp_prob = stats_data["empirical_prob"]
    theo_prob = stats_data["theoretical_prob"]

    # Determine engagement tier based on platform benchmarks
    if platform_key == "Netflix":
        # Benchmarks: < 60 min (Low), 60-150 min (Moderate), 150-220 min (High), > 220 min (Power)
        if mean_val < 60:
            tier = "Low"
            tier_class = "tier-low"
            score = min(40, int((mean_val / 60) * 40))
        elif mean_val < 150:
            tier = "Moderate"
            tier_class = "tier-moderate"
            score = 40 + int(((mean_val - 60) / 90) * 35)
        elif mean_val < 220:
            tier = "High"
            tier_class = "tier-high"
            score = 75 + int(((mean_val - 150) / 70) * 15)
        else:
            tier = "Power User"
            tier_class = "tier-power"
            score = min(100, 90 + int(((mean_val - 220) / 100) * 10))

        recs = {
            "Low": [
                "Suggest short-form miniseries (under 30 mins) and viral trending trailers to lower entry friction.",
                "Implement personalized push notifications highlighting newly added titles in preferred genres.",
                "Optimize the mobile onboarding experience with curated 'Top 10 Today' reels."
            ],
            "Moderate": [
                "Promote 'Continue Watching' row prominently with episodic cliffhanger previews.",
                "Deliver weekend watchlist digests tailored to viewing history.",
                "Surface community-rated movies to encourage binge sessions."
            ],
            "High": [
                "Recommend early access to 4K Ultra HD releases and director's commentary tracks.",
                "Suggest specialized niche sub-genres (e.g. Nordic Noir, Sci-Fi anthologies).",
                "Enable customized profile badges and multi-profile family shared watchlists."
            ],
            "Power User": [
                "Offer beta access to interactive interactive content and exclusive live festival broadcasts.",
                "Suggest cross-media recommendations (soundtracks, companion podcasts).",
                "Provide advanced subtitle customization and offline multi-device download syncing."
            ]
        }[tier]

    elif platform_key == "Spotify":
        # Benchmarks: < 45 min (Low), 45-100 min (Moderate), 100-160 min (High), > 160 min (Power)
        if mean_val < 45:
            tier = "Low"
            tier_class = "tier-low"
            score = min(40, int((mean_val / 45) * 40))
        elif mean_val < 100:
            tier = "Moderate"
            tier_class = "tier-moderate"
            score = 40 + int(((mean_val - 45) / 55) * 35)
        elif mean_val < 160:
            tier = "High"
            tier_class = "tier-high"
            score = 75 + int(((mean_val - 100) / 60) * 15)
        else:
            tier = "Power User"
            tier_class = "tier-power"
            score = min(100, 90 + int(((mean_val - 160) / 80) * 10))

        recs = {
            "Low": [
                "Showcase curated 'Daily Mix' playlists and top regional hits on the homepage.",
                "Introduce 15-minute commute playlists and audiobooks sampler to build daily habits.",
                "Offer friendly lyrics display and quick song search to improve engagement."
            ],
            "Moderate": [
                "Serve personalized 'Discover Weekly' and 'Release Radar' updates based on favorite genres.",
                "Introduce podcast episode suggestions aligning with music listening windows.",
                "Prompt creation of collaborative playlists with friends."
            ],
            "High": [
                "Highlight localized concert alerts and pre-sale merchandise for top artists.",
                "Suggest lossless HiFi audio streams and immersive spatial audio settings.",
                "Provide artist radio deep cuts and underground track discovery."
            ],
            "Power User": [
                "Enable advanced DJ smart mixing and seamless playlist transitions.",
                "Deliver real-time social listening rooms and Spotify Wrapped quarterly previews.",
                "Promote premium family or duo plans and connected smart speaker integration."
            ]
        }[tier]

    else:  # Amazon
        # Benchmarks: < 10 clicks (Low), 10-22 clicks (Moderate), 22-35 clicks (High), > 35 clicks (Power)
        if mean_val < 10:
            tier = "Low"
            tier_class = "tier-low"
            score = min(40, int((mean_val / 10) * 40))
        elif mean_val < 22:
            tier = "Moderate"
            tier_class = "tier-moderate"
            score = 40 + int(((mean_val - 10) / 12) * 35)
        elif mean_val < 35:
            tier = "High"
            tier_class = "tier-high"
            score = 75 + int(((mean_val - 22) / 13) * 15)
        else:
            tier = "Power User"
            tier_class = "tier-power"
            score = min(100, 90 + int(((mean_val - 35) / 20) * 10))

        recs = {
            "Low": [
                "Streamline homepage search with autocomplete and visual category tiles.",
                "Display prominent seasonal discount vouchers and 'Lightning Deals' to stimulate browsing.",
                "Simplify 1-Click checkout and prominent free delivery thresholds."
            ],
            "Moderate": [
                "Show personalized 'Customers Also Viewed' carousels and verified buyer reviews.",
                "Display price drop alerts on items saved in cart or wishlists.",
                "Recommend bundles (e.g. 'Frequently Bought Together') with combo discounts."
            ],
            "High": [
                "Suggest Amazon Prime membership trial showcasing Prime Video and free express shipping.",
                "Surface complementary premium accessories for recently viewed categories.",
                "Enable repeat subscribe-and-save recommendations with tiered volume savings."
            ],
            "Power User": [
                "Offer invitation-only lightning deals and VIP early access to Prime Day promotions.",
                "Provide comprehensive comparison matrices across competing high-end brands.",
                "Recommend Amazon Business or bulk corporate purchasing perks."
            ]
        }[tier]

    # Plain language mathematical insights
    var_explanation = (
        "User activity is tightly clustered around the mean with minimal behavioral dispersion."
        if std_val < (mean_val * 0.2 + 0.1)
        else "User activity exhibits substantial variance, showing diverse segments from casual to heavy consumers."
    )

    prob_comparison = (
        f"Empirical probability ({emp_prob*100:.1f}%) closely matches the model prediction ({theo_prob*100:.1f}%), indicating strong model goodness-of-fit."
        if abs(emp_prob - theo_prob) < 0.08
        else f"Empirical observation ({emp_prob*100:.1f}%) diverges somewhat from theoretical prediction ({theo_prob*100:.1f}%), reflecting sample skewness or small-sample variance."
    )

    insights = {
        "expected_value_text": f"The sample mean {mean_val:.2f} serves as an unbiased point estimator for the theoretical expected value E[X]. Across this cohort, typical activity centers near this value.",
        "variance_text": f"With a standard deviation of σ = {std_val:.2f} (variance σ² = {stats_data['pop_variance']:.2f}), {var_explanation}",
        "probability_text": f"For the threshold t = {thresh:.1f}, {emp_prob*100:.1f}% of observed users met or exceeded this target. The theoretical model computes P(X ≥ {thresh:.1f}) = {theo_prob*100:.1f}%. {prob_comparison}",
        "tier": tier,
        "tier_class": tier_class,
        "score": score,
        "recommendations": recs
    }
    return insights

@app.route('/')
def index():
    return render_template('index.html', platforms=PLATFORMS)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    try:
        payload = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": "Invalid JSON payload"}), 400

    platform_key = payload.get("platform", "Netflix")
    if platform_key not in PLATFORMS:
        return jsonify({"error": f"Unknown platform '{platform_key}'"}), 400

    platform_info = PLATFORMS[platform_key]

    # Data source: "synthetic", "preset", or "manual"
    data_source = payload.get("data_source", "synthetic")
    preset_key = payload.get("preset_key", "balanced")
    raw_input = payload.get("manual_input", "")

    # Threshold
    try:
        threshold = float(payload.get("threshold", platform_info["default_threshold"]))
    except (ValueError, TypeError):
        threshold = platform_info["default_threshold"]

    # Acquire activity array
    activity = []
    if data_source == "synthetic":
        activity = generate_synthetic_data(platform_key)
    elif data_source == "preset":
        presets = platform_info["presets"]
        activity = presets.get(preset_key, presets["balanced"])
    elif data_source == "manual":
        # Parse comma, semicolon, whitespace, newline
        import re
        tokens = re.split(r'[,;\s]+', raw_input.strip())
        tokens = [t for t in tokens if t]
        if not tokens:
            return jsonify({"error": "Manual input is empty. Please enter numeric observations or pick a preset."}), 400

        parsed = []
        for t in tokens:
            try:
                val = float(t)
                if val < 0:
                    return jsonify({"error": f"Invalid negative value '{t}'. Activity observations must be non-negative (≥ 0)."}), 400
                if platform_info["type"] == "discrete":
                    parsed.append(int(round(val)))
                else:
                    parsed.append(val)
            except ValueError:
                return jsonify({"error": f"Invalid non-numeric value '{t}'. Please supply numbers separated by commas or spaces."}), 400
        activity = parsed
    else:
        activity = generate_synthetic_data(platform_key)

    if not activity:
        return jsonify({"error": "No valid activity observations available."}), 400

    # Execute statistical analysis based on model type
    if platform_info["type"] == "continuous":
        analysis = compute_continuous_analytics(activity, threshold, platform_info)
    else:
        analysis = compute_discrete_analytics(activity, threshold, platform_info)

    # Generate insights and recommendations
    insights = generate_insights_and_recommendations(platform_key, analysis["stats"], analysis["model_type"])

    response = {
        "success": True,
        "platform": platform_info,
        "data_source": data_source,
        "raw_count": len(activity),
        "analysis": analysis,
        "insights": insights
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
