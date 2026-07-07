"""app.py - Gradio inference interface for the TakeMeter r/stocks discourse quality classifier.

The UI is intentionally thin. All classification logic lives in the takemeter
package (takemeter.model_loader, takemeter.inference, takemeter.formatting);
this module only wires the Gradio Blocks layout to that package's predict()
and format_*() functions. Keeping the split this way means the "tokenize ->
forward pass -> structured result" logic in takemeter.inference is testable,
and reusable, without importing Gradio at all.

classify() is the single Gradio callback. It calls takemeter.inference.predict()
to get a structured PredictionResult, then takemeter.formatting to turn that
into the {label: confidence} dict and Markdown summary the two Gradio output
panels expect.

Run with:
    python app.py

Then open the localhost URL shown in your terminal (usually http://localhost:7860).
The trained model directory (model/takemeter-model) is gitignored due to size. Train it
via model/model_notebook.ipynb or set TAKEMETER_MODEL_DIR to an existing checkpoint.
"""

import gradio as gr
from takemeter.examples import EXAMPLES
from takemeter.formatting import format_confidences, format_summary
from takemeter.inference import predict
from takemeter.model_loader import load_model, resolve_model_dir

MODEL_DIR = resolve_model_dir()
print(f"Loading model from: {MODEL_DIR}")

tokenizer, model, id2label = load_model(MODEL_DIR)


def classify(post: str):
    """Classify a single r/stocks post and return Gradio output values.

    Args:
        post (str): Raw text of a Reddit r/stocks post or comment.

    Returns:
        tuple[dict[str, float], str]:
            - A {label: confidence} dict consumed by gr.Label (all four classes,
              so the full distribution is visible in the confidence bar chart).
            - A Markdown string with the predicted label name, its plain-language
              description, and the triage hint.
            On empty input, returns ({}, prompt string) without running the model.
    """
    result = predict(post, tokenizer, model, id2label)
    return format_confidences(result), format_summary(result)


# Main Gradio interface definition. The left column has the input textbox, classify button, and example buttons;
# the right column has the Markdown summary and confidence bar chart. Both the button click and textbox submit trigger
# the same classify() callback so users can choose their preferred interaction pattern.
with gr.Blocks(title="TakeMeter - r/stocks Discourse Quality Classifier") as demo:
    gr.Markdown(
        "# TakeMeter\n"
        "### r/stocks Discourse Quality Classifier\n"
        "Paste a Reddit r/stocks post below. The fine-tuned DistilBERT model labels it "
        "as one of four discourse quality categories and reports its confidence.\n\n"
        "**Labels:** `Evidence_Based_Analysis` . `Interpretive_Opinion` . "
        "`News_Information` . `Low_Quality_Misleading`"
    )
    with gr.Row():
        with gr.Column(scale=3):
            post_input = gr.Textbox(
                label="Reddit post",
                placeholder="Paste a post from r/stocks here...",
                lines=10,
            )
            classify_btn = gr.Button("Classify", variant="primary")
            gr.Examples(examples=[[e] for e in EXAMPLES], inputs=post_input)
        with gr.Column(scale=2):
            summary_output = gr.Markdown()
            label_output = gr.Label(label="Confidence by class", num_top_classes=4)

    classify_btn.click(
        fn=classify,
        inputs=post_input,
        outputs=[label_output, summary_output],
    )
    post_input.submit(
        fn=classify,
        inputs=post_input,
        outputs=[label_output, summary_output],
    )


if __name__ == "__main__":
    demo.launch()
