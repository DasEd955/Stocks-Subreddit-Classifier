"""inference.py - Pure predict function for the TakeMeter classifier.

This module contains the "predict" half of the classify pipeline: tokenize a
post, run the forward pass, and return a structured PredictionResult. It has no
knowledge of Gradio, Markdown, or any other display concern, which is what
makes it reusable from a batch processing script, an API endpoint, or a test
suite without ever importing gradio.

The "format for display" half lives in formatting.py.
"""

from dataclasses import dataclass

# Match the notebook's training time tokenization exactly so deployed
# predictions do not drift from the evaluated ones.
MAX_LENGTH = 256

# Confidence at/below which the calibration analysis (planning.md Section 10)
# showed errors concentrate. Predictions under this are flagged for human review.
REVIEW_THRESHOLD = 0.60


@dataclass
class PredictionResult:
    """Structured result of classifying a single post.

    Attributes:
        label (str): The predicted class name, or None for empty input.
        confidence (float): The winning class's softmax probability, or 0.0
            for empty input.
        confidences (dict[str, float]): {label: confidence} for all classes,
            or {} for empty input.
        needs_review (bool): True if confidence < REVIEW_THRESHOLD. Always
            False for empty input.
        is_empty (bool): True if the input post was blank after stripping.
    """

    label: str
    confidence: float
    confidences: dict
    needs_review: bool
    is_empty: bool


def predict(post: str, tokenizer, model, id2label: dict) -> PredictionResult:
    """Classify a single r/stocks post and return a structured result.

    Tokenizes the post with the same max_length used at training time, runs a
    single forward pass through the fine-tuned model under no_grad(), and maps
    the resulting softmax probabilities to a PredictionResult.

    Args:
        post (str): Raw text of a Reddit r/stocks post or comment.
        tokenizer: A loaded Hugging Face tokenizer compatible with model.
        model: A loaded AutoModelForSequenceClassification in eval() mode.
        id2label (dict[int, str]): Mapping from class index to label name.

    Returns:
        PredictionResult: The predicted label, confidence, full distribution,
            and review flag. For blank input (empty or whitespace-only),
            returns a result with is_empty=True and no model call is made.
    """
    post = (post or "").strip()
    if not post:
        return PredictionResult(
            label=None, confidence=0.0, confidences={}, needs_review=False, is_empty=True
        )

    import torch

    inputs = tokenizer(
        post,
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt",
    )
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1).squeeze(0)

    confidences = {id2label[i]: float(probs[i]) for i in range(len(id2label))}

    pred_id = int(torch.argmax(probs))
    pred_label = id2label[pred_id]
    confidence = float(probs[pred_id])

    return PredictionResult(
        label=pred_label,
        confidence=confidence,
        confidences=confidences,
        needs_review=confidence < REVIEW_THRESHOLD,
        is_empty=False,
    )
