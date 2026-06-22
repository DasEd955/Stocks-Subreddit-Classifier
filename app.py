"""app.py - Gradio inference interface for the TakeMeter r/stocks discourse quality classifier.

The UI is intentionally thin. All classification logic lives in the fine-tuned
DistilBERT model loaded at startup; this module only tokenizes the input, runs the
forward pass, and maps the output probabilities to the two Gradio output panels.
classify() is the single Gradio callback. It guards against empty input, tokenizes
the post, runs model.eval() under torch.no_grad(), and returns a {label: confidence}
dict for gr.Label alongside a Markdown summary string.

resolve_model_dir() handles the two-level checkpoint layout produced by Hugging Face
Trainer: if the target directory lacks config.json (i.e. it is the parent output dir),
it auto selects the latest checkpoint-* subdirectory. An explicit TAKEMETER_MODEL_DIR
env var overrides the default model/takemeter-model path so the app can be pointed at
any compatible checkpoint without editing the source.

REVIEW_THRESHOLD (0.60) is the calibration-derived confidence cutoff documented in
planning.md §8; predictions below it surface a human review triage hint instead of an
auto-classify note. The eight curated EXAMPLES cover both decision boundary cases
(where the model disagrees with the human label) & clear signal cases that match the
intended label, so the UI demonstrates both the model's strengths and its known
failure modes.

Run with:
    python app.py

Then open the localhost URL shown in your terminal (usually http://localhost:7860).
The trained model directory (model/takemeter-model) is gitignored due to size. Train it 
via model/model_notebook.ipynb or set TAKEMETER_MODEL_DIR to an existing checkpoint.
"""

import os
import re
from pathlib import Path

import gradio as gr
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Confidence at/below which the calibration analysis (planning.md Section 8) showed
# errors concentrate. Predictions under this are flagged for human review.
REVIEW_THRESHOLD = 0.60

# Match the notebook's training time tokenization exactly so deployed predictions
# do not drift from the evaluated ones.
MAX_LENGTH = 256

# Plain-language descriptions shown in the UI for each label.
LABEL_DESCRIPTIONS = {
    "Evidence_Based_Analysis": "A claim backed by data, metrics, or reasoning that could stand on its own.",
    "Interpretive_Opinion": "A personal judgment or prediction without substantial supporting evidence.",
    "News_Information": "Factual reporting of an event, announcement, or release — no interpretation.",
    "Low_Quality_Misleading": "Hype, fearmongering, manipulation, or unsupported certainty presented as fact.",
}


def resolve_model_dir() -> Path:
    """Find the saved model directory.

    Precedence:
      1. TAKEMETER_MODEL_DIR env var, if set.
      2. The default local checkpoint shipped with the repo layout.
    If the resolved path is a parent `takemeter-model` directory containing
    `checkpoint-*` subfolders, auto-select the latest checkpoint.
    """
    here = Path(__file__).resolve().parent
    default = here / "model" / "takemeter-model"
    model_dir = Path(os.environ.get("TAKEMETER_MODEL_DIR", default))

    # If pointed at the Trainer output dir, descend into the latest checkpoint.
    if model_dir.is_dir() and not (model_dir / "config.json").exists():
        checkpoints = sorted(
            model_dir.glob("checkpoint-*"),
            key=lambda p: int(m.group()) if (m := re.search(r"\d+$", p.name)) else -1,
        )
        if checkpoints:
            model_dir = checkpoints[-1]

    if not (model_dir / "config.json").exists():
        raise FileNotFoundError(
            f"No model found at '{model_dir}'. The trained model is gitignored — "
            "train it via model/model_notebook.ipynb and place the saved "
            "'takemeter-model' directory under 'model/', or set the "
            "TAKEMETER_MODEL_DIR environment variable to its location."
        )
    return model_dir


