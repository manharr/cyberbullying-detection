# Four-Member Group Technical Deliverables
## Cyberbullying Detection & Severity Analysis — Advanced MCA Major Project

---

## Group Roles & Technical Deliverable Matrix

| Member | Primary Responsibility | Core Technologies | Primary Source Code Files |
|---|---|---|---|
| **Member 1** | NLP Pipeline & Dataset Engineering | Python, NLTK, pandas, regex | `ml/src/dataset_loader.py`<br>`ml/src/preprocessing.py`<br>`ml/tests/test_dataset.py`<br>`ml/tests/test_preprocessing.py` |
| **Member 2** | Machine Learning & Explainable AI | scikit-learn, joblib, NumPy | `ml/src/train.py`<br>`ml/src/explain.py`<br>`ml/src/severity.py`<br>`ml/src/compare_models.py`<br>`ml/tests/test_ml_pipeline.py` |
| **Member 3** | Backend Architecture & SQLite DB | FastAPI, Uvicorn, SQLite, Pydantic | `backend/app/main.py`<br>`backend/app/database/db.py`<br>`backend/app/schemas/analysis.py`<br>`backend/app/services/nlp_service.py`<br>`backend/tests/` |
| **Member 4** | Frontend Development & Integration | React 19, Vite, Material UI, Recharts | `frontend/src/App.jsx`<br>`frontend/src/pages/*`<br>`frontend/src/components/*`<br>`docs/*` |

---

## Detailed Deliverables by Team Member

### Member 1: NLP & Dataset Engineering
1. **Workspace Discovery & Schema Validation**:
   - Implemented automated workspace discovery searching root and subdirectories for `train.csv` and `train.csv.zip`.
   - Built path-traversal-safe ZIP extraction into designated `data/` directory.
   - Enforced strict schema checks verifying expected columns: `id`, `comment_text`, `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`.
   - Generated structured JSON inspection report (`ml/reports/dataset_inspection.json`).
2. **Text Normalization (Stage A)**:
   - Sanitized HTML tags, hyperlinks, IPv4 addresses, and `@user` mentions.
   - Preserved contractions and punctuation necessary for emotional expression.
3. **Tokenization & Stop-word Filtering (Stages B & C)**:
   - Integrated NLTK word tokenization.
   - Configured custom stop-word pruning with strict preservation of negation markers (`not`, `no`, `never`, `nor`, `neither`).
4. **Morphological Reduction (Stages D & E)**:
   - Implemented WordNetLemmatizer with POS tag mapping.
   - Integrated PorterStemmer as an alternative baseline.
5. **Ablation Study (`ml/src/compare_models.py`)**:
   - Designed 6-stage systematic ablation experiments comparing cleaning, stopwords, lemmatization, stemming, unigrams, and bigrams.

### Member 2: ML Modeling & Explainability
1. **TF-IDF Feature Space (Stage F)**:
   - Configured sublinear TF-IDF vectorization with 12,000 maximum features and $(1,2)$ n-gram range.
   - Guaranteed strict separation: fitted vectorizer only on the training set.
2. **Classifier Training & Benchmark (`ml/src/train.py`)**:
   - Trained Logistic Regression (balanced), Linear Support Vector Machines (Calibrated), and Multinomial Naive Bayes.
   - Handled extreme class imbalance (~10:1) via inversely proportional class weighting.
   - Implemented champion selection based on Macro F1 and toxic class F1.
3. **Multi-Label Category Heads**:
   - Trained 6 independent binary relevance classifiers for `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`.
4. **Model-Compatible Explainability (`ml/src/explain.py`)**:
   - Extracted global feature importance from trained linear coefficients.
   - Formulated local additive feature contribution ($w_j \times \text{tfidf}_j$) for specific comment predictions.
5. **Severity Estimation Module (`ml/src/severity.py`)**:
   - Designed 4-tier transparent heuristic (Levels 0 through 3) combining model confidence, category triggers, and threat indicators.

### Member 3: Backend & Database
1. **FastAPI Microservice (`backend/app/main.py`)**:
   - Engineered asynchronous REST API service with CORS middleware and Pydantic validation schemas.
   - Implemented singleton model artifact loader (`NLPModelService`) ensuring sub-10ms inference.
2. **SQLite Local Storage Engine (`backend/app/database/db.py`)**:
   - Designed normalized SQLite schema with 3 tables: `analyses`, `moderation_queue`, and `user_feedback`.
   - Added database indexes on `created_at`, `is_toxic`, and moderation `status`.
   - Developed CRUD helper functions with parameterized SQL preventing injection attacks.
3. **Batch Processing Endpoint (`POST /api/analyze/batch`)**:
   - Built streaming CSV file reader parsing up to 1,000 comments in manageable chunks.
   - Integrated row-level error handling, progress counts, and automatic database persistence.
4. **Human Moderation & Feedback Endpoints**:
   - Built `/api/moderation/queue` and `PATCH /api/moderation/{id}` supporting reviewer status updates (`APPROVED`, `REMOVED`, `ESCALATED`) and notes.

### Member 4: Frontend & System Integration
1. **React Application Architecture (`frontend/src/`)**:
   - Scaffolded Vite + React 19 single-page application with Material UI v6.
   - Implemented custom sleek dark mode theme with glassmorphic cards, custom typography, and responsive layout.
2. **Interactive Educational NLP Laboratory (`frontend/src/pages/NlpLaboratory.jsx`)**:
   - Visualized raw text transitioning sequentially through Stage A (Cleaned), Stage B (Tokens), Stage C (Negation Stopwords), Stage D (Lemmas), Stage E (Stems), and Stage F (TF-IDF Weights).
3. **Telemetry & Dashboard Analytics (`frontend/src/pages/AnalyticsDashboard.jsx`)**:
   - Constructed interactive Recharts visualizations: toxicity donut chart, severity histogram, and category bar chart.
4. **Model Benchmark & Explainability UI**:
   - Built interactive local attribution sandbox displaying term-by-term contribution polarity chips.
   - Displayed held-out test confusion matrix and preprocessing ablation comparison tables.
5. **System Documentation & Group Presentation**:
   - Authored complete architecture, methodology, dataset disclosures, testing reports, and 10-15 minute group slide outline.
