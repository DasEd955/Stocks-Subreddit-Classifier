# TakeMeter: r/stocks Discourse Quality Classifier
### Planning Document

---

## 1. Community

**Community chosen:** Reddit r/stocks

The r/stocks subreddit is an active community where retail investors, analysts, and casual observers share stock picks, market commentary, earnings reactions, and economic analysis. It was selected because it presents a genuine & consequential classification challenge: the ability to distinguish evidence-based reasoning from emotional speculation is not merely academic; it maps directly to signal quality in financial decision-making from individual retail investors to large institutional firms.

This community is an ideal fit for a classification task for several reasons. First, the discourse is structurally varied: the same ticker symbol might generate a peer-reviewed quality earnings breakdown, a prediction based off of gut feelings, a Reuters headline repost, and a pump-and-dump style hype post all within the same thread. Second, the stakes attached to financial content make the quality distinctions matter in ways that sports or entertainment subreddits do not. Third, since hedge funds & quantitative research firms already deploy alternative data pipelines that scrape social media for sentiment signals, this classifier is a small-scale, interpretable proof-of-concept for a real institutional use case. The presence of both bullish & bearish actors, the influence of macroeconomic events (Fed rate decisions, earnings seasons), and recent catalysts like AI-related equities & political market volatility all ensure that no single discourse pattern dominates; making the label boundaries both necessary and non-trivial to apply.

---

## 2. Label Taxonomy

Four mutually exclusive labels were defined. Every post in the dataset can be assigned to exactly one.

---

### `Evidence_Based_Analysis`
**Definition:** A post that makes a claim and supports it with data, financial metrics, earnings reports, economic reasoning, technical chart evidence, or other independently verifiable evidence that could be evaluated regardless of the author's identity.

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
> "Apple is still the safest large-cap out there. Their ecosystem lock in is unmatched and I don't see that changing anytime soon."

---

### `News_Information`
**Definition:** A post that primarily reports factual information, announcements, earnings releases, SEC filings, analyst actions, or market events. Conveys what happened without substantially interpreting its meaning or implications.

**Example 1:**
> "Microsoft reported Q2 FY2025 revenue of $69.6B, up 12% YoY. Azure cloud grew 31%. EPS came in at $3.23, beating consensus of $3.10."

**Example 2:**
> "Breaking: SEC has opened a formal investigation into Archegos-affiliated entities. Trading halted on several affiliated positions pending review."

---

### `Low_Quality_Misleading`
**Definition:** A post that contains hype, fearmongering, misinformation, clickbait, conspiracy-style reasoning, pump-and-dump rhetoric, or unsupported certainty presented as established fact. Characterized by emotional manipulation rather than reasoning.

**Example 1:**
> "GME to $500 by end of month. Shorts are TRAPPED. Anyone selling before $300 is leaving money on the table. This is the squeeze of the decade."

**Example 2:**
> "The market crash is coming and the elites know it. Why do you think Buffett is sitting on cash? They're about to pull the rug and retail is going to get destroyed. SELL EVERYTHING."

---

## 3. Hard Edge Cases

The most consistently ambiguous boundary in r/stocks is between `Evidence_Based_Analysis` and `Interpretive_Opinion`. Many posts include one or two data points but are structurally more opinion than analysis.

**Governing edge case decision rules:**

---

**Analysis vs. Opinion**

The key question is: *Could the evidence stand alone as the basis for the claim, independent of the author's tone?*

| Post | Label | Rule |
|------|-------|------|
| "AAPL is going to beat earnings because iPhone demand remains strong and services revenue continues to grow." | `Evidence_Based_Analysis` | The author provides reasoning that could be evaluated independently — product segment trends are verifiable. |
| "AAPL is definitely going to beat earnings." | `Interpretive_Opinion` | Prediction without meaningful evidence = Opinion, regardless of confidence. |
| "NVDA is undervalued because data center revenue grew 80% YoY." | `Evidence_Based_Analysis` | Even though framed as an opinion ("I think it's undervalued"), the cited metric is specific and verifiable. If a single concrete, checkable data point anchors the claim, lean Analysis. |

