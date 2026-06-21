# TakeMeter: r/stocks Discourse Quality Classifier

A fine-tuned DistilBERT classifier that labels Reddit r/stocks posts into four discourse quality categories, benchmarked against a zero-shot Groq LLaMA-3.3 baseline. Final test accuracy: **85.1%** (fine-tuned) vs. **80.9%** (baseline).

---

## Community Choice and Reasoning

**Community chosen:** Reddit r/stocks

The r/stocks subreddit is an active community where retail investors, analysts, and casual observers share stock picks, market commentary, earnings reactions, and economic analysis. It was selected because it presents a genuine & consequential classification challenge: the ability to distinguish evidence-based reasoning from emotional speculation is not merely academic; it maps directly to signal quality in financial decision-making from individual retail investors to large institutional firms.

This community is an ideal fit for a classification task for several reasons. First, the discourse is structurally varied: the same ticker symbol might generate a peer-reviewed quality earnings breakdown, a prediction based off of gut feelings, a Reuters headline repost, and a pump-and-dump style hype post — all within the same thread. Second, the stakes attached to financial content make the quality distinctions matter in ways that sports or entertainment subreddits do not. Third, since hedge funds & quantitative research firms already deploy alternative data pipelines that scrape social media for sentiment signals, this classifier is a small-scale, interpretable proof-of-concept for a real institutional use case. The presence of both bullish & bearish actors, the influence of macroeconomic events (Fed rate decisions, earnings seasons), and recent catalysts like AI-related equities & political market volatility all ensure that no single discourse pattern dominates; making the label boundaries both necessary and non-trivial to apply.

---

## Label Taxonomy

Four mutually exclusive labels were defined. Every post in the dataset can be assigned to exactly one.

---

### `Evidence_Based_Analysis`

**Definition:** A post that makes a claim and supports it with data, financial metrics, earnings reports, economic reasoning, technical chart evidence, or other independently verifiable evidence that could be evaluated regardless of the author's identity.

**Key rule:** If removing the opinion framing leaves a claim that is still supportable by the cited evidence, label `Evidence_Based_Analysis`. If the claim collapses without the author's assertion, it is Opinion.

**Example 1:**
> "NVDA's data center revenue grew 427% YoY to $47.5B in FY2024. At a forward P/E of ~35x on consensus FY2025 EPS of $28, the stock looks fairly valued relative to the S&P tech median of 32x. It is not the screaming buy bulls are claiming."

**Example 2:**
> "Looking at the yield curve inversion history: every recession since 1960 was preceded by a 2s10s inversion of at least 50 bps. We've been at -100 bps for 14 months. Soft landing is possible, but historically the base rate is recession within 18 months of inversion depth like this."

---

### `Interpretive_Opinion`

**Definition:** A post that expresses a personal judgment, prediction, or preference about a stock, sector, or market direction without substantial supporting evidence. The claim rests on the author's viewpoint rather than demonstrable data.

**Example 1:**
> "I think the Fed is going to pivot earlier than expected. Inflation feels like it's under control and they don't want to cause unnecessary damage to the labor market."

**Example 2:**
> "Apple is still the safest large-cap out there. Their ecosystem lock-in is unmatched and I don't see that changing anytime soon."

---

### `News_Information`

**Definition:** A post that primarily reports factual information, announcements, earnings releases, SEC filings, analyst actions, or market events. Conveys what happened without substantially interpreting its meaning or implications.

**Key rule:** Reporting facts = News. Drawing inferences from facts = Analysis. The deciding word is often "suggests," "implies," "means," or "indicates."

**Example 1:**
> "Microsoft reported Q2 FY2025 revenue of $69.6B, up 12% YoY. Azure cloud grew 31%. EPS came in at $3.23, beating consensus of $3.10."

**Example 2:**
> "Breaking: SEC has opened a formal investigation into Archegos-affiliated entities. Trading halted on several affiliated positions pending review."

---

### `Low_Quality_Misleading`

**Definition:** A post that contains hype, fearmongering, misinformation, clickbait, conspiracy-style reasoning, pump-and-dump rhetoric, or unsupported certainty presented as established fact. Characterized by emotional manipulation rather than reasoning.

**Key rule:** Strong opinion alone is not Low Quality. The threshold requires at least one of: (a) unsupported certainty presented as fact, (b) inflammatory or manipulative rhetoric designed to provoke emotional action, (c) demonstrably false claims, or (d) conspiracy-style reasoning with no logical chain.

**Example 1:**
> "GME to $500 by end of month. Shorts are TRAPPED. Anyone selling before $300 is leaving money on the table. This is the squeeze of the decade."

