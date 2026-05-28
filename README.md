# 🏛️ Engineering Impact Dashboard

A hybrid quantitative–qualitative engineering leadership engine that moves beyond naive developer analytics (such as counting commits or lines of code) and instead measures **engineering leverage, intent, and team citizenship**.

This framework scales telemetry relative to active team baselines, filters out low-signal automated activity, rewards high-leverage structural work, and incorporates qualitative leadership impact.

---

# 🧭 Core Philosophy & Pillars

Traditional engineering trackers are often easy to game and can alienate developers. This project evaluates engineering value across four strategic pillars:

## 📦 Execution Baseline

Measures operational scope, complex feature delivery, and high-priority issue resolution.

The engine scans pull request metadata for:

* Critical indicators
* Bug labels and fix signals
* Architectural modifications
* Scope and delivery patterns

---

## 💬 Collaboration & Mentorship

Quantifies engineering leverage and team citizenship.

The framework analyzes code review behavior using a **Substantive Word Filter (>15 words)** to isolate meaningful engineering feedback from low-signal approvals such as:

* "LGTM"
* "Looks good"
* Rubber-stamp reviews

This helps surface engineers contributing thoughtful mentorship and review depth.

---

## 🛑 System Quality

Tracks production stability and defensive engineering practices.

The system introduces a structural accountability layer by applying deduction penalties for:

* Triggered Git reverts
* Avoidable regressions
* Stability-related disruptions

---

## 🤝 Human Touch

A qualitative layer completed by engineering managers to capture high-value leadership signals that repositories cannot measure directly, including:

* Architectural planning
* Team leadership
* Mentorship
* Incident responsiveness
* Availability during unscripted operational escalations

---

# 📐 How the Scoring Engine Works

The scoring model avoids rigid quotas by using **Peer Cohort Normalization**.

Instead of evaluating engineers against fixed thresholds, raw metrics are scaled relative to the strongest contributor (**Peak**) inside a rolling **90-day window**.

This ensures performance expectations adapt naturally to:

* Team velocity
* Product lifecycle stage
* Organizational priorities

### Pillar Component Ratio

```math
Pillar Component Ratio =
Individual Raw Value / Cohort Max Ceiling (90-day Peak)
```

### Impact Score Formula

An engineer’s final score is dynamically calculated across all weighted pillars and capped at **100 points**.

```math
Impact Score =
Σ (Normalized Pillar Strength × Strategy Weight) × 100
```

---

# 🛠️ System Architecture

The ecosystem consists of a lightweight two-tier telemetry pipeline:

```text
        [ GitHub API Engine ]
                 │
                 ▼
 (Extracts Raw Telemetry & Text Filters)
       ┌──────────────────────────┐
       │      fetch_data.py       │
       └──────────────────────────┘
                 │
                 ▼
      (Persists Metrics Matrix)
       ┌──────────────────────────┐
       │ posthog_impact_data.csv  │
       └──────────────────────────┘
                 │
                 ▼
(Dynamic Weights & Normalization Engine)
       ┌──────────────────────────┐
       │   app.py (Streamlit UI)  │
       └──────────────────────────┘
```

## `fetch_data.py`

The ingestion pipeline.

Responsibilities include:

* Connecting to repository APIs
* Parsing pull request labels
* Tracking merge timelines
* Measuring code review comment depth
* Detecting revert activity
* Persisting telemetry into:

```text
posthog_impact_data.csv
```

## `app.py`

The interactive leadership dashboard built using Streamlit.

Responsibilities include:

* Reading telemetry matrices
* Applying normalization logic
* Dynamically adjusting strategy weights
* Re-scoring engineers in real time based on business priorities

---

# 🚀 Quick Start & Installation

## 1. Clone the Repository

```bash
git clone https://github.com/gmrock/engineer-impact.git
cd engineer-impact
```

## 2. Install Dependencies

Ensure you have **Python 3.9+** installed.

Then install the required packages:

```bash
pip install -r requirements.txt
```

## 3. Generate Telemetry Cache

Run the ingestion pipeline:

```bash
python fetch_data.py
```

This step populates:

```text
posthog_impact_data.csv
```

with the underlying telemetry baseline variables.

You may configure environment credentials to connect against production repository APIs.

## 4. Launch the Dashboard

Start the Streamlit application locally:

```bash
streamlit run app.py
```

---

# ⚙️ Strategic Priority Alignment in Practice

Instead of enforcing a rigid definition of engineering impact, the dashboard gives leadership dynamic control through adjustable strategy weights.

## 🚀 Feature Shipping Sprint

Increase **Execution Weight** (`0.50+`) to prioritize:

* Feature throughput
* Fast iteration cycles
* Delivery velocity

---

## 🛡️ System Stability Freeze

Increase **System Quality Weight** (`0.40+`) when reliability becomes the top priority.

This shifts rewards toward engineers who:

* Stabilize production systems
* Reduce regressions
* Prevent reverts
* Slow feature development to improve reliability

---

## 👥 Mentorship & Onboarding Focus

Increase **Collaboration Weight** to recognize engineers investing time in:

* Detailed code reviews
* Technical mentoring
* Structural engineering guidance
* Onboarding support

---

# 🎯 Why This Exists

Most engineering metrics systems optimize for **activity**.

This framework optimizes for **impact**.

Rather than rewarding sheer output volume, it attempts to surface engineers who:

* Create leverage
* Improve system reliability
* Mentor teammates
* Make thoughtful architectural contributions
* Increase overall engineering effectiveness

