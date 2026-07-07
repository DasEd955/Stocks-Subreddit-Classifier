"""model_loader.py - Locate and load the fine-tuned TakeMeter checkpoint.

resolve_model_dir() handles the two level checkpoint layout produced by Hugging
Face Trainer: if the target directory lacks config.json (i.e. it is the parent
output dir), it auto selects the latest checkpoint-* subdirectory. An explicit
TAKEMETER_MODEL_DIR env var overrides the default model/takemeter-model path so
the app can be pointed at any compatible checkpoint without editing the source.

load_model() wraps resolve_model_dir() and returns the loaded tokenizer, model,
and id2label mapping, ready for inference.py to use.
"""

import os
import re
from pathlib import Path

# Repo root: two levels up from this file (takemeter/model_loader.py -> repo root).
REPO_ROOT = Path(__file__).resolve().parent.parent


def resolve_model_dir(repo_root: Path = REPO_ROOT) -> Path:
    """Find the saved model directory.

    Precedence:
      1. TAKEMETER_MODEL_DIR env var, if set.
      2. The default local checkpoint shipped with the repo layout
         (<repo_root>/model/takemeter-model).
    If the resolved path is a parent `takemeter-model` directory containing
    `checkpoint-*` subfolders, auto-select the latest checkpoint.

    Args:
        repo_root (Path): Root directory the default model path is relative to.
            Defaults to this repo's root; overridable for testing.

    Returns:
        Path: Directory containing config.json for the resolved checkpoint.

    Raises:
        FileNotFoundError: If no directory containing config.json can be found
            at the resolved location.
    """
    default = repo_root / "model" / "takemeter-model"
    model_dir = Path(os.environ.get("TAKEMETER_MODEL_DIR", default))

    # If pointed at the Trainer output dir, descend into the latest checkpoint.
    if model_dir.is_dir() and not (model_dir / "config.json").exists():
        checkpoints = sorted(
            model_dir.glob("checkpoint-*"),
            key=lambda p: int(m.group()) if (m := re.search(r"\d+$", p.name)) else -1,
        )
        if checkpoints:
            model_dir = checkpoints[-1]

    if not (model_dir / "config.json").exists():
        raise FileNotFoundError(
            f"No model found at '{model_dir}'. The trained model is gitignored - "
            "train it via model/model_notebook.ipynb and place the saved "
            "'takemeter-model' directory under 'model/', or set the "
            "TAKEMETER_MODEL_DIR environment variable to its location."
        )
    return model_dir


def load_model(model_dir: Path = None):
    """Load the tokenizer, model, and label mapping for a resolved checkpoint.

    Args:
        model_dir (Path, optional): Directory to load from. If None, resolved
            via resolve_model_dir().

    Returns:
        tuple[AutoTokenizer, AutoModelForSequenceClassification, dict[int, str]]:
            The tokenizer, the model in eval() mode, and the id2label mapping
            read from the model's own config (the source of truth).
    """
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    if model_dir is None:
        model_dir = resolve_model_dir()

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()

    id2label = {int(k): v for k, v in model.config.id2label.items()}
    return tokenizer, model, id2label
