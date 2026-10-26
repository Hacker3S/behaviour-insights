# Behaviour Insights: User Behaviour Modelling Analytics Dashboard

A modern, interactive Python Flask analytics web application for B.Tech Micro Project 04:
**“User Behaviour Modelling Using Random Variables and Probability Density Functions.”**

Developed using **Python Flask**, **NumPy**, **SciPy**, and **Chart.js**.

---

## 🚀 Key Features & Highlights

1. **Platform-Appropriate Mathematical Distributions**:
   - **Netflix & Spotify (Continuous Random Variable)**:
     - $X$: Viewing or listening time (minutes/day).
     - Models observed activity in a continuous histogram and overlays a fitted **Normal Probability Density Function (PDF)** $\mathcal{N}(\mu, \sigma^2)$.
     - Evaluates Expected Value $E[X]$, sample & population variance ($\sigma^2, s^2$), and standard deviation.
   - **Amazon (Discrete Random Variable)**:
     - $X$: Product click counts per session (integer counts $k \ge 0$).
     - Plots observed frequency against the fitted **Poisson Probability Mass Function (PMF)** $\text{Pois}(\lambda)$.
     - Estimates rate parameter $\lambda$ using sample mean $\bar{x}$.

2. **Interactive Exceedance Probability Engine**:
   - Computes both **Empirical Probability** $P_{\text{emp}}(X \ge t) = \frac{\#\{x_i \ge t\}}{n}$ and **Theoretical Model Probability** (from the Normal Survival Function $1 - \Phi(t)$ or Poisson Cumulative Survival Function).
   - Real-time interactive slider & direct input for the threshold parameter $t$.

3. **Premium Modern Dark-Theme Dashboard**:
   - Dark charcoal & navy palette (`#0B0F19`) with purple, blue, and teal accent gradients.
   - Live KPI metric cards for Sample Size ($N$), Expected Activity ($E[X]$), Dispersion ($\sigma$), Exceedance Probability, and Engagement Tier.
   - Fully responsive on desktop, tablet, and mobile screens.
   - Built-in expandable mathematical viva cheatsheet with formulas for exams and presentations.

4. **Flexible Data Ingestion Modes**:
   - **Preset Scenarios**: One-click selection for *Balanced*, *Low Activity*, *High Activity*, and *Zero-Variance* edge cases.
   - **Custom Manual Observation**: Ingests custom numbers separated by commas, spaces, semicolons, or newlines with real-time observation counter.
   - **Random Synthetic Cohort**: Generates $N=500$ observations using NumPy.

5. **Heuristic Rule-Based Recommendations**:
   - Platform-tailored engagement strategies based on calculated engagement scores and tiers (Low, Moderate, High, Power User).
   - Clearly labeled as an educational heuristic prototype.

---

## 📁 Project Directory Structure

```text
behaviour_insights/
│
├── app.py                   # Flask backend with NumPy & SciPy statistical calculations
├── requirements.txt         # Python dependencies (Flask, NumPy, SciPy)
├── README.md                # Documentation and setup instructions
│
├── templates/
│   └── index.html           # Modern dashboard UI template
│
└── static/
    ├── style.css            # Dark theme styles, glassmorphism, responsive layout
    └── dashboard.js         # Interactive Chart.js rendering and state management
```

---

## 🛠️ Step-by-Step Installation & Running Guide (Windows)

### Prerequisites
- Python 3.10 or newer installed.
- VS Code or Windows PowerShell.

### Step 1: Open Project in Terminal
Open your terminal (PowerShell or VS Code terminal) and navigate into the project folder:
```powershell
cd "f:\Second Year\MATHS\Microproject-website\behaviour_insights"
```

### Step 2: (Optional) Create & Activate Virtual Environment
```powershell
py -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Required Libraries
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Start the Web Application
```powershell
python app.py
```

You should see:
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 5: Open in Your Browser
Open Chrome, Edge, or Firefox and go to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🎓 Viva & Presentation Talking Points

1. **Why do we use continuous distributions for Netflix and Spotify, but Poisson for Amazon?**
   - *Netflix & Spotify:* Watch and listen times are continuous real numbers measuring continuous duration ($X \in [0, \infty)$). The Central Limit Theorem suggests aggregated consumption clusters naturally in a bell-shaped Gaussian distribution.
   - *Amazon:* Product clicks are discrete count events ($k \in \{0, 1, 2, \dots\}$). Discrete events occurring independently in a fixed session window are modelled by the Poisson distribution.

2. **How is the Expected Value estimated?**
   $$\hat{\mu} = \bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i$$
   The sample mean $\bar{x}$ is the minimum-variance unbiased estimator of the population expectation $E[X]$.

3. **What is the difference between Empirical and Model Probability?**
   - *Empirical Probability:* Direct counting of observed data exceeding threshold $t$: $\frac{\text{Count}(x_i \ge t)}{n}$.
   - *Model Probability:* Area under the theoretical probability density function from $t$ to $\infty$:
     $$P(X \ge t) = \int_{t}^{\infty} f(x)\,dx = 1 - \Phi\left(\frac{t-\mu}{\sigma}\right)$$
   - Comparing these two reveals how well the real user data fits the idealized mathematical model.

---

## 🧪 Testing Checklist

- [x] **Netflix Normal PDF:** Verified histogram and fitted Normal PDF overlay reflecting $\mu$ and $\sigma$.
- [x] **Spotify Adaptation:** Dynamically updates when values or presets change.
- [x] **Amazon Poisson PMF:** Displays integer click counts on the x-axis with discrete frequencies and Poisson PMF overlay.
- [x] **Dynamic Submissions:** Different datasets immediately generate distinct visualisations without stale caching.
- [x] **Threshold Recalculation:** Adjusting the threshold slider updates exceedance probabilities in real time.
- [x] **Edge Case Resilience:** Verified zero-variance ($[120, 120, \dots]$) and small sample inputs operate without division-by-zero crashes.
