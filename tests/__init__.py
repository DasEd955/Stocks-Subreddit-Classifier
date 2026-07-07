"""tests - pytest suite for the TakeMeter r/stocks discourse quality classifier.

Covers the takemeter package (model_loader, inference, formatting, examples)
with fast unit tests that do not require the trained checkpoint, plus a
smaller set of integration tests that exercise the real fine-tuned model when
it is present on disk (model/takemeter-model, gitignored) and skip themselves
otherwise. See tests/conftest.py for the shared fixtures both layers use.
"""
