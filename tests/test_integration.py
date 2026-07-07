"""Integration tests for the TakeMeter classification pipeline.

Unlike test_inference.py and test_formatting.py (which use fake models to
test each function in isolation), these tests wire the real components
together end to end: takemeter.model_loader.load_model() loads the actual
fine-tuned checkpoint, and predict() + format_summary()/format_confidences()
run on it directly, the same call chain app.py's classify() uses.

These tests require the trained checkpoint at model/takemeter-model, which is
gitignored due to size. They are automatically skipped (via the
real_model_components fixture in conftest.py) if that checkpoint is not
present, e.g. on a fresh clone before running model/model_notebook.ipynb.
"""

import pytest
from takemeter.formatting import format_confidences, format_summary
from takemeter.inference import PredictionResult, predict


def test_real_model_loads_with_four_class_label_mapping(real_model_components):
    """The loaded checkpoint's id2label should expose exactly the four documented taxonomy classes."""
    _, _, id2label = real_model_components

    assert len(id2label) == 4
    assert set(id2label.values()) == {
        "Evidence_Based_Analysis",
        "Interpretive_Opinion",
        "News_Information",
        "Low_Quality_Misleading",
    }


def test_real_model_predicts_on_a_clear_news_post(real_model_components):
    """A clear, factual news style post should run through predict() and return a valid PredictionResult."""
    tokenizer, model, id2label = real_model_components

    post = (
        "Apple reported Q2 FY2025 revenue of $95.4B, up 5% YoY. "
        "Services revenue hit a new record at $26.6B. EPS of $1.65 beat consensus by $0.04."
    )
    result = predict(post, tokenizer, model, id2label)

    assert isinstance(result, PredictionResult)
    assert result.is_empty is False
    assert result.label in id2label.values()
    assert 0.0 <= result.confidence <= 1.0


def test_real_model_end_to_end_matches_app_classify_shape(real_model_components):
    """predict() -> format_confidences()/format_summary() should produce the same shapes app.classify() returns."""
    tokenizer, model, id2label = real_model_components

    post = "GME to $500 by end of month. Shorts are TRAPPED. This is the squeeze of the decade."
    result = predict(post, tokenizer, model, id2label)
    confidences = format_confidences(result)
    summary = format_summary(result)

    assert isinstance(confidences, dict)
    assert set(confidences.keys()) == set(id2label.values())
    assert isinstance(summary, str)
    assert result.label in summary


def test_real_model_empty_input_short_circuits_without_touching_model(real_model_components):
    """Empty input should still short circuit to the prompt string even with the real model loaded."""
    tokenizer, model, id2label = real_model_components

    result = predict("", tokenizer, model, id2label)

    assert result.is_empty is True
    assert format_summary(result) == "Enter a post above and press **Classify**."


def test_real_model_confidence_distribution_sums_to_one(real_model_components):
    """The real model's softmax output over all four classes should sum to ~1.0."""
    tokenizer, model, id2label = real_model_components

    post = "I think tech stocks feel overextended right now, just a gut read."
    result = predict(post, tokenizer, model, id2label)

    assert sum(result.confidences.values()) == pytest.approx(1.0, abs=1e-4)


def test_app_module_builds_gradio_demo_without_error():
    """Importing app.py should load the model and build a gr.Blocks demo without raising.

    This is the closest thing to a UI smoke test without launching a server:
    it exercises the exact import time wiring (model load -> Blocks layout)
    that a user hits when running `python app.py`.
    """
    pytest.importorskip("gradio")

    try:
        import app
    except FileNotFoundError:
        pytest.skip("Trained model checkpoint not found; skipping app.py import test.")

    assert app.demo is not None
    assert callable(app.classify)
