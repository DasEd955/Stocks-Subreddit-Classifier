"""Unit tests for the labeled dataset at data/data.csv.

Validates the structural invariants the rest of the project assumes: the
expected columns exist, every label belongs to the 4-class taxonomy
documented in README.md and planning.md, and there are no fully blank rows.
These tests protect against silent corruption of the dataset (e.g. a bad
manual edit) rather than testing model code.
"""

from pathlib import Path
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = REPO_ROOT / "data" / "data.csv"

EXPECTED_LABELS = {
    "Evidence_Based_Analysis",
    "Interpretive_Opinion",
    "News_Information",
    "Low_Quality_Misleading",
}


@pytest.fixture(scope="module")
def data_df():
    """Load data/data.csv once for all tests in this module.

    Skips the module's tests if the CSV is not present on disk.

    Returns:
        pandas.DataFrame: The loaded labeled dataset.
    """
    if not DATA_CSV.exists():
        pytest.skip(f"{DATA_CSV} not found; skipping dataset tests.")
    return pd.read_csv(DATA_CSV)


def test_data_has_expected_columns(data_df):
    """data.csv should have the id, text, label, and source columns the notebook expects."""
    assert list(data_df.columns) == ["id", "text", "label", "source"]


def test_data_labels_are_within_taxonomy(data_df):
    """Every row's label should be one of the four defined discourse-quality classes."""
    actual_labels = set(data_df["label"].unique())

    assert actual_labels <= EXPECTED_LABELS


def test_data_has_no_missing_text_or_label(data_df):
    """No row should have a blank text or label field, since that would break tokenization/training."""
    assert data_df["text"].isna().sum() == 0
    assert data_df["label"].isna().sum() == 0


def test_data_has_no_duplicate_ids(data_df):
    """The id column should be unique so each row can be traced back to a single annotated example."""
    assert data_df["id"].is_unique


def test_data_matches_documented_total_count(data_df):
    """The README and planning.md report 310 annotated examples; the CSV should match that count."""
    assert len(data_df) == 310


def test_data_matches_documented_label_distribution(data_df):
    """Per-label counts should match the distribution table documented in README.md and planning.md."""
    expected_counts = {
        "Interpretive_Opinion": 116,
        "News_Information": 68,
        "Low_Quality_Misleading": 65,
        "Evidence_Based_Analysis": 61,
    }
    actual_counts = data_df["label"].value_counts().to_dict()

    assert actual_counts == expected_counts