**Rule:** If removing the opinion framing leaves a claim that is still supportable by the cited evidence, label `Evidence_Based_Analysis`. If the claim collapses without the author's assertion, label `Interpretive_Opinion`.

---

**News vs. Analysis**

| Post | Label | Rule |
|------|-------|------|
| "NVIDIA reports Q2 revenue of $45B, up 50% YoY." | `News_Information` | Pure fact reporting with no interpretive layer. |
| "NVIDIA's 50% YoY revenue growth suggests AI demand remains stronger than expected heading into Q3." | `Evidence_Based_Analysis` | Explaining implications of a fact = Analysis, not News. |

**Rule:** Reporting facts = News. Drawing inferences from facts = Analysis. The deciding word is often "suggests," "implies," "means," or "indicates."

---

**Low Quality vs. Opinion**

| Post | Label | Rule |
|------|-------|------|
| "I think Tesla is overvalued." | `Interpretive_Opinion` | A strong subjective opinion, but not manipulative or dishonest. |
| "Tesla is a guaranteed 10x by next year. Anyone selling is an idiot." | `Low_Quality_Misleading` | Combines unsupported certainty ("guaranteed") with inflammatory rhetoric — pattern of pump-and-dump style content. |

**Rule:** Strong opinion alone is not Low Quality. The threshold for `Low_Quality_Misleading` requires at least one of: (a) unsupported certainty presented as fact, (b) inflammatory or manipulative rhetoric designed to provoke emotional action, (c) demonstrably false claims, or (d) conspiracy-style reasoning with no logical chain.

---

**Additional edge case: News framed analytically**

A news headline reposted with an analytical-sounding title crosses into Analysis if the author adds implication. Example:

> "Goldman raises MSFT price target to $500 — this signals institutional confidence is accelerating ahead of the AI capex cycle."

The first clause is News; the second is Analysis. **Rule:** Label by the dominant purpose of the post. If >50% of the content is reporting and the analytical comment is decorative, label News. If the analytical framing is the thesis and the news is merely the supporting premise, label Analysis.

---

## 4. Data Collection Plan

**Source:** Reddit r/stocks subreddit (public posts and top-level comments)

**Collection method:** Manual curation via Reddit's search and hot/top/new feeds, filtered by post type and content. Posts were collected across varied time windows to avoid overfitting to a single market event cycle (e.g., earnings season only).

**Final dataset size:** 310 annotated examples

| Label | Count | % |
|-------|-------|---|
| Interpretive_Opinion | 116 | 37.4% |
| News_Information | 68 | 21.9% |
| Low_Quality_Misleading | 65 | 21.0% |
| Evidence_Based_Analysis | 61 | 19.7% |
| **Total** | **310** | **100%** |

**Collection challenge and resolution:**

`Interpretive_Opinion` and `News_Information` were the easiest labels to find — opinion posts are the default mode of social media commentary, and news reposts are extremely common on financial subreddits. `Low_Quality_Misleading` examples were also abundant, though they required more judgment to distinguish from strong opinions.

`Evidence_Based_Analysis` proved the hardest to find in sufficient quantity. Genuinely evidence-grounded posts are rarer in retail-investor communities than casual observation suggests — most posts that look analytical on the surface fail the "could the evidence stand alone" test upon closer inspection.

**Imbalance resolution:** Rather than discarding examples from overrepresented classes (which would waste real data and reduce total signal), class weights were computed using inverse frequency and applied to the `CrossEntropyLoss` function during fine-tuning. This mathematically equalizes the model's learning pressure across labels without altering the dataset distribution:

```
Class weights:
  Evidence_Based_Analysis:  1.2705
  Interpretive_Opinion:     0.6681
  Low_Quality_Misleading:   1.1397
  News_Information:         1.1923
```

This approach penalizes the model more heavily for misclassifying underrepresented classes, preserving all 310 samples while correcting for the skew.

---

## 5. Evaluation Metrics

Accuracy alone is insufficient for this task. Here is the full evaluation framework and the justification for each metric from both an ML and financial application perspective.

### Primary Metrics

