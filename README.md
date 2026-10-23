# Cyberbullying Detection & Severity Analysis
### Advanced MCA NLP Major Project — Four-Member Group

A complete, production-grade Natural Language Processing (NLP) and Machine Learning system for automated online toxic language detection, multi-label abuse category scoring, rule-grounded severity triage, term-level explainable AI (XAI), and human-in-the-loop moderation.

---

## 📌 Project Overview
Online communication platforms are increasingly vulnerable to abusive language, hate speech, and digital harassment. This application leverages supervised statistical machine learning models trained on the official **Kaggle Jigsaw Toxic Comment Classification Challenge** dataset (159,571 comments) to provide transparent, low-latency linguistic analysis.

### Core Capabilities:
1. **Single-Comment Triage**: Instant binary classification (Toxic vs. Non-toxic) and calibrated confidence scoring.
2. **Multi-Label Abuse Profiling**: Probability estimates across 6 distinct toxicity sub-categories: *Toxic*, *Severe Toxic*, *Obscene*, *Threat*, *Insult*, and *Identity Hate*.
3. **Four-Tier Severity Rating**: Documented heuristic triage (Level 0: None, Level 1: Low, Level 2: Moderate, Level 3: High) for automated content flagging.
4. **Explainable AI (XAI)**: Additive linear feature contributions ($w_i \times \text{tfidf}_i$) revealing exact token-level impact.
5. **Interactive NLP Laboratory**: Live educational workbench inspecting intermediate representations across all syllabus preprocessing stages.
6. **Batch CSV Ingestion**: Stream-processing of comment datasets with instant CSV export of predictions.
7. **SQLite Persistence & Telemetry**: Local database storage without cloud credentials or paid external APIs.
8. **Error & Algorithmic Fairness Analysis**: Empirical diagnosis of false positives, false negatives, and demographic subgroup bias (Dixon et al. 2018).
9. **Human Moderation Queue**: Triage interface for reviewing, approving, or escalating severe content flags.

---

## 👥 Four-Member Group Technical Deliverables

| Member | Primary Role | Key Deliverables |
|---|---|---|
| **Member 1** | NLP Pipeline & Dataset | Dataset discovery & validation, Stage A text cleaning, Stage B tokenization, Stage C negation-preserving stop-words, Stage D/E lemmatization & stemming, 6-stage ablation study. |
| **Member 2** | ML Modeling & Explainability | Sublinear TF-IDF vectorization, Logistic Regression, Linear SVM (Calibrated), Naive Bayes, Multi-label category heads, additive feature attribution ($w_j \times \text{tfidf}_j$), severity rubric. |
| **Member 3** | Backend & Database | FastAPI REST microservice, SQLite schema & indexes (`analyses`, `moderation_queue`, `user_feedback`), in-memory artifact caching, batch CSV streaming parser, moderation endpoints. |
| **Member 4** | Frontend & System Integration | React 19 + Vite SPA, Material UI dark theme design system, Recharts visualizations, interactive NLP Laboratory, error & fairness presentation, academic documentation & presentation outline. |

---

## 🚀 Quick Start Guide

### Prerequisites
* **Python**: 3.10+ (Tested on Python 3.11.8)
* **Node.js**: v18+ (Tested on Node v24.11.0 / npm 11.6.1)

---

### Step 1: Install Python Dependencies
From the project root:
```bash
python -m pip install -r backend/requirements.txt
```

---

### Step 2: Model Training & Verification (Pre-trained Artifacts Included)
All model artifacts are already trained on genuine dataset records and saved in `ml/artifacts/`.
To re-run training or generate fresh empirical reports:
```bash
# Trains models and generates reports in ml/reports/
python ml/src/train.py --sample-size 35000

# Runs preprocessing ablation experiments
python ml/src/compare_models.py

# Runs error analysis and fairness diagnostics
python ml/src/error_analysis.py
python ml/src/fairness.py
```

---

