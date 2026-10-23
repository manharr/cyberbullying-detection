# System Architecture & Technical Specification
## Cyberbullying Detection & Severity Analysis — Advanced MCA NLP Project

---

## 1. Executive Architecture Overview
The system follows a decoupled, three-tier modular architecture designed for local, reproducible, and resource-efficient execution on standard student laptops without paid external APIs or cloud infrastructure.

```
+------------------------------------------------------------------------------------------------+
|                                    PRESENTATION TIER (REACT SPA)                                |
|  - Modern Vite + React 19 Client with Material UI & Recharts                                   |
|  - 11 Dedicated Pages: Overview, Single Analyzer, Batch CSV, Dashboard Telemetry,              |
|    Analysis History, Model Benchmarks, Explainability (XAI), NLP Lab, Error & Fairness,        |
|    Moderation Queue, About & Methodology                                                       |
+------------------------------------------------------------------------------------------------+
                                           |  HTTP / REST (Proxy /api)
                                           v
+------------------------------------------------------------------------------------------------+
|                                  APPLICATION SERVICES TIER (FASTAPI)                           |
|  - FastAPI ASGI Framework with Pydantic Schema Validation & CORS Middleware                    |
|  - Singleton Model Artifact Loader (Low-latency in-memory cache)                               |
|  - Streaming CSV Ingestion with Batch Slicing & Record Level Safety Triggers                   |
|  - Human Moderation Workflow & Real-time Aggregated Statistics Engine                          |
+------------------------------------------------------------------------------------------------+
         |                                                                      |
         | NLP & Model Inference                                                | SQLite DB Operations
         v                                                                      v
+------------------------------------------+        +--------------------------------------------+
|         MACHINE LEARNING PIPELINE        |        |               DATA TIER (SQLITE)           |
|  - Preprocessing (Clean, Tokenize,       |        |  - Local Persistent Database:              |
|    Negation Stopwords, WordNet Lemmas)   |        |    `cyberbullying.db`                      |
|  - Fitted TF-IDF Vectorizer (1,2 ngrams) |        |  - Indexed Tables:                         |
|  - Calibrated Linear SVM & Logistic Reg  |        |    1. `analyses` (historical records)      |
|  - 6 Multi-label Category Classifiers    |        |    2. `moderation_queue` (flagged cases)   |
|  - Model Explainer & Severity Heuristics |        |    3. `user_feedback` (audits)             |
+------------------------------------------+        +--------------------------------------------+
```

---

## 2. Component Breakdown

### 2.1 Natural Language Processing Pipeline (`ml/src/`)
* **`dataset_loader.py`**: Discovers `train.csv` or safely unpacks `train.csv.zip` within the workspace. Validates schema columns (`id`, `comment_text`, `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`), checks missing data, and creates stratified train (70%), validation (15%), and held-out test splits (15%).
* **`preprocessing.py`**: Implements sequential stages:
  * *Stage A*: Text cleaning (sanitizes HTML tags, strips URLs, user mentions `@user`, IP addresses, and lowercases text).
  * *Stage B*: Tokenization via NLTK word tokenizer.
  * *Stage C*: Stop-word filtering with strict negation preservation (`not`, `no`, `never`, `nor`, `neither`).
  * *Stage D*: WordNet Lemmatization mapping POS tags to normalize grammatical variants.
  * *Stage E*: Porter Stemming for algorithmic suffix comparison.
  * *Stage F*: Vectorization via sublinear TF-IDF (unigram and bigram vocabularies).
* **`train.py`**: Trains Logistic Regression (balanced), Linear SVM (calibrated), and Naive Bayes; evaluates validation Macro F1; selects the champion model; trains multi-label binary relevance heads; evaluates champion model on strictly held-out test set; persists `.joblib` artifacts to `ml/artifacts/`.
* **`compare_models.py`**: Runs 6-stage preprocessing ablation experiments across identical splits.
* **`explain.py`**: Calculates global coefficient rankings and local term additive contributions ($w_i \times \text{tfidf}_i$).
* **`severity.py`**: Implements transparent multi-factor linguistic severity ratings (Levels 0 through 3).
* **`error_analysis.py` & `fairness.py`**: Diagnoses false positives/negatives and evaluates disparate impact across demographic keywords.