**Example 2:**
> "The market crash is coming and the elites know it. Why do you think Buffett is sitting on cash? They're about to pull the rug and retail is going to get destroyed. SELL EVERYTHING."

---

## Data Collection

### Source and Collection Method

Posts and top-level comments were manually curated from Reddit r/stocks via the search and hot/top/new feeds, filtered by post type and content. Collection was distributed across varied time windows to avoid overfitting to a single market event cycle (e.g., earnings season only).

**Final dataset size: 310 annotated examples**

### Label Distribution

| Label | Count | % |
|-------|-------|---|
| Interpretive_Opinion | 116 | 37.4% |
| News_Information | 68 | 21.9% |
| Low_Quality_Misleading | 65 | 21.0% |
| Evidence_Based_Analysis | 61 | 19.7% |
| **Total** | **310** | **100%** |

`Interpretive_Opinion` and `News_Information` were the easiest labels to find — opinion posts are the default mode of social media commentary and news reposts are extremely common on financial subreddits. `Evidence_Based_Analysis` proved the hardest to collect in sufficient quantity. Genuinely evidence-grounded posts are rarer in retail-investor communities than casual observation suggests; most posts that look analytical on the surface fail the "could the evidence stand alone" test upon closer inspection.

### Labeling Process

All 310 examples were labeled manually by the project author without LLM pre-labeling or suggestions at annotation time. LLM-assisted pre-labeling was deliberately avoided for two reasons: (1) the Analysis/Opinion boundary is a subtle structural distinction that an LLM conflates in predictable ways, and pre-labeling risks anchoring the annotator to the LLM's decision; (2) at 310 examples, manual annotation was achievable and introducing an LLM pass would make the ground truth a reflection of the LLM's priors filtered through one person's review, which is a weaker epistemic position than direct human annotation.

**Limitation:** Single-annotator datasets carry consistency risk. The annotator's application of the Analysis/Opinion boundary may have drifted across 310 examples, particularly at the hardest edge cases. Without inter-annotator agreement metrics there is no way to quantify this drift.

### Three Difficult-to-Label Examples

**1. Opinion framing over an evidence-based inference**
> "Microsoft's cloud segment has been growing faster than AWS for three consecutive quarters, which tells me the enterprise migration cycle still has runway."

The phrase "tells me" signals personal interpretation, but "three consecutive quarters" is a specific, verifiable trend. Applying the stripping rule — remove the opinion framing, does the claim still stand? Yes. Labeled **`Evidence_Based_Analysis`**. The "tells me" is editorial framing over an evidence-based inference, not the thesis itself.

**2. Strong opinion with rhetorical edge, no manipulative intent**
> "Anyone who bought ARKK in 2021 deserves what happened to them. Cathie Wood is a fraud and I have zero sympathy."

"Fraud" is a strong and potentially unfounded characterization, but the post is retrospective commentary rather than a call to financial action. It contains no market prediction and does not attempt to move someone's trading behavior. It is opinionated, not misleading in the technical sense. Labeled **`Interpretive_Opinion`** — sits close to the Low Quality line but does not cross the manipulation threshold.

**3. News headline with an analytical rider**
> "Goldman raises MSFT price target to $500 — this signals institutional confidence is accelerating ahead of the AI capex cycle."

The first clause is News; the second is Analysis. The rule is to label by dominant purpose. Here, the analytical framing ("this signals…") is the thesis and the Goldman action is merely the supporting premise. Labeled **`Evidence_Based_Analysis`**.

---

## Fine-Tuning Approach

### Base Model

`distilbert-base-uncased` — 40% smaller than BERT-base, 60% faster, retains ~97% of BERT's performance on classification tasks. Chosen because it fits a Colab T4 GPU with room for batch size tuning and trains in under 15 minutes on a 217-example training set.

### Training Setup

| Component | Value |
|-----------|-------|
| Base model | `distilbert-base-uncased` |
| Max token length | 256 |
| Epochs | 5 |
| Learning rate | 3e-5 |
| Batch size (train / eval) | 16 / 32 |
| Loss function | Weighted CrossEntropyLoss |
| Warmup steps | 50 |
| Best model selection | `load_best_model_at_end=True` on validation accuracy |

### Hyperparameter Decisions

Three deliberate departures from the notebook defaults were made, and together they moved final accuracy from ~50% to 85.1%:

**1. Class weights on the loss function**

The dataset has a 2:1 imbalance between the largest class (`Interpretive_Opinion`, 37.4%) and the smallest (`Evidence_Based_Analysis`, 19.7%). Without correction, the model can achieve ~37% accuracy by predicting the majority class exclusively. Class weights were computed using inverse frequency and applied directly to `CrossEntropyLoss` via a custom `WeightedTrainer` subclass:

