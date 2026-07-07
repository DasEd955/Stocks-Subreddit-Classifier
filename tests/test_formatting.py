"""Unit tests for takemeter.formatting.

Builds PredictionResult objects directly (no model needed) to test the
display formatting functions in isolation from inference and Gradio.
"""

from takemeter.formatting import (
    EMPTY_INPUT_PROMPT,
    LABEL_DESCRIPTIONS,
    format_confidences,
    format_summary,
    format_triage_hint,
)
from takemeter.inference import REVIEW_THRESHOLD, PredictionResult


def _result(label="Interpretive_Opinion", confidence=0.75, is_empty=False, needs_review=None):
    """Build a PredictionResult for formatting tests without running a model.

    Args:
        label (str): Predicted label name.
        confidence (float): Winning class confidence.
        is_empty (bool): Whether to simulate the empty-input case.
        needs_review (bool, optional): Explicit override; defaults to
            confidence < REVIEW_THRESHOLD if not provided.

    Returns:
        PredictionResult: A result object suitable for passing to the
            format_* functions under test.
    """
    if needs_review is None:
        needs_review = confidence < REVIEW_THRESHOLD
    confidences = {} if is_empty else {label: confidence, "News_Information": 1 - confidence}
    return PredictionResult(
        label=None if is_empty else label,
        confidence=0.0 if is_empty else confidence,
        confidences=confidences,
        needs_review=False if is_empty else needs_review,
        is_empty=is_empty,
    )


def test_format_confidences_passes_through_dict():
    """format_confidences() should return the result's confidences dict unchanged."""
    result = _result(confidence=0.8)

    assert format_confidences(result) == result.confidences


def test_format_confidences_empty_for_empty_input():
    """format_confidences() should return an empty dict for empty-input results."""
    result = _result(is_empty=True)

    assert format_confidences(result) == {}


def test_format_summary_returns_prompt_for_empty_input():
    """format_summary() should return the empty-input prompt string, not a label block."""
    result = _result(is_empty=True)

    assert format_summary(result) == EMPTY_INPUT_PROMPT


def test_format_summary_includes_predicted_label():
    """format_summary() should include the predicted label name in its output."""
    result = _result(label="News_Information", confidence=0.9)

    summary = format_summary(result)

    assert "News_Information" in summary


def test_format_summary_includes_label_description():
    """format_summary() should include the plain-language description for the predicted label."""
    result = _result(label="Low_Quality_Misleading", confidence=0.9)

    summary = format_summary(result)

    assert LABEL_DESCRIPTIONS["Low_Quality_Misleading"] in summary


def test_format_summary_includes_triage_hint():
    """format_summary() should embed the same text produced by format_triage_hint()."""
    result = _result(label="Evidence_Based_Analysis", confidence=0.9)

    summary = format_summary(result)

    assert format_triage_hint(result) in summary


def test_format_triage_hint_flags_low_confidence():
    """Below threshold confidence should produce a hint mentioning human review."""
    result = _result(confidence=0.4, needs_review=True)

    hint = format_triage_hint(result)

    assert "review" in hint.lower()
    assert "40%" in hint


def test_format_triage_hint_confirms_high_confidence():
    """At/above threshold confidence should produce a hint confirming automatic classification."""
    result = _result(confidence=0.85, needs_review=False)

    hint = format_triage_hint(result)

    assert "automatically" in hint.lower()
    assert "85%" in hint


def test_format_summary_handles_unknown_label_gracefully():
    """A label not present in LABEL_DESCRIPTIONS should not raise a KeyError."""
    result = _result(label="Some_New_Label", confidence=0.9)

    summary = format_summary(result)

    assert "Some_New_Label" in summary
