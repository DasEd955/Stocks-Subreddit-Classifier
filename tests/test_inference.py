"""Unit tests for takemeter.inference.predict().

Uses the fake_tokenizer/make_fake_model fixtures from conftest.py so these
tests exercise the tokenize -> forward pass -> structured result logic
without loading the real, gitignored fine-tuned checkpoint.
"""

import pytest
from takemeter.inference import REVIEW_THRESHOLD, PredictionResult, predict


def test_empty_string_returns_empty_result_without_calling_model(fake_tokenizer, fake_model, fake_id2label):
    """An empty string should short circuit to is_empty=True and never call the model."""
    result = predict("", fake_tokenizer, fake_model, fake_id2label)

    assert result.is_empty is True
    assert result.label is None
    assert result.confidence == 0.0
    assert result.confidences == {}
    assert result.needs_review is False


def test_whitespace_only_input_is_treated_as_empty(fake_tokenizer, fake_model, fake_id2label):
    """A string of only whitespace should be stripped and treated the same as empty input."""
    result = predict("   \n\t  ", fake_tokenizer, fake_model, fake_id2label)

    assert result.is_empty is True
    assert result.confidences == {}


def test_none_input_is_treated_as_empty(fake_tokenizer, fake_model, fake_id2label):
    """None should be handled gracefully (coerced to empty string) rather than raising."""
    result = predict(None, fake_tokenizer, fake_model, fake_id2label)

    assert result.is_empty is True


def test_predict_returns_prediction_result_instance(fake_tokenizer, fake_model, fake_id2label):
    """predict() should always return a PredictionResult, not a raw tuple or dict."""
    result = predict("some post text", fake_tokenizer, fake_model, fake_id2label)

    assert isinstance(result, PredictionResult)


def test_predict_selects_argmax_label(fake_tokenizer, make_fake_model, fake_id2label):
    """The predicted label should be the class with the highest logit (argmax)."""
    model = make_fake_model(winning_index=2, winning_logit=5.0)

    result = predict("Apple reported record earnings.", fake_tokenizer, model, fake_id2label)

    assert result.label == "News_Information"


def test_predict_confidences_sum_to_one(fake_tokenizer, fake_model, fake_id2label):
    """The full confidence distribution should be a valid softmax output (sums to ~1.0)."""
    result = predict("a post", fake_tokenizer, fake_model, fake_id2label)

    assert sum(result.confidences.values()) == pytest.approx(1.0, abs=1e-5)


def test_predict_confidences_include_all_labels(fake_tokenizer, fake_model, fake_id2label):
    """The confidences dict should have one entry per class in id2label."""
    result = predict("a post", fake_tokenizer, fake_model, fake_id2label)

    assert set(result.confidences.keys()) == set(fake_id2label.values())


def test_predict_flags_low_confidence_for_review(fake_tokenizer, make_fake_model, fake_id2label):
    """A prediction with confidence below REVIEW_THRESHOLD should set needs_review=True."""
    # Near-uniform logits keep the winning softmax probability below the threshold.
    model = make_fake_model(winning_index=0, winning_logit=0.05, other_logit=0.0)

    result = predict("an ambiguous post", fake_tokenizer, model, fake_id2label)

    assert result.confidence < REVIEW_THRESHOLD
    assert result.needs_review is True


def test_predict_does_not_flag_high_confidence_for_review(fake_tokenizer, make_fake_model, fake_id2label):
    """A prediction with confidence at or above REVIEW_THRESHOLD should set needs_review=False."""
    model = make_fake_model(winning_index=1, winning_logit=6.0, other_logit=0.0)

    result = predict("a clear post", fake_tokenizer, model, fake_id2label)

    assert result.confidence >= REVIEW_THRESHOLD
    assert result.needs_review is False


def test_predict_confidence_matches_winning_label_probability(fake_tokenizer, make_fake_model, fake_id2label):
    """result.confidence should equal confidences[result.label], not an independently computed value."""
    model = make_fake_model(winning_index=3, winning_logit=4.0)

    result = predict("a post", fake_tokenizer, model, fake_id2label)

    assert result.confidence == pytest.approx(result.confidences[result.label])