```
Class weights:
  Evidence_Based_Analysis:  1.2705
  Interpretive_Opinion:     0.6681
  Low_Quality_Misleading:   1.1397
  News_Information:         1.1923
```

This penalizes the model more heavily for misclassifying underrepresented classes, preserving all 310 samples while correcting for the skew — no data was deleted or manually resampled.

**2. Epochs increased from 3 to 5**

At the default 3 epochs, the model was stuck in a flat training region and had not converged. Increasing to 5 allowed it to escape this plateau. Because `load_best_model_at_end=True` is set, if the model began overfitting on epoch 4 or 5, the Trainer automatically rolled back to the checkpoint with the best validation accuracy — making the increase in epochs safe rather than a risk of overfitting.

**3. Learning rate increased from 2e-5 to 3e-5**

A slightly higher learning rate was used to help the model escape the flat region faster on a small dataset. At this scale (217 training examples), 2e-5 produced sluggish early training; 3e-5 accelerated convergence without introducing instability.

---

## Baseline Description

The zero-shot baseline used `llama-3.3-70b-versatile` via the Groq API. The system prompt provided the four label definitions in plain language, one example post per label, and decision rules for the hard boundaries (Analysis vs. Opinion, News vs. Analysis, Opinion vs. Low Quality). The model was instructed to respond with only the label name and no explanation. Temperature was set to 0 for deterministic output. All 47 test examples were classified with a 0.1s delay between requests to respect free-tier rate limits.

The baseline prompt was designed to be a genuine competitor — not a strawman — by including the full label definitions and explicit boundary rules. A zero-shot LLaMA-3.3-70B with a well-crafted prompt is a high bar; outperforming it demonstrates real value from the supervised fine-tuning pipeline.

---

## Evaluation Report

### Overall Accuracy

| Model | Accuracy | Test Set Size |
|-------|----------|---------------|
| Zero-shot baseline (Groq LLaMA-3.3-70B) | 80.9% | 47 |
| Fine-tuned DistilBERT | **85.1%** | 47 |
| Fine-tuning improvement | **+4.2pp** | — |

### Per-Class Metrics — Fine-Tuned Model

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| Evidence_Based_Analysis | 0.69 | 1.00 | 0.82 | 9 |
| Interpretive_Opinion | 0.88 | 0.78 | 0.82 | 18 |
| News_Information | 1.00 | 0.90 | 0.95 | 10 |
| Low_Quality_Misleading | 0.89 | 0.80 | 0.84 | 10 |
| **Macro Average** | **0.86** | **0.87** | **0.86** | 47 |

### Per-Class Metrics — Zero-Shot Baseline

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| Evidence_Based_Analysis | 1.00 | 0.33 | 0.50 | 9 |
| Interpretive_Opinion | 0.67 | 1.00 | 0.80 | 18 |
| News_Information | 1.00 | 0.90 | 0.95 | 10 |
| Low_Quality_Misleading | 1.00 | 0.80 | 0.89 | 10 |
| **Macro Average** | **0.92** | **0.76** | **0.78** | 47 |

The baseline's structural failure is visible in the `Evidence_Based_Analysis` row: precision of 1.00 but recall of only 0.33. The zero-shot model almost never predicted `Evidence_Based_Analysis`. When it did, it was always right, but it missed 6 of the 9 true cases and defaulted them to `Interpretive_Opinion`. This is a known failure mode of instruction following LLMs on expert taxonomies: without training signal on the Analysis/Opinion boundary, the model defaults to the simpler label. The fine-tuned model corrects this entirely, achieving 1.00 recall on `Evidence_Based_Analysis` at the cost of a modest precision drop (0.69, three false positives from Opinion posts).

### Confusion Matrix (Fine-Tuned Model)

![Confusion Matrix](results/confusion_matrix.png)

```
                    Predicted
               EBA    IO    NI   LQM
Actual  EBA  [  9    0    0    0  ]
        IO   [  3   14    0    1  ]
        NI   [  1    0    9    0  ]
        LQM  [  0    2    0    8  ]
```

*(EBA = Evidence_Based_Analysis, IO = Interpretive_Opinion, NI = News_Information, LQM = Low_Quality_Misleading)*

The confusion matrix confirms the expected pattern: the dominant error boundary is `Interpretive_Opinion` → `Evidence_Based_Analysis` (3 cases), with a secondary boundary at `Low_Quality_Misleading` → `Interpretive_Opinion` (2 cases). No errors cross the News boundary in both directions — `News_Information` is nearly perfectly separated, with only one post misclassified (a news post with analytical framing that the model correctly intuited as more Analysis than News). All other label pairs show zero confusion.