MODEL_DIR = resolve_model_dir()
print(f"Loading model from: {MODEL_DIR}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

# id2label from the saved config is the source of truth for the label mapping.
ID2LABEL = {int(k): v for k, v in model.config.id2label.items()}


def classify(post: str):
    """Classify a single r/stocks post and return Gradio output values.

    Tokenizes the post with the same max_length used at training time, runs a
    single forward pass through the fine-tuned model under no_grad(), and maps
    the resulting softmax probabilities to the two UI output components.

    A triage hint is appended to the summary based on whether the top-class
    confidence clears REVIEW_THRESHOLD: below it the prediction is flagged for
    human review; at or above it the auto classify note is shown instead.

    Args:
        post (str): Raw text of a Reddit r/stocks post or comment.

    Returns:
        tuple[dict[str, float], str]:
            - A {label: confidence} dict consumed by gr.Label (all four classes,
              so the full distribution is visible in the confidence bar chart).
            - A Markdown string with the predicted label name, its plain-language
              description from LABEL_DESCRIPTIONS, and the triage hint.
            On empty input, returns ({}, prompt string) without running the model.
    """
    post = (post or "").strip()
    if not post:
        return {}, "Enter a post above and press **Classify**."

    inputs = tokenizer(
        post,
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt",
    )
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1).squeeze(0)

    # gr.Label expects {label: confidence} and renders the sorted distribution.
    confidences = {ID2LABEL[i]: float(probs[i]) for i in range(len(ID2LABEL))}

    pred_id = int(torch.argmax(probs))
    pred_label = ID2LABEL[pred_id]
    confidence = float(probs[pred_id])

    description = LABEL_DESCRIPTIONS.get(pred_label, "")
    if confidence < REVIEW_THRESHOLD:
        triage = (
            f"⚠️ **Low Confidence ({confidence:.0%})** — Below the {REVIEW_THRESHOLD:.0%} "
            "review threshold. In a production triage pipeline this post would be routed "
            "to a human reviewer rather than automatically classified."
        )
    else:
        triage = (
            f"✅ **Confident ({confidence:.0%})** — At or above the "
            f"{REVIEW_THRESHOLD:.0%} threshold, this prediction can run automatically."
        )

    summary = f"### Prediction: `{pred_label}`\n\n{description}\n\n{triage}"
    return confidences, summary