**Macro F1 Score**
The single most important metric for this classifier. Macro F1 averages F1 across all four classes with equal weight, meaning it holds the model accountable for performance on underrepresented labels (`Evidence_Based_Analysis`, `Low_Quality_Misleading`) just as much as the majority class. For a financial tool, this matters: a model that achieves 85% accuracy by correctly labeling only `Interpretive_Opinion` posts — and never correctly identifying `Evidence_Based_Analysis` — provides near-zero investment research value. Macro F1 surfaces that failure.

**Per-class Precision, Recall, and F1**
Different failure modes carry different costs depending on the downstream use case:

- **Precision on `Evidence_Based_Analysis`:** A false positive here means mislabeling an opinion as analysis — an investor who trusts the classifier would read subjective content as if it were evidence-backed. In an investment filtering context, this is analogous to a false signal: costly.
- **Recall on `Low_Quality_Misleading`:** A false negative here means letting misleading content pass undetected. In a market surveillance or content moderation context, missing hype posts is more dangerous than occasionally flagging a borderline opinion.
- **Recall on `News_Information`:** High recall ensures time-sensitive factual updates are not misclassified as opinion and deprioritized by an investor using the tool as a feed filter.

**Confusion Matrix**
Essential for identifying systematic boundary confusion. The confusion matrix reveals which label pairs the model conflates most frequently — in this project, the expected hard boundary is `Interpretive_Opinion` ↔ `Evidence_Based_Analysis`, because many posts sit near that line. A confusion matrix makes this pattern visible and quantifiable.

### Secondary Metrics

**Overall Accuracy**
Reported as a reference baseline, but not the primary decision metric. Given class imbalance (Interpretive_Opinion at 37.4%), a model that predicts only the majority class would achieve ~37% accuracy — informative as a floor, not a ceiling.

**Baseline Comparison (Zero-shot Groq llama-3.3-70b-versatile)**
The fine-tuned model is benchmarked against a zero-shot LLM baseline using the same test set. This comparison answers the question that actually matters for deployment: *did task-specific fine-tuning outperform what a general-purpose LLM could do with well-crafted prompting?* If the answer is no, the fine-tuning pipeline needs to be reconsidered. If yes, the improvement quantifies the value of labeled data and supervised training.

---

## 6. Definition of Success

### Minimum Viable Performance (MVP Threshold)

For this classifier to be genuinely useful as a financial content filtering tool, the following minimum thresholds must be met on the held-out test set:

| Metric | Minimum Threshold | Rationale |
|--------|-------------------|-----------|
| Overall Accuracy | ≥ 75% | Baseline floor above majority-class guessing |
| Macro F1 | ≥ 0.70 | Ensures no class is systematically ignored |
| F1 on `Evidence_Based_Analysis` | ≥ 0.65 | The highest-signal class must be reliably detected |
| F1 on `Low_Quality_Misleading` | ≥ 0.65 | Noise filtering must be functional |

**Achieved results (fine-tuned DistilBERT, 47-example test set):**

| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Evidence_Based_Analysis | 0.75 | 1.00 | 0.86 |
| Interpretive_Opinion | 0.88 | 0.78 | 0.82 |
| News_Information | 1.00 | 0.90 | 0.95 |
| Low_Quality_Misleading | 0.80 | 0.80 | 0.80 |
| **Macro Average** | **0.86** | **0.87** | **0.86** |

**Overall accuracy: 85.1% (40/47)** — all MVP thresholds met and exceeded.

---

### The Real Deployment Case: Financial Analyst Applications

This project is deliberately designed as a small-scale proof-of-concept for approaches already used by institutional investors. The following use cases represent where a production-grade version of this classifier would create measurable value:

**1. Investment Research Filtering**

A platform ingesting thousands of Reddit, Twitter/X, StockTwits, and forum posts per day could use this classifier to automatically triage content:

- `Evidence_Based_Analysis` → priority read queue
- `Interpretive_Opinion` → sentiment signal pool (quantified by label ratio over time)
- `News_Information` → factual update stream (potentially routed to event-driven strategies)
- `Low_Quality_Misleading` → noise bucket (suppressed or flagged for manipulation monitoring)