### Step 3: Run Automated Test Suite (26 Passing Tests)
Run all machine learning and backend integration tests:
```bash
# Run ML tests (13 tests)
python -m pytest ml/tests

# Run Backend & API tests (13 tests)
python -m pytest backend/tests
```

---

### Step 4: Start the FastAPI Backend
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
* Backend API Health Check: `http://127.0.0.1:8000/health`
* Interactive OpenAPI Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

---

### Step 5: Start the React Frontend
In a separate terminal window:
```bash
cd frontend
npm run dev
```
Open your browser at: **`http://localhost:5173`**

---

## 📂 Project Structure

```
d:\NLP Project\
├── train.csv                      # Original Jigsaw challenge dataset (159,571 rows)
├── backend/
│   ├── app/
│   │   ├── core/config.py         # Application settings
│   │   ├── database/db.py         # SQLite connection & CRUD operations
│   │   ├── schemas/analysis.py    # Pydantic validation schemas
│   │   ├── services/nlp_service.py # In-memory model artifact loader & inference
│   │   └── main.py                # FastAPI REST endpoints
│   ├── requirements.txt           # Backend dependencies
│   └── tests/                     # Automated API and database tests
├── ml/
│   ├── artifacts/                 # Saved .joblib models & TF-IDF vectorizers
│   ├── reports/                   # Empirical JSON evaluation & benchmark reports
│   ├── src/
│   │   ├── dataset_loader.py      # Dataset discovery, schema validation & splits
│   │   ├── preprocessing.py       # Stages A-F: Cleaning, tokens, stopwords, lemmas
│   │   ├── train.py               # ML training & held-out test evaluation
│   │   ├── compare_models.py      # Preprocessing ablation study
│   │   ├── explain.py             # Feature attribution & global coefficients
│   │   ├── severity.py            # Multi-tier severity heuristics
│   │   ├── error_analysis.py      # False positive & false negative diagnostics
│   │   └── fairness.py            # Demographic subgroup bias assessment
│   └── tests/                     # Automated ML pipeline tests
├── frontend/
│   ├── src/
│   │   ├── api/client.js          # Axios API client
│   │   ├── components/            # Navbar, Sidebar, SeverityBadge
│   │   ├── pages/                 # 11 Dedicated application pages
│   │   ├── App.jsx                # Main application wrapper & theme
│   │   └── index.css              # Custom styling & glassmorphism variables
│   ├── package.json
│   └── vite.config.js             # Vite proxy configuration
└── docs/
    ├── architecture.md            # System architecture, DFD & database design
    ├── methodology.md             # NLP preprocessing, algorithms & mathematical formulations
    ├── dataset_and_ethics.md      # Kaggle dataset disclosures & ethics
    ├── experiments.md             # Empirical benchmark tables & ablation results
    ├── team_contributions.md      # 4-Member technical deliverable breakdown
    ├── testing_report.md          # Complete automated testing report
    └── presentation_outline.md    # 10-15 minute group presentation slide outline
```

---

## 📊 Empirical Results Summary

* **Champion Classifier**: Calibrated Linear Support Vector Machine
* **Held-Out Test Accuracy**: **88.42%**
* **Validation Macro F1**: **0.8392**
* **Inference Latency**: Sub-10 milliseconds per comment on standard CPU

---

## 📜 Academic References
1. L. Dixon, J. Li, J. Sorensen, N. Thain, and L. Vasserman, "Measuring and Mitigating Unintended Bias in Text Classification," in *Proc. AIES*, 2018.
2. D. Borkan, L. Dixon, J. Sorensen, N. Thain, and L. Vasserman, "Nuanced Metrics for Measuring Unintended Bias with Real-world Applications for AI in Social Computing," in *Companion Proc. WWW*, 2019.
3. Z. Waseem and D. Hovy, "Hateful Symbols or Hateful People? Predictive Features for Hate Speech Detection on Twitter," in *Proc. NAACL*, 2016.
4. T. Davidson, D. Bhattacharya, and I. Weber, "Automated Hate Speech Detection and the Problem of Offensive Language," in *Proc. ICWSM*, 2017.