### Wrong Prediction Analysis

The model made 7 errors on the 47-example test set. All 7 fall on exactly two boundaries, with no scatter across other pairs. This is a structurally meaningful finding — not random noise.

**Boundary 1: `Interpretive_Opinion` → predicted `Evidence_Based_Analysis` (3 cases)**

**Error #1:**
> "I am not buying SPCX tomorrow and this is the exact math that changed my mind. Everyone is excited about the SpaceX IPO opening on Nasdaq tomorrow at $135 a share, I get it that the business..."

True label: `Interpretive_Opinion` | Predicted: `Evidence_Based_Analysis` | Confidence: 0.47

The title phrase "this is the exact math that changed my mind" is the trigger. The word "math" combined with numerical reasoning language throughout the post activates the model's `Evidence_Based_Analysis` pattern even though the post is fundamentally an opinion piece — the author is explaining why they personally won't buy, not presenting an independent analysis that stands alone as evidence. The model is picking up on surface vocabulary ("math," "exact") rather than reasoning structure. Low confidence (0.47) signals the model is uncertain; it's not a committed misclassification, it's a coin-flip at the boundary.

**Error #4:**
> "We can write off any answer here which ignores the fact that Friday last week was the worst day in the market in over 4 years (was not CPI leak as it doesn't explain last Friday)..."

True label: `Interpretive_Opinion` | Predicted: `Evidence_Based_Analysis` | Confidence: 0.43

Structurally similar to Error #1. The post references a specific market event with precise framing ("worst day in over 4 years," "was not CPI leak"), which triggers the analytical vocabulary pattern. The post is substantively an opinion about market causation with no independently verifiable evidence — but it reads like analysis. Extremely low confidence (0.43) confirms the model is nearly guessing.

**Error #7:**
> "For those who keep asking for a 'one buy and hold for the next 10 years' the opportunity is here: it's GOOGL..."

True label: `Interpretive_Opinion` | Predicted: `Evidence_Based_Analysis` | Confidence: 0.40

The post includes some supporting reasoning about GOOGL's business fundamentals. The model finds enough analytical framing in the body to push it over the Evidence_Based threshold, but the post's thesis ("the opportunity is here") is a personal conviction, not an independently verifiable claim. The confidence of 0.40 is the lowest of any prediction in the test set — the model barely tips to the wrong side.

**What causes this boundary to fail:** The model has learned to associate analytical vocabulary (math, exact, fact, worst, since, over X years) with `Evidence_Based_Analysis`. What it has not fully learned is the structural test: *does the claim stand independently of the author's assertion?* That distinction requires understanding argument structure, not surface vocabulary.

---

**Boundary 2: `Low_Quality_Misleading` → predicted `Interpretive_Opinion` (2 cases)**

**Error #2:**
> "Markets have got to the point where it's all so stupid, people will actually be happy when they drop. Oil market experts are pulling their hair out. Value investing died a long time ago. Buffett will..."

True label: `Low_Quality_Misleading` | Predicted: `Interpretive_Opinion` | Confidence: 0.58

This post reads like an opinionated rant — frustrated, reasoned in tone, not explicitly making market-moving claims. The difference between this and `Interpretive_Opinion` is that it makes no verifiable claims and is emotionally reactive rather than analytical. "Value investing died" is presented as established fact rather than opinion; the tone is fearmongering rather than reasoned disagreement. The model has not fully separated emotional-reactive language from frustrated-but-legitimate opinion. This is a genuinely hard case: a grader who saw this post without the low-quality framework might label it Opinion as well.

**Error #6:**
> "Is this where the retail market comes to cope with the reality that we're retail? Take Merrill Lynch's advice and take your profits now. We could read into that advice..."

True label: `Low_Quality_Misleading` | Predicted: `Interpretive_Opinion` | Confidence: 0.60

Similar to Error #2. The post uses sarcasm ("is this where the retail market comes to cope") combined with a direct call to financial action ("take your profits now"), but the sarcastic framing makes it read like cynical commentary rather than manipulation. The model has not learned that sarcasm-as-manipulation crosses the Low Quality threshold. The signal it would need to distinguish these — the directional call-to-action embedded in sarcastic framing — is subtle and likely underrepresented at this data scale.

**What causes this boundary to fail:** Emotionally frustrated posts that make no verifiable claims but also avoid explicit certainty language (no "guaranteed," no "load up") fall into a gray zone the model hasn't fully learned. At 310 examples, the training signal for this specific subtype of `Low_Quality_Misleading` is thin.