An investor or research analyst using such a tool could process a 10x higher post volume with the same reading time, by focusing on the high-signal bucket.

**2. Sentiment Quality Signal (Beyond Valence)**

Traditional NLP sentiment analysis classifies posts as positive, negative, or neutral. This approach is ubiquitous and noisy, precisely because it treats an evidence-based bearish thesis the same as a panic-driven sell post. A discourse quality classifier adds a second axis: not just *what direction* the sentiment is, but *how much it should be trusted*.

For a quantitative strategy, this enables a more nuanced signal:
- High `Evidence_Based_Analysis` posts trending bearish on a ticker → potentially meaningful
- High `Low_Quality_Misleading` posts trending bullish on a ticker → possible pump-and-dump signal; fade rather than follow

**3. Market Intelligence and Alternative Data**

Hedge funds and research firms (Two Sigma, Man Group, Citadel) already deploy alternative data pipelines that consume social media content. The key insight this classifier formalizes is that *not all social signal is equal*. A spike in `Low_Quality_Misleading` content around a specific ticker ahead of a price move is a qualitatively different signal from a spike in `Evidence_Based_Analysis` content; conflating them in a raw sentiment score discards that distinction.

Potential institutional metrics derived from this classifier:
- **Discourse quality ratio:** `Evidence_Based_Analysis` / total posts per ticker per day — a proxy for informed investor attention
- **Hype index:** rolling 7-day `Low_Quality_Misleading` post rate as a contrarian signal
- **Conviction ratio:** `Evidence_Based_Analysis` / (`Interpretive_Opinion` + `Evidence_Based_Analysis`) — measures whether bullish or bearish thesis is evidence-supported or sentiment-driven

**4. Honest Limitations at This Scale**

A 310-example dataset fine-tuned on DistilBERT is not a production system. At this scale, the model learns the patterns present in the annotation decisions made by a single annotator on a specific slice of r/stocks activity. Real deployment would require:

- Inter-annotator agreement validation across multiple labelers
- Continuous retraining as market discourse evolves (new tickers, new events, new manipulation patterns)
- Adversarial testing against coordinated inauthentic behavior (bot farms, coordinated pump posts)
- Domain adaptation if extended beyond r/stocks to other financial communities

The value of this project is in demonstrating the framework and validating that a fine-tuned model substantially outperforms zero-shot classification on this specific, expert-defined taxonomy. It succeeds in doing so, at 85.1% macro-averaged accuracy against a structurally broken zero-shot baseline.

---

## 7. AI Tool Plan

This project's workflow is annotation-heavy and evaluation-driven rather than implementation-heavy, so AI tools are used at three specific points where they add the most leverage: stress-testing label definitions before any annotation begins, and identifying error patterns after the model is trained. Annotation itself was kept fully manual by deliberate choice.

---

### 7.1 Label Stress-Testing

**Purpose:** Before committing to annotating 200+ examples, use an LLM to generate adversarial boundary posts — posts that sit exactly at the edge between two labels. If the generated posts cannot be cleanly classified using the existing definitions, the definitions need tightening before annotation begins.

**Prompt used (given to Claude):** The four label definitions and edge case rules from Section 2 and 3 were provided verbatim, with the instruction: *"Generate 5–10 posts that sit at the hardest possible boundary between two labels. Do not make them obviously one or the other."*

**Generated boundary posts and their resolved labels:**

*Analysis ↔ Opinion boundary:*

> "Microsoft's cloud segment has been growing faster than AWS for three consecutive quarters, which tells me the enterprise migration cycle still has runway."

→ `Evidence_Based_Analysis`. "Three consecutive quarters" is a specific, verifiable trend; the conclusion is derived from the cited pattern, not asserted independently. The phrase "tells me" is opinion framing over an evidence-based inference — apply the stripping rule: remove "tells me" and the claim still stands.

> "AI spending feels like it's plateauing — the hyperscalers are still growing capex but the marginal returns look like they're compressing."