# The examples fall into two groups. The first four are by the taxonomy correct but
# sit on a model decision boundary. The deployed checkpoint disagrees with the human
# label, which is exactly the calibration weakness documented in planning.md §8–9.
# The second four were tuned against the actual checkpoint so its argmax matches the
# intended label. Predictions below are from checkpoint-56 (the shipped model).
EXAMPLES = [
    # BOUNDARY — intended Evidence_Based_Analysis; model predicts Interpretive_Opinion
    # (~0.54). The canonical Analysis↔Opinion confusion: the valuation verdict ("looks
    # fairly valued") reads as a personal take to the model despite the cited metrics.
    "NVDA's data center revenue grew 427% YoY to $47.5B in FY2024. At a forward P/E of ~35x on consensus FY2025 EPS of $28, the stock looks fairly valued relative to the S&P tech median of 32x. It is not the screaming buy bulls are claiming.",
    # BOUNDARY — intended Interpretive_Opinion; model predicts Low_Quality_Misleading
    # (~0.49, with Opinion ~0.41 just behind). The confident macro call tips it toward
    # the manipulation class even though there is no hype or call to action.
    "I think the Fed is going to pivot earlier than expected. Inflation feels like it's under control and they don't want to cause unnecessary damage to the labor market.",
    # BOUNDARY — intended News_Information; model predicts News but weakly (~0.35, with
    # Opinion ~0.28 close behind). Bare earnings figures with no headline/source cue sit
    # near the News↔Opinion line for this checkpoint.
    "Apple reported Q2 FY2025 revenue of $95.4B, up 5% YoY. Services revenue hit a new record at $26.6B. EPS of $1.65 beat consensus by $0.04.",
    # BOUNDARY — intended Low_Quality_Misleading; model predicts Low_Quality (~0.56).
    # The only original example whose argmax matches the human label, though still under
    # the 0.60 review threshold.
    "GME to $500 by end of month. Shorts are TRAPPED. Anyone selling before $300 is leaving money on the table. This is the squeeze of the decade.",
    # CLEAR — Evidence_Based_Analysis (model predicts EBA ~0.48). EBA is the hardest
    # class for this checkpoint: it keys on length + a thesis that draws inferences from
    # data ("my thesis", "tells you", "the implication is"), plus the "Company Analysis"
    # tag seen in real EBA posts. Short data dumps get read as News or Opinion instead.
    "My thesis: Microsoft is the best positioned name in the cloud cycle, and the segment data backs it up rather than the other way around. Company Analysis Azure grew 33% YoY last quarter against AWS at 17% and Google Cloud at 28%, the third consecutive quarter it has outpaced both rivals, which tells you this is share gain, not just a rising tide. Commercial remaining performance obligations hit $315B, up 34% YoY; that contracted backlog means the growth is already booked, not hoped for. Operating margin held at 45% even as capex ramped to $20B, so I read this as durable compounding rather than growth bought with eroding profitability. The implication is that Microsoft is capturing a disproportionate share of new enterprise AI spend, and that is what justifies the ~35x forward P/E premium over the rest of big tech - you are paying up for the highest-quality compounder in the group, and on these numbers I think that premium is earned.",
    # CLEAR — Interpretive_Opinion (model predicts Opinion ~0.50). Purely subjective
    # ("feels", "gut sense", "vibe"), zero data, no manipulative call to action. So, it
    # stays clear of both Analysis and Low Quality.
    "Honestly I just don't trust this rally. Everything feels stretched to me and I've got a gut sense we're due for a real pullback before year end. Nothing concrete, just the vibe of the market right now. I'm staying mostly in cash until it feels healthier.",
    # CLEAR — News_Information (model predicts News ~0.51). Phrased in the headline +
    # category tag + URL structure the model learned for real news posts; without that
    # surface form (e.g. a bare "Breaking: ..." sentence) it mislabels facts as opinion.
    "Fed holds rates steady at 4.25%-4.50%, in line with expectations Broad market news The Federal Reserve held its benchmark interest rate at 4.25% to 4.50% at the conclusion of today's FOMC meeting. The central bank said it will wait for more data before deciding on any rate cuts. https://www.cnbc.com/fomc-decision.html",
    # CLEAR — Low_Quality_Misleading (model predicts Low_Quality ~0.50). Conspiracy
    # framing + unsupported certainty ("guaranteed 10-bagger") + inflammatory call to
    # action. Multiple planning.md §3 criteria at once.
    "PLTR is about to explode and the suits on Wall Street are praying you stay asleep. Insiders are quietly loading the boat while the financial media tells you to sell. This is a guaranteed 10 bagger. Mortgage the house if you have to. Anyone who fades this will be crying in a year.",
]

# Main Gradio interface definition. The left column has the input textbox, classify button, and example buttons; 
# the right column has the Markdown summary and confidence bar chart. Both the button click and textbox submit trigger 
# the same classify() callback so users can choose their preferred interaction pattern.
with gr.Blocks(title="TakeMeter — r/stocks Discourse Quality Classifier") as demo:
    gr.Markdown(
        "# 📊 TakeMeter\n"
        "### r/stocks Discourse Quality Classifier\n"
        "Paste a Reddit r/stocks post below. The fine-tuned DistilBERT model labels it "
        "as one of four discourse quality categories and reports its confidence.\n\n"
        "**Labels:** `Evidence_Based_Analysis` · `Interpretive_Opinion` · "
        "`News_Information` · `Low_Quality_Misleading`"
    )
    with gr.Row():
        with gr.Column(scale=3):
            post_input = gr.Textbox(
                label="Reddit post",
                placeholder="Paste a post from r/stocks here...",
                lines=10,
            )
            classify_btn = gr.Button("Classify", variant="primary")
            gr.Examples(examples=[[e] for e in EXAMPLES], inputs=post_input)
        with gr.Column(scale=2):
            summary_output = gr.Markdown()
            label_output = gr.Label(label="Confidence by class", num_top_classes=4)

    classify_btn.click(
        fn=classify,
        inputs=post_input,
        outputs=[label_output, summary_output],
    )
    post_input.submit(
        fn=classify,
        inputs=post_input,
        outputs=[label_output, summary_output],
    )


if __name__ == "__main__":
    demo.launch()