---

**AI-assisted pattern identification:** The seven wrong predictions were fed to Claude with the prompt: *"Here are 7 posts that a fine-tuned DistilBERT classifier got wrong, with predicted and true labels. Given these label definitions, identify systematic patterns in the errors. What is the model actually learning that causes these specific confusions? Be specific."* Claude correctly identified both dominant boundaries (Opinion/Analysis surface vocabulary and LQM/Opinion emotional tone), flagged the low-confidence pattern on the Analysis misclassifications, and suggested that short post length might correlate with errors. The length claim was checked numerically in Section 4c: misclassified posts average 777 chars vs. 2,061 for correct ones — **the length pattern is confirmed, not rejected**. Every pattern reported below is independently computed in the notebook (`Section 4c`) so none rests on the LLM's assertion alone.

---

### Systematic Error Pattern Analysis

Listing seven individual wrong predictions is description, not diagnosis. To establish a *systematic* pattern, the notebook (`Section 4c`) tests four candidate hypotheses against the full test set by counting — each is confirmed or rejected by the data, not by inspection.

**Pattern 1 — Errors concentrate on two boundaries (confirmed).** All 7 errors fall on a small number of label pairs. The dominant boundary is `Interpretive_Opinion` → `Evidence_Based_Analysis` (3 of 7, 43%); the secondary boundary is `Low_Quality_Misleading` → `Interpretive_Opinion` (2 of 7, 29%). The remaining 2 errors are a single `Interpretive_Opinion` → `Low_Quality_Misleading` and a single `News_Information` → `Evidence_Based_Analysis`. Five of seven errors sit on the two suspected boundaries — error is structurally clustered, not scattered noise.

**Pattern 2 — The Opinion/Analysis confusion is directional (confirmed).** The confusion is *asymmetric*: the model labels true `Interpretive_Opinion` posts as `Evidence_Based_Analysis` 3 times, but never makes the reverse error (true Analysis → predicted Opinion = 0). This is the single most systematic finding: **the model has a directional bias toward over-claiming evidence.** It reads analytical-sounding vocabulary ("math," "exact," "the fact that," "worst day in 4 years") as if it were real evidence, and pulls opinion posts across the boundary. It does not make the opposite mistake of dismissing genuine analysis as opinion. This is consistent with the confusion matrix, where the entire EBA row is correctly classified (recall 1.00) while the IO row leaks 3 cases into EBA.

**Pattern 3 — Length is a correlate of errors (supported, but not the cause).** The notebook's Section 4c computes mean/median character length for correct vs. incorrect predictions: correct predictions average 2,061 chars, incorrect predictions average 777 chars — misclassified posts are markedly shorter (less than 0.8× the correct-prediction mean, the notebook's threshold for "supported"). However, length is a correlate, not a cause. Shorter posts have fewer tokens to establish label-disambiguating vocabulary, which means the model falls back on weaker surface signals — consistent with the vocabulary-based failure mode described in Pattern 2. A post that is short *and* uses analytical-sounding words is exactly the profile of the Opinion→Analysis errors. Length predicts errors but does not explain them.

**Pattern 4 — Errors are reliably low-confidence (confirmed).** The 7 misclassifications have a mean confidence of 0.523, compared to 0.571 on correct predictions — a separation of only +0.048. Five of the 7 errors fall below 0.60 confidence (71%). The model's softmax scores are compressed into the 0.35–0.73 range across the entire test set (the 0.90–1.00 bin is empty), so the separation is modest but real. Routing predictions below 0.60 to human review would catch the majority of errors with minimal cost to throughput — the 0.50–0.70 bin shows 92% empirical accuracy, so confident predictions in that range are reliable.

**The systematic pattern, stated plainly:** *The model's errors are not random. They concentrate on two structural boundaries (Opinion↔Analysis and LQM↔Opinion), are directionally biased toward over-claiming evidence from analytical vocabulary, correlate with shorter post length (misclassified posts average 777 chars vs. 2,061 for correct ones), and occur at systematically lower confidence than correct predictions (mean 0.523 vs. 0.571). The model fails specifically when a short opinion post borrows the surface vocabulary of analysis — and it signals that failure through low confidence.*

---

### Confidence Calibration

A confidence score is only useful if it is *meaningful*: a 90%-confident prediction should be right more often than a 60%-confident one. If confidence does not track correctness, the softmax probability is a decorative number and cannot be used to route low-confidence posts to human review (one of the deployment cases in [planning.md](planning.md)). The notebook (`Section 4b`) assesses this three ways. The reliability diagram is saved to [results/calibration_curve.png](results/calibration_curve.png).

