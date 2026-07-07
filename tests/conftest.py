"""Shared pytest fixtures for the TakeMeter test suite.

Two model fixtures are provided:

- fake_tokenizer/fake_model/fake_id2label: a tiny hand-built stand-in that
  mimics the Hugging Face tokenizer/model call signatures used by
  takemeter.inference.predict(). These make the inference and formatting unit
  tests fast and independent of the large gitignored checkpoint under
  model/takemeter-model.
- real_model_components: the actual trained checkpoint, loaded once per test
  session via takemeter.model_loader.load_model(). Tests that need it should
  request this fixture; it is automatically skipped if the checkpoint is not
  present on disk (it is gitignored and not always available, e.g. in CI).
"""

import sys
from pathlib import Path
import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

LABELS = ["Evidence_Based_Analysis", "Interpretive_Opinion", "News_Information", "Low_Quality_Misleading"]


class FakeTokenizerOutput(dict):
    """Minimal stand-in for a BatchEncoding; supports **inputs unpacking."""


class FakeTokenizer:
    """Stand-in tokenizer that mimics the AutoTokenizer call signature used in predict().

    Ignores the actual text content and returns fixed-shape dummy tensors, since
    the fake model below only cares about batch size, not real token ids.
    """

    def __call__(self, text, truncation=True, max_length=256, return_tensors="pt"):
        """Return dummy input_ids/attention_mask tensors regardless of text content.

        Args:
            text (str): The post text (ignored; content does not affect output).
            truncation (bool): Accepted for signature compatibility; unused.
            max_length (int): Accepted for signature compatibility; unused.
            return_tensors (str): Accepted for signature compatibility; unused.

        Returns:
            FakeTokenizerOutput: A dict-like object with input_ids and
                attention_mask tensors for a single 3-token sequence.
        """
        return FakeTokenizerOutput(
            input_ids=torch.tensor([[101, 2000, 102]]),
            attention_mask=torch.tensor([[1, 1, 1]]),
        )


class FakeModelOutput:
    """Minimal stand-in for a Hugging Face SequenceClassifierOutput."""

    def __init__(self, logits):
        """Store the fixed logits tensor this fake forward pass should return.

        Args:
            logits (torch.Tensor): Shape (1, num_labels) logits tensor.
        """
        self.logits = logits


class FakeModel:
    """Stand-in model that returns fixed logits regardless of input.

    next_logits is mutable per-test so different tests can drive different
    predicted labels/confidences without needing a real forward pass.
    """

    def __init__(self, logits):
        """Store the logits this fake model's forward pass will always return.

        Args:
            logits (torch.Tensor): Shape (1, num_labels) logits tensor.
        """
        self.next_logits = logits

    def __call__(self, input_ids=None, attention_mask=None):
        """Return a fixed FakeModelOutput regardless of the given inputs.

        Args:
            input_ids (torch.Tensor, optional): Accepted for signature
                compatibility; unused.
            attention_mask (torch.Tensor, optional): Accepted for signature
                compatibility; unused.

        Returns:
            FakeModelOutput: Wraps this instance's fixed next_logits tensor.
        """
        return FakeModelOutput(logits=self.next_logits)

    def eval(self):
        """Mimic torch.nn.Module.eval() by returning self for chaining."""
        return self


@pytest.fixture
def fake_id2label():
    """Return the standard 4-class id2label mapping used across the test suite."""
    return dict(enumerate(LABELS))


@pytest.fixture
def fake_tokenizer():
    """Return a FakeTokenizer instance for use in predict() unit tests."""
    return FakeTokenizer()


@pytest.fixture
def make_fake_model():
    """Factory fixture: build a FakeModel that argmaxes to a chosen class.

    Usage: make_fake_model(winning_index=3, winning_logit=4.0) returns a model
    whose forward pass produces softmax probabilities peaked on class 3.

    Returns:
        Callable[..., FakeModel]: A factory function accepting winning_index,
            winning_logit, and other_logit keyword arguments.
    """

    def _make(winning_index=0, winning_logit=3.0, other_logit=0.0):
        """Build a FakeModel whose fixed logits peak at winning_index.

        Args:
            winning_index (int): Class index that should win the argmax.
            winning_logit (float): Logit value assigned to winning_index.
            other_logit (float): Logit value assigned to all other classes.

        Returns:
            FakeModel: A model whose forward pass always returns these logits.
        """
        logits = torch.full((1, len(LABELS)), float(other_logit))
        logits[0, winning_index] = float(winning_logit)
        return FakeModel(logits)

    return _make


@pytest.fixture
def fake_model(make_fake_model):
    """Return a default FakeModel that predicts class 0 with high confidence."""
    return make_fake_model(winning_index=0, winning_logit=3.0)


def _resolve_real_model_dir():
    """Resolve the real trained checkpoint's directory, or None if not found.

    Returns:
        Path | None: The resolved model directory, or None if
            takemeter.model_loader.resolve_model_dir() raises FileNotFoundError.
    """
    from takemeter.model_loader import resolve_model_dir

    try:
        return resolve_model_dir()
    except FileNotFoundError:
        return None


@pytest.fixture(scope="session")
def real_model_components():
    """Load the real fine-tuned checkpoint once per test session.

    Skips the test if the checkpoint is not present on disk, since
    model/takemeter-model is gitignored and not guaranteed to exist in every
    environment (e.g. a fresh clone or CI without the trained artifact).

    Returns:
        tuple: (tokenizer, model, id2label) as returned by
            takemeter.model_loader.load_model().
    """
    model_dir = _resolve_real_model_dir()
    if model_dir is None:
        pytest.skip("Trained model checkpoint not found under model/takemeter-model; skipping.")

    from takemeter.model_loader import load_model

    tokenizer, model, id2label = load_model(model_dir)
    return tokenizer, model, id2label