### 2.2 FastAPI Backend (`backend/app/`)
* **`core/config.py`**: Centralized configuration management for paths, thresholds, and retention.
* **`database/db.py`**: SQLite database engine utilizing Python's native `sqlite3` driver with foreign key enforcement and indexed queries.
* **`schemas/analysis.py`**: Type-safe Pydantic models for incoming payloads and outgoing responses.
* **`services/nlp_service.py`**: Singleton service loading trained artifacts once at startup to guarantee sub-10ms single comment inference.
* **`main.py`**: RESTful API endpoints for single analysis, CSV batch processing, SQLite telemetry, model metrics, explainability, interactive laboratory diagnostics, and human moderation.

### 2.3 React Single-Page Application (`frontend/src/`)
* Built with Vite, React 19, and Material UI.
* Responsive dark theme utilizing glassmorphic surfaces, custom typography (Plus Jakarta Sans), and responsive charts (Recharts).
* Fully wired to relative backend routes via Vite development proxy (`/api` and `/health` mapped to `http://127.0.0.1:8000`).

---

## 3. Data Flow Diagram (DFD Level 1)

```
[User / Moderator]
        │
        ▼ (Submits Text / Uploads CSV)
[FastAPI Ingestion Endpoint]
        │
        ├─► [NLPPipeline] ──► [TF-IDF Vectorizer (Training Fitted)]
        │                               │
        │                               ▼
        │                  [Trained Linear SVM Model]
        │                               │
        │                               ├─► Binary Toxicity & Confidence
        │                               ├─► Multi-Label Category Heads
        │                               ├─► Additive Term Explanations
        │                               └─► Severity Heuristic Module
        │
        ├─► [SQLite Persistence Engine]
        │         ├─► INSERT INTO `analyses`
        │         └─► IF Severity >= 2: INSERT INTO `moderation_queue`
        │
        ▼
[React UI Rendering & Feedback]
```

---

## 4. Database Schema Design (SQLite)

### Table: `analyses`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique analysis identifier |
| `comment_text` | TEXT | NOT NULL | Sanitized comment text string |
| `is_toxic` | INTEGER | NOT NULL | Binary classification (0 or 1) |
| `confidence` | REAL | NOT NULL | Calibrated probability confidence |
| `primary_class` | TEXT | NOT NULL | 'Toxic' or 'Non-toxic' |
| `estimated_severity` | INTEGER | NOT NULL | Severity rating (0 to 3) |
| `severity_label` | TEXT | NOT NULL | 'None', 'Low', 'Moderate', 'High' |
| `category_scores` | TEXT | NOT NULL | JSON string of 6 category probabilities |
| `influential_words` | TEXT | NOT NULL | JSON string of influential terms |
| `created_at` | TEXT | NOT NULL | ISO 8601 UTC timestamp |

### Table: `moderation_queue`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Moderation queue entry ID |
| `analysis_id` | INTEGER | FOREIGN KEY REFERENCES analyses(id) | Associated analysis link |
| `comment_text` | TEXT | NOT NULL | Flagged text |
| `flagged_reason` | TEXT | NOT NULL | Algorithmic flag description |
| `severity_level` | INTEGER | NOT NULL | Severity score (2 or 3) |
| `status` | TEXT | DEFAULT 'PENDING' | 'PENDING', 'APPROVED', 'REMOVED', 'ESCALATED' |
| `reviewer_notes` | TEXT | NULLABLE | Human moderator justification |
| `reviewed_at` | TEXT | NULLABLE | Timestamp of moderator action |
| `created_at` | TEXT | NOT NULL | Flag creation timestamp |

### Table: `user_feedback`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Feedback record identifier |
| `analysis_id` | INTEGER | FOREIGN KEY REFERENCES analyses(id) | Related analysis link |
| `is_accurate` | INTEGER | NOT NULL | 1 for accurate, 0 for misclassification |
| `suggested_label` | TEXT | NULLABLE | User suggested label |
| `user_comments` | TEXT | NULLABLE | User notes |
| `created_at` | TEXT | NOT NULL | Feedback timestamp |