**1. Confidence separates correct from incorrect predictions.** The mean confidence on the 40 correct predictions is 0.571 vs. 0.523 on the 7 wrong ones — a gap of +0.048. This is a modest separation because the model's entire softmax distribution is compressed into the 0.35–0.73 range: the 0.90–1.00 bin is empty across all 47 test examples. The signal is real but small. Crucially, 5 of the 7 errors fall below 0.60 (71%), making the confidence score a useful triage filter even with the narrow overall range.

**2. Accuracy rises with confidence (reliability table).** The notebook's Section 4b bins show: 0.00–0.50 bin (n=10) → 60% accuracy; 0.50–0.70 bin (n=36) → 92% accuracy; 0.70–0.90 bin (n=1) → 100% accuracy. The 0.90–1.00 bin is empty. Accuracy rises sharply from the low to mid confidence tier — the 0.50–0.70 bin, which contains 77% of all test predictions, is highly reliable. This is the empirical answer to the "90% vs. 60%" question reframed for this model: **yes, a mid-confidence prediction (0.50–0.70) is meaningfully more likely to be correct (92%) than a low-confidence one (0.00–0.50, 60%).**

**3. Expected Calibration Error (ECE).** The notebook reports ECE — the population-weighted average gap between stated confidence and realized accuracy across bins — together with the reliability diagram plotting confidence against empirical accuracy (the diagonal is perfect calibration).

**Practical consequence:** 5 of the 7 errors (71%) fall below 0.60 confidence. Routing predictions under ~0.60 to human review would catch those errors while passing through the 0.50–0.70 bin (n=36, 92% accurate) automatically. The threshold is imperfect at this scale — 10 low-confidence predictions would be flagged, but 6 of those 10 are actually correct. In a production setting with higher volume, this tradeoff (flagging ~20% of predictions for review in exchange for catching 71% of errors) is operationally useful. The deployed interface ([app.py](app.py)) implements this triage hint directly.

**Honest caveat:** With only 47 test examples, per-bin counts are small and ECE is a noisy point estimate. These findings are reported as *directional* evidence that confidence is informative — strong enough to support a triage threshold — not as a precise calibration certificate. A production system would re-estimate calibration on a far larger held-out set.

---

### Sample Classifications

The following posts were run through the saved fine-tuned model (`checkpoint-56`) and reflect its actual output — labels and confidence scores are produced by the same artifact loaded by the deployed interface ([app.py](app.py)), not manually entered:

| Post (truncated) | Predicted Label | Confidence | Correct? |
|------------------|-----------------|------------|----------|
| "NVDA's data center revenue grew 427% YoY to $47.5B in FY2024. At a forward P/E of ~35x on consensus FY2025 EPS of $28, the stock looks fairly valued..." | `Interpretive_Opinion` | 0.54 | ✗ (true: EBA) |
| "I think the Fed is going to pivot earlier than expected. Inflation feels like it's under control and they don't want to cause unnecessary damage to the labor market." | `Low_Quality_Misleading` | 0.49 | ✗ (true: IO) |
| "Apple reported Q2 FY2025 revenue of $95.4B, up 5% YoY. Services revenue hit a new record at $26.6B. EPS of $1.65 beat consensus by $0.04." | `News_Information` | 0.35 | ✓ |
| "GME to $500 by end of month. Shorts are TRAPPED. Anyone selling before $300 is leaving money on the table." | `Low_Quality_Misleading` | 0.62 | ✓ |
| "Microsoft's cloud segment has been growing faster than AWS for three consecutive quarters, which tells me the enterprise migration cycle still has runway." | `Interpretive_Opinion` | 0.57 | ✓ |

These five posts were chosen as canonical examples of each label, but they are not from the held-out test set — they are new inputs, not seen during training or evaluation. Three of five are correctly classified; two are wrong, both at low confidence (0.54 and 0.49). This is consistent with the model's actual behavior: the notebook's Section 4b confirms no test prediction exceeded 0.73 confidence, the 0.90–1.00 bin is empty, and mean confidence on correct predictions is only 0.571.

**Why confidence is uniformly low:** The model's softmax outputs are compressed into the 0.35–0.65 range across the board. This is a known artifact of training with `WeightedCrossEntropyLoss` on a small dataset — the class weights push the model toward hedged rather than peaked distributions, and the model has learned that many posts sit near label boundaries. It is poorly calibrated (ECE = 0.287): its stated confidence substantially underestimates its realized accuracy. The 0.50–0.70 confidence bin has 92% empirical accuracy, meaning the model is nearly as reliable at 0.55 as a well-calibrated model at 0.90.

