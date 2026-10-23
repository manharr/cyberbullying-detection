# Academic Presentation Outline (10–15 Minutes)
## Cyberbullying Detection & Severity Analysis — Four-Member Group

---

## Presentation Structure Overview
* **Total Time**: 12–15 Minutes (approx. 3–4 minutes per member)
* **Format**: Slide Presentation accompanied by Live Web Application Demonstration
* **Target Audience**: MCA Project Evaluation Committee / Faculty Mentors

---

## Slide-by-Slide Allocation

### Section 1: Introduction & NLP Pipeline (Member 1 — 0:00 to 3:30)
* **Slide 1: Title Slide & Project Identity**
  * Title: *Cyberbullying Detection & Severity Analysis using Machine Learning and Explainable NLP*
  * Student Names, MCA Program, Department, and Academic Year.
* **Slide 2: Problem Statement & Motivation**
  * Proliferation of digital harassment, hate speech, and online bullying on social platforms.
  * Limitations of static regex keyword blacklists (easily evaded by spelling variations and obfuscations).
* **Slide 3: Crucial Conceptual Distinction**
  * Automated Toxicity Detection (lexical analysis of an isolated utterance) vs. Interpersonal Cyberbullying (requires repetition, power imbalance, and targeted malice).
* **Slide 4: Dataset Exploration & Integrity Checks**
  * Kaggle Jigsaw Toxic Comment Challenge (159,571 comments, 6 non-exclusive categories).
  * Addressing extreme class imbalance (~10:1 ratio) via stratified splitting.
* **Slide 5: NLP Preprocessing Stages A–E**
  * Text cleaning (HTML, URLs, mentions), tokenization.
  * Stop-word removal with critical preservation of negation words (`not`, `no`, `never`) to avoid negation inversion.
  * WordNet lemmatization vs. Porter stemming.

---

### Section 2: Machine Learning Models & Experimental Findings (Member 2 — 3:30 to 7:00)
* **Slide 6: Feature Engineering (Stage F)**
  * Sublinear TF-IDF vectorization with unigram and bigram vocabularies (12,000 features).
  * Strict training/test separation eliminating data leakage.
* **Slide 7: Candidate Algorithms & Hyperparameters**
  * Logistic Regression with balanced weighting ($w_c = \frac{N}{2 N_c}$).
  * Linear Support Vector Machines with 3-fold Platt scaling for calibrated probabilities.
  * Multinomial Naive Bayes with Laplace smoothing ($\alpha = 0.1$).
* **Slide 8: Benchmark Comparison & Model Selection**
  * Comparison Table on 5,250 validation samples:
    * Linear SVM: **0.8392 Macro F1** (Selected Champion).
    * Logistic Regression: 0.8372 Macro F1.
    * Naive Bayes: 0.8034 Macro F1.
* **Slide 9: Held-Out Test Evaluation & Confusion Matrix**
  * Final evaluation on 5,250 held-out comments: 88.42% accuracy, 0.8385 test Macro F1, 414 true positives.
* **Slide 10: Preprocessing Ablation Study**
  * Proof that Bigram TF-IDF $(1,2)$ provided the highest Macro F1 (0.8247) by capturing phrase context.

---

### Section 3: Explainability, Severity & Backend Architecture (Member 3 — 7:00 to 10:30)
* **Slide 11: Explainable AI (XAI) Mathematics**
  * Additive linear feature contribution: $\text{Contribution}(j) = w_j \times \text{tfidf}_j$.
  * Transparent global coefficient ranking (toxic indicators vs. civil indicators).
* **Slide 12: Transparent Multi-Tier Severity Rubric**
  * Level 0 (None), Level 1 (Low), Level 2 (Moderate), Level 3 (High).
  * Combining confidence, multi-label category activations, and direct threat/hate speech triggers.
* **Slide 13: System Architecture & FastAPI Services**
  * Asynchronous REST API service with Pydantic type safety.
  * Singleton model artifact loader providing sub-10ms inference.
* **Slide 14: Data Tier: SQLite Database Design**
  * Local zero-configuration storage (`cyberbullying.db`).
  * Normalized schema: `analyses`, `moderation_queue`, and `user_feedback`.
  * Streaming CSV batch processing for up to 1,000 rows.

---

### Section 4: Frontend Application, Fairness & Live Demo (Member 4 — 10:30 to 14:00)
* **Slide 15: Frontend Engineering & Design System**
  * React 19 + Vite SPA with Material UI and responsive Recharts.
  * High-contrast sleek dark theme with glassmorphic cards and accessible typography.
* **Slide 16: Live System Demonstration**
  * Single Comment Analyzer: Real-time classification, severity badge, and influential word chips.
  * Interactive NLP Laboratory: Live step-by-step diagnostic inspection across Stages A through F.
  * Batch CSV Analysis & instant classified spreadsheet download.
* **Slide 17: Error Analysis & Algorithmic Fairness**
  * Real false positive and false negative test cases.
  * Demographic subgroup False Positive Rate disparity analysis (measuring unintended bias per Dixon et al.).
* **Slide 18: Human-in-the-Loop Moderation**
  * Reviewing flagged high-severity comments, recording notes, and overriding false positives.
* **Slide 19: Conclusion & Future Scope**
  * Summary of deliverables.
  * Future enhancements: Conversational thread history modeling, multilingual expansion, transformer distillation.
* **Slide 20: References & Q&A Session**
  * Academic citations and committee question-and-answer period.