→ `Interpretive_Opinion`. "Feels like" and "looks like" signal unverified intuition. "Marginal returns compressing" is not cited with data — it is asserted as felt observation. Strip the framing: the residual claim is not independently supportable.

> "Meta's Reality Labs has lost over $40B since 2020. At some point the market is going to stop giving Zuckerberg a pass on this."

→ `Evidence_Based_Analysis`. The $40B figure is specific and verifiable; the second sentence is an opinion rider. The post's primary function is to anchor a claim in evidence. The opinion rider is editorial, not the thesis.

*News ↔ Analysis boundary:*

> "Nvidia just reported another blowout quarter. $30B revenue, 122% YoY growth. This changes the competitive calculus for AMD — their data center roadmap looks underpowered by comparison."

→ `Evidence_Based_Analysis`. The first two sentences are news; the third is the dominant purpose of the post and constitutes analysis (draws an implication about a competitor). The analytical framing is the thesis; the news figures are the supporting premise.

> "CPI came in at 3.1% vs. 3.3% expected. Markets rallied. 10Y yields fell 12 bps."

→ `News_Information`. Pure fact reporting across three data points, no interpretive layer added. No implication is drawn.

*Opinion ↔ Low Quality boundary:*

> "I genuinely don't understand why anyone is still long $TSLA here. The fundamentals don't support a $600B valuation and Musk is a liability."

→ `Interpretive_Opinion`. The first clause is strong opinion; the second ("fundamentals don't support") gestures at evidence without citing it, which is not enough to cross into Analysis. The post is direct but not manipulative — no certainty-as-fact, no inflammatory call to action beyond implicit disagreement. Stays Opinion.

> "TSLA puts are literally free money right now. This thing is about to collapse. Load up or stay poor."

→ `Low_Quality_Misleading`. "Literally free money" is unsupported certainty presented as fact. "Stay poor" is inflammatory rhetoric designed to pressure a financial action. Classic pump/dump framing applied inversely (a short-side pump). Crosses the Low Quality threshold on criteria (a) and (b).

> "Anyone who bought ARKK in 2021 deserves what happened to them. Cathie Wood is a fraud and I have zero sympathy."

→ `Interpretive_Opinion`. The "fraud" characterization is strong and potentially unfounded, but the post is retrospective commentary rather than a call to financial action. It does not contain a market prediction or attempt to move someone's trading behavior. It is opinionated, not misleading in the technical sense. Stays Opinion — but sits close to the line.

**Outcome of stress-testing:** The definitions held. All generated boundary posts could be resolved using the existing decision rules without requiring new rules or definition revisions. The most useful finding was that "opinion framing over an evidence-based inference" (e.g., "tells me," "I think," "seems like") does not automatically make a post Opinion — the stripping test is the correct tool.

---

### 7.2 Annotation Assistance

**Decision: No LLM pre-labeling. All 310 examples were manually annotated.**

Every row in [data.csv](data/data.csv) was labeled by hand, without LLM pre-labeling or suggestions at annotation time.

**Why manual-only annotation was chosen:**

1. **Label quality over speed.** The label definitions were designed around subtle structural distinctions (evidence that stands alone vs. opinion framing, reporting vs. implication) that an LLM will conflate in predictable ways — particularly at the Analysis/Opinion boundary. Pre-labeling with an LLM and then reviewing for disagreements risks anchoring the annotator to the LLM's decision, which undermines the independence of the ground truth.

2. **The dataset is small enough.** At 310 examples, manual annotation was achievable. LLM-assisted pre-labeling is a productivity tool for datasets in the thousands; using it here would introduce annotation bias without meaningful time savings.

3. **Single-annotator ground truth requires extra discipline.** Without a second annotator to check against (inter-annotator agreement was not computed for this project), the labeled dataset is entirely a reflection of one person's application of the definitions. Introducing an LLM pre-labeling pass would make the ground truth a reflection of *the LLM's priors filtered through one person's review* — a weaker epistemic position than direct human annotation.