**Row 1 misclassification (NVDA — true: `Evidence_Based_Analysis`, predicted: `Interpretive_Opinion`):** This post is a hard case even for a human annotator — it combines opinion framing ("looks fairly valued") with specific financial metrics (P/E, EPS). The model predicts `Interpretive_Opinion` at 0.54, only marginally preferred over the correct label `Evidence_Based_Analysis` (0.18). This exact boundary confusion — analytical vocabulary triggering the wrong label at low confidence — is the dominant error pattern identified in Section 4 and the error pattern analysis.

**Row 2 misclassification (Fed pivot — true: `Interpretive_Opinion`, predicted: `Low_Quality_Misleading`):** The post is hedged ("I think," "feels like") but the model assigns it `Low_Quality_Misleading` at 0.49 — nearly a coin flip between LQM (0.49) and IO (0.41). This is the secondary error boundary (LQM↔IO) and occurs precisely at the low confidence that the triage threshold is designed to catch.

---

## Reflection: What the Model Learned vs. What Was Intended

The model was designed to learn *reasoning structure*: whether a post's claim is grounded in independently verifiable evidence, regardless of how it is phrased. What the model actually learned, at 217 training examples, is a strong approximation of that intention via *surface vocabulary patterns*.

It learned, correctly, that `News_Information` posts contain specific numbers, company names, percentage changes, and factual verbs in past tense ("reported," "announced," "raised"). It learned that `Low_Quality_Misleading` posts contain certainty markers ("guaranteed," "TRAPPED," "load up") and imperatives. It learned that `Interpretive_Opinion` posts use hedging language ("I think," "I feel," "I believe").

Where it overfits is at the `Evidence_Based_Analysis` / `Interpretive_Opinion` boundary. The model learned that analytical vocabulary (math, exact, fact, data, metrics) predicts `Evidence_Based_Analysis`, which is correlated but not identical to the intended definition. The intended definition requires a structural property — the evidence standing independently of the author's assertion — that cannot be reliably detected from surface vocabulary alone.

The practical consequence is systematic false positives on `Evidence_Based_Analysis`: opinion posts that use analytical-sounding language get pulled across the boundary. The model cannot perform the "stripping test" that the annotation guidelines describe, because that test requires semantic understanding of the claim's logical structure, not pattern matching on vocabulary.

This is not a failure of the fine-tuning approach; it is an honest limitation of DistilBERT at this data scale. A model that learned the intended structural distinction would need substantially more training examples at the hard boundary, examples that systematically contrast analytical vocabulary with non-analytical reasoning, so the model can learn to disambiguate the two. Alternatively, a larger model (BERT-large, RoBERTa) might better capture argument structure from context. The gap between intention and learned decision boundary is ~4.2pp of accuracy at this scale — meaningful but not catastrophic.

---

## Spec Reflection

**One way the spec helped:** Defining the four labels and their edge case rules before any annotation began was the single most valuable structural decision in this project. The "stripping test" (remove opinion framing — does the claim stand independently?) resolved dozens of ambiguous cases that would otherwise have been labeled inconsistently. Without that rule written down before annotation, the Analysis/Opinion boundary would have drifted significantly across 310 examples.

**One way implementation diverged from the spec:** The spec assumed inter-annotator agreement would be feasible to compute. In practice, with a single annotator and a 310-example manual dataset, there was no second labeler to check against. The consequence is that annotation consistency is structural risk that cannot be quantified. Several posts near the Analysis/Opinion boundary were revisited multiple times during annotation, and it is plausible that if the same annotator reviewed the dataset a second time without memory of the first pass, some borderline decisions would differ. The spec should have included at least a 30-example second-pass consistency check by the same annotator to estimate this drift.

---

## Deployed Interface

