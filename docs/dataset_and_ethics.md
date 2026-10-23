# Dataset Disclosures & Ethical Considerations
## Cyberbullying Detection & Severity Analysis

---

## 1. Dataset Overview & Discovery
The dataset employed is the official **Jigsaw Toxic Comment Classification Challenge** dataset hosted on Kaggle:
* **Source**: Alphabet Conversation AI / Jigsaw & Kaggle
* **Original File**: `train.csv` (Size: ~68.8 MB)
* **Total Instances**: 159,571 user comments extracted from Wikipedia Talk Pages
* **Text Column**: `comment_text` (Null count: 0)

### 1.1 Category Distribution & Class Imbalance
The dataset contains non-exclusive multi-label annotations:

| Category | Positive Count | Positive Percentage | Class Imbalance Ratio |
|---|---|---|---|
| `toxic` (Primary Target) | 15,294 | 9.58% | ~9.4 : 1 |
| `severe_toxic` | 1,595 | 1.00% | ~99.0 : 1 |
| `obscene` | 8,449 | 5.29% | ~17.9 : 1 |
| `threat` | 478 | 0.30% | ~332.8 : 1 |
| `insult` | 7,877 | 4.94% | ~19.3 : 1 |
| `identity_hate` | 1,405 | 0.88% | ~112.6 : 1 |

To prevent bias toward the majority class (90.42% non-toxic), the training pipeline applies **stratified sampling** and **balanced class weighting** ($w_c = \frac{N}{2 N_c}$).

---

## 2. Fundamental Conceptual Distinction: Toxicity vs. Cyberbullying

A central academic requirement of this project is explicitly establishing the difference between **automated toxicity detection** and **interpersonal cyberbullying**:

* **Toxicity Detection**: Evaluates whether an isolated text string contains rude, disrespectful, obscene, or threatening language. It is an algorithmic, lexical-semantic classification task evaluated on a single utterance.
* **Cyberbullying**: A complex sociological and psychological phenomenon defined by:
  1. **Repetition**: Persistent, recurring harassment directed at a targeted individual over time.
  2. **Power Imbalance**: An asymmetry in social, emotional, or technological leverage between harasser and victim.
  3. **Intent to Harm**: Deliberate psychological malice.
  4. **Relational Context**: The social dynamic of the parties involved.

> **Academic Notice**:
> An isolated comment labeled "Toxic" does **not** prove legal harassment or established cyberbullying. The system functions as a triage engine to alert human moderation teams, never as an autonomous legal adjudicator.

---

## 3. Algorithmic Bias & Demographic Disparity

As demonstrated by Dixon et al. (AIES 2018), text classifiers trained on public online discussions frequently exhibit **unintended demographic bias**:
* Identity words such as *"gay"*, *"lesbian"*, *"muslim"*, *"jewish"*, and *"black"* frequently co-occur with hateful slurs in public comment boards.
* Consequently, linear and bag-of-words models can assign slightly positive weights to identity terms themselves.
* This causes an elevated False Positive Rate (FPR) on benign sentences containing identity mentions (e.g., *"I am a proud gay woman"* misflagged as toxic).

### Mitigation Measures in This Application:
1. **Fairness Assessment Dashboard**: Continuously measures Subgroup FPR across Religion, Race, Sexual Orientation, and Gender keywords.
2. **Human Moderation Queue**: Low-confidence or identity-flagged comments are triaged for human review before punitive enforcement.
3. **User Inaccuracy Feedback**: Allows moderators and users to register false positives to guide future model retraining.

---

## 4. Privacy & Data Retention Guidelines
* The local SQLite database stores minimal metadata and runs strictly on localhost.
* No data is transmitted to external cloud APIs, tracking servers, or third-party storage.
* Deletion endpoints (`DELETE /api/history/{id}`) perform cascade deletion of historical analyses, moderation records, and user feedback.