**Limitation to acknowledge:** Single-annotator datasets carry consistency risk. The annotator's application of the Analysis/Opinion boundary may have drifted across 310 examples, particularly for the hardest edge cases. Without inter-annotator agreement metrics, there is no way to quantify this drift. This is a structural limitation of the dataset and should be disclosed in any deployment context.

**Disclosure:** No AI tool was used at any point during the annotation process. All labels in data.csv were assigned by the project author directly.

---

### 7.3 Failure Analysis

**Purpose:** After training, feed the model's 7 misclassifications to an LLM and ask it to identify systematic patterns before writing the evaluation narrative. The goal is to separate model-specific failure modes from annotation noise — and to surface patterns that are not obvious from looking at individual wrong predictions in isolation.

**Process:**

Each of the 7 wrong predictions (predicted label, true label, and post text) will be provided to Claude with the following prompt:

> *"Here are 7 posts that a fine-tuned DistilBERT classifier got wrong, with the predicted and true labels. Given these label definitions [definitions pasted], identify any systematic patterns in the errors. What is the model actually learning that causes these specific confusions? Be specific — don't just list the examples back."*

**What to look for in the LLM's response:**

- Whether the errors cluster around a specific label boundary (expected: `Interpretive_Opinion` ↔ `Evidence_Based_Analysis`)
- Whether the errors are driven by surface features (analytical-sounding vocabulary, present tense vs. reporting tense) rather than structural properties
- Whether short posts are disproportionately misclassified — the model may rely on length as a proxy for evidence density
- Whether the model conflates persuasive tone with Low Quality, or analytical vocabulary with Analysis

**How to verify the patterns independently:**

LLM-identified patterns will be checked against the confusion matrix and the full test set predictions before being reported as findings. Specifically:
- If the LLM claims "the model confuses opinionated tone with Low Quality," count how many of the 7 errors actually involve that boundary vs. how many involve the Analysis/Opinion boundary
- If the LLM claims "short posts are misclassified more often," check whether the misclassified posts are systematically shorter than correctly classified ones
- Any pattern not verifiable from the available prediction data will not be reported as a finding

**What the LLM analysis cannot tell us:** Whether the errors are the model's fault or the annotation's fault. A post that the model labels `Evidence_Based_Analysis` but the ground truth says `Interpretive_Opinion` might be a model error, or it might be an annotation inconsistency that a second human annotator would have labeled differently. The failure analysis will flag this ambiguity explicitly rather than treating all misclassifications as model failures.

---

## Model Architecture Summary

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Base model | `distilbert-base-uncased` | 40% smaller than BERT-base, 60% faster, retains ~97% of performance; fits Colab T4 GPU with room for batch size tuning |
| Max token length | 256 | Preserves full post context; Reddit posts rarely exceed this length |
| Epochs | 5 | Increased from default 3; small dataset benefits from more passes before plateau |
| Learning rate | 3e-5 | Increased from default 2e-5 to escape training flatness on small dataset |
| Batch size | 16 (train) / 32 (eval) | Standard for DistilBERT fine-tuning at this data scale |
| Loss function | Weighted CrossEntropyLoss | Class weights applied to compensate for Interpretive_Opinion overrepresentation |
| Warmup steps | 50 | Prevents large gradient updates in early training on a small corpus |

---

## 8. Stretch Feature: Confidence Calibration

**Purpose:** A confidence score is only useful if it is *meaningful* — i.e., the model's stated certainty tracks its actual correctness. A well-calibrated model that says "90% confident" should be right ~90% of the time, and a "60% confident" prediction should be right ~60% of the time. If confidence does not track accuracy, then the softmax probability is just a number and cannot be used downstream (e.g., to route low-confidence posts to human review in the deployment cases described in Section 6).

**The question this answers:** *Does a 90%-confident prediction actually get it right more often than a 60%-confident one?* This is the difference between a model whose confidence is actionable and one whose confidence is decorative.

**Methodology:**

The fine-tuned model's softmax probabilities on the 47-example test set (`ft_probs`, already computed in Section 4) give a confidence score per prediction (the max-softmax probability). Calibration is assessed three ways:

