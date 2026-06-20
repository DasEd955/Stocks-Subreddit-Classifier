# TakeMeter: r/stocks Discourse Quality Classifier
### Planning Document

---

## 1. Community

**Community chosen:** Reddit r/stocks

The r/stocks subreddit is an active community where retail investors, analysts, and casual observers share stock picks, market commentary, earnings reactions, and economic analysis. It was selected because it presents a genuine & consequential classification challenge: the ability to distinguish evidence-based reasoning from emotional speculation is not merely academic; it maps directly to signal quality in financial decision-making from individual retail investors to large institutional firms.

This community is an ideal fit for a classification task for several reasons. First, the discourse is structurally varied: the same ticker symbol might generate a peer-reviewed quality earnings breakdown, a prediction based off of gut feelings, a Reuters headline repost, and a pump-and-dump style hype post — all within the same thread. Second, the stakes attached to financial content make the quality distinctions matter in ways that sports or entertainment subreddits do not. Third, since hedge funds & quantitative research firms already deploy alternative data pipelines that scrape social media for sentiment signals, this classifier is a small-scale, interpretable proof-of-concept for a real institutional use case. The presence of both bullish & bearish actors, the influence of macroeconomic events (Fed rate decisions, earnings seasons), and recent catalysts like AI-related equities & political market volatility all ensure that no single discourse pattern dominates; making the label boundaries both necessary and non-trivial to apply.

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

*Planned stretch features: confidence calibration, error pattern analysis, deployed Gradio interface.*
