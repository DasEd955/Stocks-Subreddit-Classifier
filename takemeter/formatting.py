"""formatting.py - Turn a PredictionResult into display-ready shapes.

This is the "format for display" half of the classify pipeline described in
inference.py's module docstring. Keeping it separate from predict() means the
Markdown/triage hint text can be tested (and changed) without touching model
loading or the forward pass, and means a non-Gradio consumer (a JSON API, a
CLI) can use predict() directly and skip this module entirely.
"""

from takemeter.inference import REVIEW_THRESHOLD, PredictionResult

# Plain language descriptions shown in the UI for each label.
LABEL_DESCRIPTIONS = {
    "Evidence_Based_Analysis": "A claim backed by data, metrics, or reasoning that could stand on its own.",
    "Interpretive_Opinion": "A personal judgment or prediction without substantial supporting evidence.",
    "News_Information": "Factual reporting of an event, announcement, or release, with no interpretation.",
    "Low_Quality_Misleading": "Hype, fearmongering, manipulation, or unsupported certainty presented as fact.",
}

EMPTY_INPUT_PROMPT = "Enter a post above and press **Classify**."


def format_confidences(result: PredictionResult) -> dict:
    """Return the {label: confidence} dict consumed by gr.Label.

    Args:
        result (PredictionResult): The result of a predict() call.

    Returns:
        dict[str, float]: All four class confidences, or {} for empty input.
    """
    return result.confidences


def format_triage_hint(result: PredictionResult) -> str:
    """Build the human review triage hint for a non-empty prediction.

    Args:
        result (PredictionResult): A predict() result with is_empty=False.

    Returns:
        str: A Markdown line flagging low confidence for human review, or
            confirming the prediction can run automatically.
    """
    if result.needs_review:
        return (
            f"Low Confidence ({result.confidence:.0%}). Below the {REVIEW_THRESHOLD:.0%} "
            "review threshold. In a production triage pipeline this post would be routed "
            "to a human reviewer rather than automatically classified."
        )
    return (
        f"Confident ({result.confidence:.0%}). At or above the "
        f"{REVIEW_THRESHOLD:.0%} threshold, this prediction can run automatically."
    )


def format_summary(result: PredictionResult) -> str:
    """Build the Markdown summary string shown alongside the confidence bars.

    Args:
        result (PredictionResult): The result of a predict() call.

    Returns:
        str: For empty input, the prompt string asking the user to enter a
            post. Otherwise a Markdown block with the predicted label, its
            plain language description, and the triage hint.
    """
    if result.is_empty:
        return EMPTY_INPUT_PROMPT

    description = LABEL_DESCRIPTIONS.get(result.label, "")
    triage = format_triage_hint(result)
    return f"### Prediction: `{result.label}`\n\n{description}\n\n{triage}"