1. **Mean confidence on correct vs. incorrect predictions.** The single most direct check: if the model is calibrated at all, its average confidence on the predictions it got *right* should be meaningfully higher than on the ones it got *wrong*. If these two numbers are close, confidence is uninformative.

2. **Accuracy within confidence bins (reliability table).** Predictions are bucketed by confidence (e.g., 0.0–0.5, 0.5–0.7, 0.7–0.9, 0.9–1.0) and per-bin accuracy is computed. A calibrated model shows monotonically increasing accuracy across bins. This is the empirical answer to the "90% vs. 60%" question.

3. **Expected Calibration Error (ECE).** A single summary number: the average gap between confidence and accuracy across bins, weighted by bin population. Lower is better; ECE near 0 means stated confidence ≈ realized accuracy. A reliability diagram (confidence vs. accuracy, with the diagonal as perfect calibration) is plotted and saved to `results/calibration_curve.png`.

**Honest caveat to report:** With only 47 test examples, per-bin counts are small and ECE is a noisy estimate. The finding will be framed as directional evidence (does confidence separate right from wrong?) rather than a precise calibration certificate, and the small-sample limitation will be disclosed alongside the numbers.

**Verification:** The bin accuracies and the correct-vs-incorrect confidence gap are computed directly from the same `ft_probs`/`ft_pred_ids`/`ft_true_ids` arrays used for the main evaluation, so they are internally consistent with the reported 85.1% accuracy.

---

## 9. Stretch Feature: Error Pattern Analysis

**Purpose:** Go beyond the existing per-error narrative (Section 7.3 lists the 7 individual misclassifications) and identify a *systematic, programmatically verified* pattern in the errors — a single statement of the form "the model fails specifically when X" that is backed by counting over the actual predictions, not by eyeballing examples.

**What is already implemented (baseline to build on):**
- Section 4 of the notebook prints all 7 wrong predictions with confidence scores.
- A "Boundary Confusion Analysis" cell groups errors by `(true → predicted)` label pair.
- The README narrates both dominant error boundaries qualitatively.

**What this feature adds:** A quantitative pass that tests candidate systematic patterns against the full test set, so each claimed pattern is either confirmed or rejected by the data rather than asserted:

1. **Error concentration by boundary.** Quantify what fraction of all errors fall on the two suspected boundaries (`Interpretive_Opinion`↔`Evidence_Based_Analysis` and `Low_Quality_Misleading`→`Interpretive_Opinion`) vs. scattered elsewhere. A high concentration is evidence of a *structural* failure mode, not noise.

2. **Directionality of the Opinion/Analysis confusion.** Test whether the errors are asymmetric — i.e., the model pulls Opinion *into* Analysis far more than the reverse. Asymmetry indicates the model has a directional bias (over-applying analytical-vocabulary cues), which is a more specific finding than "it confuses these two labels."

3. **Length-as-proxy hypothesis (explicit verification).** The notebook's Section 4c computes mean/median character length of correct vs. incorrect predictions. The result: misclassified posts average 777 chars vs. 2,061 for correct predictions — the hypothesis is *supported* numerically, not rejected. Shorter posts have fewer tokens to establish label-disambiguating vocabulary, so the model falls back on weaker surface signals. Length is a correlate of error but not a root cause: it is a proxy for the vocabulary sparsity that underlies the Opinion→Analysis confusion.

4. **Confidence signature of errors.** Cross-link to the calibration feature: test whether errors cluster at low confidence (the model "knows" when it is unsure). If the misclassifications are disproportionately low-confidence, that is itself a systematic and *useful* pattern — it means a confidence threshold could catch most errors.

**The systematic pattern to be stated (hypothesis, to be confirmed by the code):** *The model's errors are not random — they concentrate on a single structural boundary (Opinion vs. Analysis), are directionally biased (Opinion→Analysis), and occur at systematically lower confidence than its correct predictions. The model is reliably uncertain exactly where it is wrong.* The notebook output will confirm or revise this statement with hard numbers.

**Verification discipline:** Every claimed pattern is computed from `ft_pred_ids`/`ft_true_ids`/`ft_probs`/`test_df` directly and reported as confirmed or rejected by the actual numbers — including patterns where the data contradicts the framing in Section 7.3 (e.g., the length hypothesis turned out to be *supported* by the numbers, not rejected, despite an earlier incorrect claim in the README).

