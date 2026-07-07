"""Unit tests for takemeter.model_loader.resolve_model_dir().

These tests build small fake directory trees under tmp_path so they cover the
path resolution logic (env var precedence, checkpoint auto-selection, missing
model error) without needing the real, gitignored trained checkpoint.
"""

import pytest
from takemeter.model_loader import resolve_model_dir


def _touch_config(directory):
    """Create directory (and parents) and drop an empty config.json inside it.

    Args:
        directory (Path): Directory to create and mark as a valid model dir.
    """
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "config.json").write_text("{}")


def test_resolves_default_path_when_config_present(tmp_path):
    """resolve_model_dir() should return model/takemeter-model when it directly contains config.json."""
    model_dir = tmp_path / "model" / "takemeter-model"
    _touch_config(model_dir)

    resolved = resolve_model_dir(repo_root=tmp_path)

    assert resolved == model_dir


def test_auto_selects_latest_checkpoint_by_numeric_suffix(tmp_path):
    """When the default dir has no config.json but has checkpoint-* children, pick the highest-numbered one."""
    parent = tmp_path / "model" / "takemeter-model"
    _touch_config(parent / "checkpoint-8")
    _touch_config(parent / "checkpoint-56")
    _touch_config(parent / "checkpoint-120")

    resolved = resolve_model_dir(repo_root=tmp_path)

    assert resolved.name == "checkpoint-120"


def test_env_var_overrides_default_path(tmp_path, monkeypatch):
    """TAKEMETER_MODEL_DIR should take precedence over the default model/takemeter-model path."""
    default_dir = tmp_path / "model" / "takemeter-model"
    _touch_config(default_dir)

    override_dir = tmp_path / "elsewhere" / "custom-checkpoint"
    _touch_config(override_dir)
    monkeypatch.setenv("TAKEMETER_MODEL_DIR", str(override_dir))

    resolved = resolve_model_dir(repo_root=tmp_path)

    assert resolved == override_dir


def test_raises_file_not_found_when_no_model_present(tmp_path):
    """resolve_model_dir() should raise FileNotFoundError when nothing exists at the resolved path."""
    with pytest.raises(FileNotFoundError, match="No model found"):
        resolve_model_dir(repo_root=tmp_path)


def test_raises_file_not_found_when_parent_dir_has_no_checkpoints(tmp_path):
    """An empty takemeter-model directory (no config.json, no checkpoint-* subfolders) should still raise."""
    parent = tmp_path / "model" / "takemeter-model"
    parent.mkdir(parents=True)

    with pytest.raises(FileNotFoundError):
        resolve_model_dir(repo_root=tmp_path)


def test_error_message_mentions_env_var_and_notebook(tmp_path):
    """The FileNotFoundError message should point users at TAKEMETER_MODEL_DIR and the training notebook."""
    with pytest.raises(FileNotFoundError) as exc_info:
        resolve_model_dir(repo_root=tmp_path)

    message = str(exc_info.value)
    assert "TAKEMETER_MODEL_DIR" in message
    assert "model_notebook.ipynb" in message