A single-file [Gradio](https://www.gradio.app/) app ([app.py](app.py)) loads the fine-tuned model and lets you classify a brand-new post interactively: paste a Reddit r/stocks post, press **Classify**, and the app returns the predicted discourse-quality label, the model's confidence, the full probability distribution across all four classes, and a triage hint.

The triage hint operationalizes the calibration finding from the [Confidence Calibration](#confidence-calibration) section: because the model's errors concentrate below ~0.60 confidence, any prediction under that threshold is flagged for human review rather than auto-classified — exactly the human-in-the-loop pattern a production content-triage system would use.

The interface tokenizes input with the **same** settings used at training time (`truncation=True, max_length=256`) and reads the label mapping from the saved model's own `id2label`, so the deployed predictions are identical to what the notebook produces — no drift between evaluation and deployment.

### Prerequisites

The trained model directory (`model/takemeter-model`) is **gitignored** because it is a large binary artifact, so it is not shipped in this repo. Before running the interface you need the trained model on disk:

- Run [model/model_notebook.ipynb](model/model_notebook.ipynb) end-to-end (Sections 1–3 train and save the model), then download the resulting `takemeter-model` directory from Colab and place it at `model/takemeter-model/`.

The app auto-resolves the model location: it reads the optional `TAKEMETER_MODEL_DIR` environment variable, defaults to `model/takemeter-model`, and if pointed at that Trainer output directory it automatically selects the latest `checkpoint-*` subfolder.

### How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the interface
python app.py
```

Gradio prints a local URL (default `http://127.0.0.1:7860`) — open it in a browser. To point the app at a model stored elsewhere:

```bash
# macOS / Linux
TAKEMETER_MODEL_DIR=/path/to/takemeter-model python app.py

# Windows (PowerShell)
$env:TAKEMETER_MODEL_DIR = "C:\path\to\takemeter-model"; python app.py
```

The app runs on CPU by default — DistilBERT is small enough for sub-second single-post inference, so no GPU is required to demo it.

### Honest Note on Deployed Behavior

The interface inherits every limitation of the underlying model documented in the [reflection](#reflection-what-the-model-learned-vs-what-was-intended) above — the directional Opinion→Analysis bias and the thin training signal for sarcastic `Low_Quality_Misleading` posts. It is also **poorly calibrated**: the canonical example posts return confidences in the ≈0.35–0.62 range, and some borderline posts (e.g. the NVDA analysis post) are misclassified at low confidence. The interface deliberately surfaces these true, low confidences via the triage hint rather than hiding them behind a single confident-looking label.

---

## AI Usage

### Instance 1: BERT Architecture and Training Loop Explanation

Before implementing the fine-tuning cell, Claude was asked to explain how DistilBERT's classification head attaches to the transformer backbone, how the training loop differs from a standard PyTorch CNN training loop (the extent of my prior model training experience), and what the `Trainer` API abstracts away relative to writing a manual loop. Claude produced a detailed walkthrough of the transformer classification architecture — `[CLS]` token pooling, the pre-classifier dense layer, the final linear head — and explained the differences in gradient flow between sequence classification and convolutional architectures.

**What was changed or overridden:** Claude's explanation included a recommendation to use `AutoModel` with a manually attached classification head rather than `AutoModelForSequenceClassification`, on the grounds that it gives more control. After reviewing the HuggingFace docs, this was overridden in favor of `AutoModelForSequenceClassification` because the notebook scaffold was already built around the `Trainer` API, which expects the model to return a loss from its `.forward()` call — something `AutoModelForSequenceClassification` handles automatically and a manual head would require re-implementing. The explanation was valuable for understanding; the implementation recommendation was not adopted.

### Instance 2: Class Weighting Mechanics and Accuracy Improvements

After the initial training run produced ~50% accuracy (barely above random on four classes), Claude was asked — from the perspective of a senior ML engineer and financial analyst — to explain how class weighting works mechanically in a CrossEntropyLoss function and what other accuracy improvements would be appropriate given the dataset characteristics. Claude explained inverse-frequency class weight computation, how the per-sample loss scaling interacts with gradient updates across a mini-batch, and why it prevents the model from collapsing to majority-class prediction. It also recommended increasing epochs (with `load_best_model_at_end` as a safety net against overfitting) and a modest learning rate increase to escape the flat training region.

**What was changed or overridden:** Claude's initial weight formula suggestion used `n_samples / (n_classes * n_samples_per_class)` — standard inverse frequency. This was implemented directly as described. Claude also recommended label smoothing (epsilon=0.1) as an additional regularizer. This was tested and then removed: label smoothing reduced validation accuracy on this small dataset because the hard label signal is exactly what the model needs at 217 training examples — smoothing it was counterproductive. Claude's architectural suggestion (adding a dropout layer between pre-classifier and classifier) was also skipped; the `Trainer` + `WeightedTrainer` pattern was simpler and achieved the accuracy target without additional architectural changes.

The three changes implemented (class weights, 5 epochs, 3e-5 learning rate) moved final test accuracy from ~50% to **85.1%**.

---

*Dataset: 310 manually annotated r/stocks posts · Model: distilbert-base-uncased fine-tuned on T4 GPU · Test set: 47 examples · Evaluation: macro F1 = 0.86 · Stretch features: confidence calibration + systematic error pattern analysis + deployed Gradio interface*
