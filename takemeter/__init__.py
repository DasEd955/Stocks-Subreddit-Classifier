"""takemeter - Core package for the TakeMeter r/stocks discourse quality classifier.

This package separates the model-based logic (path resolution, model loading,
tokenization, inference) from the Gradio UI defined in app.py, so the
classification logic can be reused in a batch script or an API endpoint
without importing Gradio at all.

Modules:
    model_loader.py - resolve_model_dir() and load_model() for locating and
        loading the fine-tuned checkpoint.
    inference.py - predict(), the pure tokenize -> forward pass -> structured
        result function. Has no knowledge of Gradio or display formatting.
    formatting.py - format_confidences() and format_summary(), which turn a
        PredictionResult into the shapes the UI renders.
    examples.py - The curated EXAMPLES list of sample r/stocks posts used by the
        Gradio interface.
"""