---

## 10. Stretch Feature: Deployed Interface

**Purpose:** Make the fine-tuned classifier usable by a non-technical person without opening the notebook. A deployed interface closes the loop on the deployment cases in Section 6 (Investment Research Filtering, content triage): an analyst pastes a Reddit post, presses one button, and gets back the discourse-quality label plus the model's confidence — the exact human-in-the-loop interaction a production triage tool would expose.

**The question this answers:** *Can the trained model be invoked on a brand-new, never-seen post and return an actionable label + confidence, outside the training/eval harness?* The notebook only ever runs the model on the locked 47-example test set; this proves the saved artifact works as a standalone predictor.

**Methodology:**

A single-file [Gradio](https://www.gradio.app/) app ([app.py](app.py)) loads the fine-tuned model from the saved `model/takemeter-model` checkpoint with `AutoModelForSequenceClassification.from_pretrained`, tokenizes the input post with the *same* settings the notebook used at training time (`truncation=True, max_length=256`), runs a forward pass, and applies `softmax` to the logits. It then displays:

1. **The predicted label** — `argmax` over the four classes, mapped to its string name via the model's own `id2label` (the source of truth baked into `config.json`).
2. **The confidence** — the max softmax probability, shown as a Gradio `Label` with the full probability distribution across all four classes so the user sees not just the winner but how close the runner-up was (directly relevant to the Opinion↔Analysis boundary failure documented in Section 9).
3. **A triage hint** — because the calibration analysis (Section 8) established that errors concentrate below ~0.60 confidence, the interface flags low-confidence predictions as "route to human review," operationalizing the triage threshold rather than just reporting a number.

**Design decisions:**

- **Inference parity with training.** The app reuses `max_length=256` and reads labels from `id2label` in the saved config, so the deployed predictions are identical to what the notebook would produce — no silent drift between eval and deployment.
- **Model path is configurable and auto-resolving.** The trained model directory (`model/takemeter-model`) is gitignored (it is a large binary artifact), so the app does not assume a fixed file. It reads an optional `TAKEMETER_MODEL_DIR` environment variable, defaults to the local checkpoint, and if pointed at the parent `takemeter-model` directory it auto-selects the latest `checkpoint-*` subfolder. This keeps the committed code runnable for anyone who has trained (or downloaded) the model without committing the weights themselves.
- **CPU-friendly.** The app runs the model on CPU by default (DistilBERT is small enough for sub-second single-post inference), so it does not require a GPU to demo.

**Honest caveat to report:** The interface inherits every limitation of the underlying model documented in Sections 8–9 and the README reflection — in particular the directional Opinion→Analysis bias and the thin training signal for sarcastic `Low_Quality_Misleading` posts. The confidence-based triage hint is the interface's way of surfacing that uncertainty rather than hiding it behind a single label.

**Verification:** The app was verified by loading the saved best checkpoint (`checkpoint-56`, epoch 4, validation accuracy 0.848 — the `load_best_model_at_end` selection) and classifying the canonical example posts end-to-end. The model loads and runs to completion on CPU, and the interface faithfully reports the model's actual `argmax` label and max-softmax confidence.

**A finding surfaced during verification (reported honestly, not hidden):** the *deployed* predictions on the README "Sample Classifications" posts do **not** all match the high-confidence labels printed in that table (e.g. the NVDA data-center post is predicted `Interpretive_Opinion` at 0.54, not `Evidence_Based_Analysis` at 0.94). This is consistent with the model's *own* calibration data already documented in Section 8 / the README — mean confidence on correct predictions is only ~0.57 and ECE is 0.287, so the model is poorly calibrated and rarely produces the 0.9+ confidences that table reports. The sample-table numbers appear to be illustrative rather than reproduced from this checkpoint. The interface exposes the model's true (low, sometimes wrong) confidence rather than the aspirational table values — which is the entire point of shipping the calibration-based triage hint. Running instructions are documented in the README.
