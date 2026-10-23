# NLP Methodology & Algorithmic Formulation
## Cyberbullying Detection & Severity Analysis

---

## 1. Natural Language Processing Pipeline

### Stage A — Text Sanitization & Cleaning
Online user comments contain substantial noise including HTML formatting tags, hyperlink references, user mentions, IP addresses, and irregular typography. The text cleaner normalizes text as follows:
1. Replaces HTML tags using regular expression `r"<[^>]+>"`.
2. Strips URLs via `r"https?://\S+|www\.\S+"`.
3. Strips mentions `@username` and IPv4 addresses to preserve user privacy and prevent overfitting to specific handles.
4. Normalizes casing to lowercase.
5. Replaces non-standard punctuation while preserving apostrophes for contractions (e.g., `don't`, `can't`) and sentence termination markers.
6. Collapses contiguous whitespace.

### Stage B — Tokenization
Text strings are segmented into discrete linguistic tokens using NLTK's standard `word_tokenize`, with a regex-based fallback `r"\b[\w']+\b|[!?]"`.

### Stage C — Stop-Word Pruning with Negation Protection
Standard English stop-word lexicons include terms such as *"not"*, *"no"*, *"never"*, *"neither"*, and *"nor"*. In sentiment analysis and toxic language detection, stripping negation terms causes **negation inversion**, wherein an utterance like *"I am not bad"* is reduced to *["bad"]*, triggering an erroneous false positive.
Our pipeline filters high-frequency grammatical words (e.g., *"the"*, *"is"*, *"at"*) while explicitly retaining the `NEGATION_WORDS` set:
$$\mathcal{S}_{\text{applied}} = \mathcal{S}_{\text{NLTK}} \setminus \{\text{not}, \text{no}, \text{never}, \text{nor}, \text{neither}, \text{none}, \dots\}$$

### Stage D & E — Lemmatization vs. Stemming
* **WordNet Lemmatization**: Uses WordNet lexical databases to map morphological variations to valid dictionary base forms (lemmas), e.g., *"bullies"* $\to$ *"bully"*. POS tagging is supported for fine-grained morphological disambiguation.
* **Porter Stemming**: Operates via iterative heuristic suffix stripping rules, e.g., *"connected"* $\to$ *"connect"*, but produces non-dictionary stems like *"bulli"*.
Our empirical ablation experiments demonstrate that WordNet lemmatization preserves semantic clarity without vocabulary corruption.

### Stage F — Vectorization via Term Frequency-Inverse Document Frequency (TF-IDF)
To map discrete token strings to numerical feature vectors, we compute sublinear TF-IDF over unigram and bigram ranges:
$$\text{TF}(t, d) = 1 + \ln(f_{t,d}) \quad \text{for } f_{t,d} > 0$$
$$\text{IDF}(t, D) = \ln\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$
The resulting sparse vectors are normalized using the Euclidean norm ($\ell_2$).
**Data Discipline Rule**: The `TfidfVectorizer` is strictly fitted exclusively on the training split $\mathcal{D}_{\text{train}}$ and subsequently transformed on validation $\mathcal{D}_{\text{val}}$ and test sets $\mathcal{D}_{\text{test}}$, completely eliminating data leakage.

---

## 2. Machine Learning Classifiers

### 2.1 Logistic Regression with Balanced Weighting
Optimizes log-loss with $\ell_2$ regularization:
$$\min_{\mathbf{w}, b} \frac{1}{2} \|\mathbf{w}\|_2^2 + C \sum_{i=1}^N w_i^{\text{class}} \log\left(1 + \exp(-y_i (\mathbf{w}^T \mathbf{x}_i + b))\right)$$
To overcome the ~10:1 class imbalance present in toxicity datasets, sample weights are inversely proportional to class frequencies:
$$w_c = \frac{N}{2 \times N_c}$$

### 2.2 Linear Support Vector Machine (LinearSVC with Calibration)
Finds the maximum margin separating hyperplane minimizing hinge loss:
$$\min_{\mathbf{w}, b} \frac{1}{2} \|\mathbf{w}\|_2^2 + C \sum_{i=1}^N \max(0, 1 - y_i(\mathbf{w}^T \mathbf{x}_i + b))$$
Because standard SVM decision boundaries produce uncalibrated distance scores, we employ **Platt Scaling** via `CalibratedClassifierCV` using 3-fold cross validation:
$$P(y=1|\mathbf{x}) = \frac{1}{1 + \exp(A \cdot f(\mathbf{x}) + B)}$$
where $f(\mathbf{x})$ is the linear decision score.

### 2.3 Multinomial Naive Bayes
Applies Bayes' theorem under conditional independence:
$$P(c|\mathbf{x}) \propto P(c) \prod_{j=1}^V P(t_j|c)^{x_j}$$
with Laplace smoothing parameter $\alpha = 0.1$.

---

## 3. Explainable AI: Feature Attribution
For linear classifiers, the final decision score is an additive linear combination of feature weights:
$$f(\mathbf{x}) = b + \sum_{j \in \text{active}} w_j \cdot x_j$$
We compute the local contribution of each word $j$ present in comment $\mathbf{x}$:
$$\text{Contribution}(j) = w_j \times x_j$$
* If $\text{Contribution}(j) > 0$: The word pushes the classification toward **Toxic**.
* If $\text{Contribution}(j) < 0$: The word mitigates the classification toward **Non-toxic**.

---

## 4. Multi-Factor Severity Estimation Rubric

Severity is evaluated through a transparent, documented rubric combining calibrated model confidence, multi-label category activations, and linguistic threat triggers:

| Level | Severity Label | Trigger Criteria | Action Recommendation |
|---|---|---|---|
| **0** | **None** | Predicted non-toxic ($P(\text{toxic}) < 0.50$) | No action required |
| **1** | **Low** | Mild toxic ($P \ge 0.50$) without threats, identity slurs, or obscenity | Standard logging / down-ranking |
| **2** | **Moderate** | Multiple toxic categories active, obscenity + insult $\ge 0.50$, or confidence $\ge 0.85$ | Automatic triage to human moderation queue |
| **3** | **High** | Direct threats ($P(\text{threat}) \ge 0.40$), identity hate speech ($P(\text{hate}) \ge 0.40$), or extreme toxicity ($P(\text{severe}) \ge 0.50$) | Immediate comment removal; safety review |
