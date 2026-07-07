"""Unit tests for takemeter.examples.EXAMPLES.

Covers the shape and basic content invariants of the curated example list
shown in the Gradio interface, since a malformed entry (wrong type, empty
string) would silently break gr.Examples at UI build time.
"""

from takemeter.examples import EXAMPLES


def test_examples_is_nonempty_list():
    """EXAMPLES should be a non-empty list, matching the eight curated posts described in its docstring."""
    assert isinstance(EXAMPLES, list)
    assert len(EXAMPLES) > 0


def test_examples_are_all_nonempty_strings():
    """Every entry in EXAMPLES should be a non-blank string suitable for a gr.Textbox default."""
    for example in EXAMPLES:
        assert isinstance(example, str)
        assert example.strip() != ""


def test_examples_has_expected_count():
    """EXAMPLES should contain exactly eight posts: four boundary cases and four clear cases."""
    assert len(EXAMPLES) == 8


def test_examples_are_unique():
    """No two example posts should be identical, since duplicates add no value to the UI."""
    assert len(set(EXAMPLES)) == len(EXAMPLES)
