"""gen_diagrams.py - One-Time generator for the TakeMeter architecture diagrams.

Produces two PNG diagrams in the scripts/ directory that document the project's
architecture at two levels of detail:

  1. Model-Architecture.png — the fine-tuned DistilBERT classification pipeline:
     input text → WordPiece tokenizer → embedding layer → 6-layer transformer encoder
     → [CLS] pooling → pre-classifier Linear → classification head Linear(768→4)
     → softmax probabilities. Includes the training configuration footer (dataset
     split, WeightedTrainer class weights, optimizer schedule, test-set metrics).

  2. Repo-Architecture.png — the full repository pipeline:
     labeled CSV → fine-tuning notebook (Colab/T4) vs. Groq zero-shot baseline →
     saved checkpoint-56 → Gradio inference app → browser user. Includes the
     committed results/ artifacts panel.

Both diagrams are rendered with Pillow using a dark background palette. Layout
helpers make_box() and make_varrow() are returned as closures capturing the
ImageDraw instance so each diagram gets its own independent drawing surface.
font() and center() are module-level utilities shared by both diagrams.

Font loading tries a short list of common TrueType font paths (Windows, then
macOS, then Linux) and falls back to Pillow's built-in bitmap font with a
printed warning if none are found. This keeps the script runnable on any OS
and in CI, though the fallback font ignores the requested point size and
diagram text will look smaller/plainer than the TrueType rendering.

Run with:
    python scripts/gen_diagrams.py

from the repo root. Output files are written alongside this script in scripts/.
Requires: Pillow (pip install pillow).
"""
from PIL import Image, ImageDraw, ImageFont

# ── Shared Palette / Fonts ────────────────────────────────────────────────
BG = (23, 23, 26)
INK = (235, 236, 238)
SUB = (188, 192, 200)
ARROW = (150, 154, 162)

# Candidate paths per font role, checked in order. Covers Windows, macOS, and
# common Linux (DejaVu is bundled with most distros' fontconfig packages).
_FONT_CANDIDATES = {
    "regular": [
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "bold": [
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "mono": [
        "C:/Windows/Fonts/consola.ttf",
        "/System/Library/Fonts/Supplemental/Andale Mono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ],
}

F = _FONT_CANDIDATES["regular"][0]
FB = _FONT_CANDIDATES["bold"][0]
FM = _FONT_CANDIDATES["mono"][0]

_warned_fallback = False


def font(path, size):
    """Load a TrueType font at the given point size, with a portable fallback.

    Tries the requested path first, then the other OS candidates for whichever
    role that path belongs to (regular, bold, or mono), and finally falls back
    to Pillow's built-in bitmap font if nothing on disk matches. The fallback
    is logged once so a missing font set is visible instead of silently
    changing the diagram's appearance.

    Args:
        path (str): Absolute path to the preferred .ttf font file.
        size (int): Point size to load. Ignored by the bitmap fallback.

    Returns:
        ImageFont.FreeTypeFont | ImageFont.ImageFont: The loaded font object.
    """
    global _warned_fallback

    role = next((r for r, paths in _FONT_CANDIDATES.items() if path in paths), None)
    candidates = _FONT_CANDIDATES.get(role, [path]) if role else [path]

    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue

    if not _warned_fallback:
        print(
            "Warning: no TrueType fonts found from the known candidate paths. "
            "Falling back to Pillow's default bitmap font; diagram text will "
            "render smaller and without bold/mono styling."
        )
        _warned_fallback = True
    return ImageFont.load_default()


f_title = font(FB, 32)
f_sub = font(F, 17)
f_stage = font(FB, 23)
f_detail = font(F, 15)
f_mono = font(FM, 13)
f_small = font(F, 13)
f_smallb = font(FB, 14)
f_label = font(FB, 14)
f_smallmono = font(FM, 12)


def center(draw, cx, y, text, fnt, fill):
    """Draw text horizontally centered on the given x coordinate.

    Args:
        draw (ImageDraw.ImageDraw): The draw context to render into.
        cx (float): The x coordinate of the desired center.
        y (float): The top y coordinate for the text baseline.
        text (str): The string to render.
        fnt (ImageFont.FreeTypeFont): The font to use.
        fill (tuple[int, int, int]): RGB fill color.
    """
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def make_box(d):
    """Return a box drawing closure bound to the given ImageDraw context.

    The returned box() function draws a rounded rectangle with an optional
    title, subtitle, and list of detail lines, stacking them vertically from
    the top of the box. All text is either centered or left-aligned depending
    on the align_center flag.

    Args:
        d (ImageDraw.ImageDraw): The draw context to bind the closure to.

    Returns:
        Callable: box(x, y, w, h, fill, title, lines, *, title_font,
            line_font, title_fill, line_fill, radius, align_center, sub)
            that draws one diagram block and returns its bounding rect as
            (x, y, x+w, y+h).
    """
    def box(x, y, w, h, fill, title=None, lines=None, *, title_font=f_stage,
            line_font=f_detail, title_fill=INK, line_fill=(225, 228, 234),
            radius=14, align_center=True, sub=None):
        d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill)
        cx = x + w / 2
        cy = y + 14
        if title:
            if align_center:
                center(d, cx, cy, title, title_font, title_fill)
            else:
                d.text((x + 16, cy), title, font=title_font, fill=title_fill)
            cy += title_font.size + 8
        if sub:
            if align_center:
                center(d, cx, cy, sub, f_small, SUB)
            else:
                d.text((x + 16, cy), sub, font=f_small, fill=SUB)
            cy += f_small.size + 8
        for ln in (lines or []):
            if align_center:
                center(d, cx, cy, ln, line_font, line_fill)
            else:
                d.text((x + 16, cy), ln, font=line_font, fill=line_fill)
            cy += line_font.size + 5
        return (x, y, x + w, y + h)
    return box


def make_varrow(d):
    """Return a vertical arrow drawing closure bound to the given ImageDraw context.

    The returned varrow() function draws a downward-pointing arrow (line + filled
    triangle head) between two y coordinates, with an optional pill label centered
    on the shaft.

    Args:
        d (ImageDraw.ImageDraw): The draw context to bind the closure to.

    Returns:
        Callable: varrow(cx, y0, y1, label=None) that draws one connector arrow.
            cx is the horizontal center; y0 and y1 are the top and bottom y
            coordinates; label is an optional string drawn on a dark background
            pill beside the shaft.
    """
    def varrow(cx, y0, y1, label=None):
        d.line([cx, y0, cx, y1], fill=ARROW, width=3)
        d.polygon([(cx - 7, y1 - 10), (cx + 7, y1 - 10), (cx, y1)], fill=ARROW)
        if label:
            w = d.textlength(label, font=f_label)
            pad = 7
            ly = (y0 + y1) / 2 - f_label.size / 2
            d.rectangle([cx + 14, ly - pad + 2, cx + 14 + w + 2 * pad,
                         ly + f_label.size + pad - 2], fill=BG)
            d.text((cx + 14 + pad, ly), label, font=f_label, fill=(210, 213, 220))
    return varrow


# ===========================================================================
# DIAGRAM 1 — Fine-tuned DistilBERT model architecture
# ===========================================================================
def gen_model_diagram(out_path):
    """Render the fine-tuned DistilBERT model architecture diagram and save it as a PNG.

    Draws the full inference pipeline from raw input text through the WordPiece
    tokenizer, embedding layer, 6-layer transformer encoder, [CLS] pooling,
    pre-classifier Linear, and classification head to the four output classes.
    A side panel annotates fine-tuning scope (all backbone layers trainable) and
    a footer panel summarizes the training configuration (dataset split, class
    weights, optimizer schedule, and test-set metrics).

    Args:
        out_path (str | os.PathLike): Destination path for the output PNG.

    Side effects:
        Writes a 1180×1500 PNG to out_path and prints the path and size to stdout.
    """
    W, H = 1180, 1500
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    box = make_box(d)
    varrow = make_varrow(d)

    CX = 520
    BW = 600
    LX = CX - BW / 2

    # Palette
    C_IN = (38, 110, 74)      # green  - input text
    C_TOK = (31, 111, 92)     # teal   - tokenizer
    C_EMB = (74, 62, 140)     # indigo - embeddings
    C_ENC = (33, 86, 166)     # blue   - transformer encoder
    C_POOL = (122, 102, 36)   # gold   - pooled representation
    C_HEAD = (138, 52, 40)    # red    - classification head
    C_OUT = (70, 72, 80)      # gray   - output
    C_SIDE = (44, 44, 50)     # side notes
    C_TRAIN = (58, 53, 86)    # training config

    # ---- Title -----------------------------------------------------------
    center(d, W / 2, 26, "Fine-Tuned DistilBERT Classifier", f_title, INK)
    center(d, W / 2, 66,
           "TakeMeter  -  r/stocks discourse-quality classifier  (model/model_notebook.ipynb)",
           f_sub, SUB)

    # ---- Input -----------------------------------------------------------
    y = 108
    box(LX, y, BW, 70, C_IN,
        title="Input  -  Reddit r/stocks post (text)",
        lines=["one post/comment string  .  4-class discourse-quality label"],
        title_font=f_stage, line_font=f_small)
    varrow(CX, y + 70, y + 70 + 36, "raw text")

    # ---- Tokenizer -------------------------------------------------------
    y = 250
    box(LX, y, BW, 118, C_TOK,
        title="WordPiece Tokenizer",
        sub="AutoTokenizer  .  distilbert-base-uncased",
        lines=["lowercase + WordPiece  ->  input_ids, attention_mask",
               "truncation=True  .  max_length = 256",
               "DataCollatorWithPadding (dynamic per-batch padding)"])
    varrow(CX, y + 118, y + 118 + 40, "input_ids + attention_mask")

    # ---- Embeddings ------------------------------------------------------
    y = 408
    box(LX, y, BW, 100, C_EMB,
        title="Embedding Layer",
        sub="dim = 768  .  vocab = 30,522  .  max positions = 512",
        lines=["token embeddings  +  positional embeddings",
               "LayerNorm  +  dropout (0.1)"])
    varrow(CX, y + 100, y + 100 + 40, "768-d token vectors")

    # ---- Transformer Encoder --------------------------------------------
    y = 548
    box(LX, y, BW, 168, C_ENC,
        title="Transformer Encoder  x6 layers",
        sub="DistilBERT backbone (6 layers, GELU)",
        lines=["Multi-Head Self-Attention  (12 heads, attn dropout 0.1)",
               "Add & LayerNorm",
               "Feed-Forward  (hidden_dim = 3072, GELU)",
               "Add & LayerNorm",
               "-> contextual hidden states  [seq_len x 768]"])
    # Left Annotation - what is frozen / trained
    box(20, y + 14, 230, 140, C_SIDE,
        title="Fine-tuning", title_font=f_smallb,
        lines=["full backbone weights",
               "  initialized from",
               "  distilbert-base-uncased",
               "  (UNEXPECTED MLM head",
               "   dropped on load)",
               "",
               "all layers trainable"],
        line_font=f_small, align_center=False)
    varrow(CX, y + 168, y + 168 + 40, "[CLS] hidden state (768-d)")

    # ---- Pooled Rep / Pre-Classifier ------------------------------------
    y = 796
    box(LX, y, BW, 96, C_POOL,
        title="Pooled Representation",
        sub="first-token ([CLS]) hidden state",
        lines=["pre_classifier: Linear(768 -> 768) + ReLU",
               "dropout (seq_classif_dropout = 0.2)"])
    varrow(CX, y + 96, y + 96 + 40, "768-d pooled vector")

    # ---- Classification Head --------------------------------------------
    y = 932
    box(LX, y, BW, 92, C_HEAD,
        title="Classification Head",
        sub="newly initialized for this task",
        lines=["classifier: Linear(768 -> 4)  ->  logits",
               "softmax  ->  per-class probabilities"])
    varrow(CX, y + 92, y + 92 + 40, "4 logits / probabilities")

    # ---- Output ----------------------------------------------------------
    y = 1064
    box(LX, y, BW, 110, C_OUT,
        title="Output  -  4 discourse-quality classes",
        lines=["0  Evidence_Based_Analysis      1  Interpretive_Opinion",
               "2  News_Information             3  Low_Quality_Misleading",
               "argmax = predicted label  .  max softmax = confidence"],
        title_font=f_stage, line_font=f_small)

    # ---- Training Config (full-width footer panel) ----------------------
    y = 1210
    box(20, y, W - 40, 210, C_TRAIN,
        title="Training configuration  (Hugging Face Trainer)", title_font=f_smallb,
        lines=[
            "Dataset: 310 labeled posts  ->  stratified 70/15/15 split  (train 217 / val 46 / test 47)",
            "WeightedTrainer: CrossEntropyLoss with inverse-frequency class weights  [1.27, 0.67, 1.14, 1.19]",
            "Optimizer schedule: 5 epochs  .  lr = 3e-5  .  batch 16  .  weight_decay = 0.01  .  warmup_steps = 50",
            "Eval/save per epoch  .  load_best_model_at_end (metric = accuracy)  .  saved as checkpoint-56",
            "",
            "Test-set results: accuracy = 0.851  (vs. Groq llama-3.3-70b zero-shot baseline 0.809, +0.043)",
            "Macro F1 = 0.86  .  ECE = 0.287  .  errors concentrate on Opinion<->Analysis and LQM<->Opinion boundaries",
        ],
        line_font=f_small, align_center=False)

    # ---- Footer ----------------------------------------------------------
    center(d, W / 2, 1440,
           "Flow: text -> WordPiece tokenize -> embed -> 6x transformer encoder -> [CLS] pool "
           "-> pre_classifier -> Linear(768->4) -> softmax",
           f_small, SUB)

    img.save(out_path)
    print("wrote", out_path, img.size)


# ===========================================================================
# DIAGRAM 2 — Whole Repository Architecture
# ===========================================================================
def gen_repo_diagram(out_path):
    """Render the whole repository architecture diagram and save it as a PNG.

    Draws the end-to-end project pipeline: labeled CSV dataset → fine-tuning
    notebook (Colab/T4) with a Groq zero-shot baseline comparison → saved
    checkpoint-56 artifact → Gradio inference app → browser user. A footer panel
    lists the committed results/ artifacts (evaluation JSON, confusion matrix,
    calibration curve) and their key metrics.

    Args:
        out_path (str | os.PathLike): Destination path for the output PNG.

    Side effects:
        Writes a 1320×1560 PNG to out_path and prints the path and size to stdout.
    """
    W, H = 1320, 1560
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    box = make_box(d)
    varrow = make_varrow(d)

    CX = 540
    BW = 620
    LX = CX - BW / 2

    C_DATA = (38, 110, 74)    # green  - data
    C_NB = (74, 62, 140)      # indigo - notebook / training
    C_MODEL = (33, 86, 166)   # blue   - trained model artifact
    C_APP = (138, 52, 40)     # red    - gradio app
    C_USER = (40, 96, 70)     # user
    C_OUT = (70, 72, 80)      # gray   - outputs
    C_SIDE = (44, 44, 50)
    C_BASE = (122, 102, 36)   # gold   - groq baseline

    # ---- Title -----------------------------------------------------------
    center(d, W / 2, 26, "TakeMeter  -  Repository Architecture", f_title, INK)
    center(d, W / 2, 66,
           "r/stocks discourse-quality classifier  .  data -> fine-tune -> trained model -> takemeter/ -> Gradio UI",
           f_sub, SUB)

    # ---- Data ------------------------------------------------------------
    y = 108
    box(LX, y, BW, 110, C_DATA,
        title="Labeled Dataset",
        sub="data/data.csv  .  data/data.xlsx",
        lines=["310 annotated r/stocks posts  .  columns: id, text, label, source",
               "4 classes (Opinion 116 . News 68 . LQM 65 . Analysis 61)"])
    varrow(CX, y + 110, y + 110 + 36, "CSV upload")

    # ---- Notebook / Training Pipeline -----------------------------------
    y = 290
    box(LX, y, BW, 168, C_NB,
        title="Fine-Tuning Notebook  (Colab / T4 GPU)",
        sub="model/model_notebook.ipynb",
        lines=["1. Load + validate CSV  .  map labels  ->  ids",
               "2. Stratified 70/15/15 split  .  WordPiece tokenize (max_len 256)",
               "3. WeightedTrainer fine-tunes distilbert-base-uncased (5 epochs, lr 3e-5)",
               "4. Evaluate on locked test set  .  confusion matrix . calibration . error analysis",
               "5. Compare vs. Groq zero-shot baseline  .  export artifacts"])
    # Right Annotation - Groq baseline
    box(980, y + 24, 320, 128, C_BASE,
        title="Zero-shot baseline", title_font=f_smallb,
        lines=["groq  .  llama-3.3-70b-versatile",
               "temperature = 0  .  max_tokens = 20",
               "system prompt = label definitions",
               "(planning.md taxonomy)",
               "",
               "test accuracy = 0.809"],
        line_font=f_small, align_center=False)
    d.line([980, y + 84, CX + BW / 2, y + 84], fill=ARROW, width=3)
    d.polygon([(CX + BW / 2 + 10, y + 84 - 6), (CX + BW / 2 + 10, y + 84 + 6),
               (CX + BW / 2, y + 84)], fill=ARROW)
    varrow(CX, y + 168, y + 168 + 40, "saved model + results")

    # ---- Trained Model Artifact -----------------------------------------
    y = 538
    box(LX, y, BW, 120, C_MODEL,
        title="Trained Model  (checkpoint-56)",
        sub="model/takemeter-model/checkpoint-56/  (gitignored)",
        lines=["DistilBERT-for-sequence-classification, 4-class head",
               "model.safetensors  .  config.json (id2label/label2id)",
               "tokenizer.json + vocab  .  trainer_state.json"])
    varrow(CX, y + 120, y + 120 + 40, "load weights + tokenizer")

    # ---- takemeter/ package (model loading + inference + formatting) -----
    y = 698
    box(LX, y, BW, 214, C_APP,
        title="takemeter/ package",
        sub="model_loader.py  .  inference.py  .  formatting.py  .  examples.py",
        lines=["model_loader.resolve_model_dir(): TAKEMETER_MODEL_DIR env or latest checkpoint-*",
               "inference.predict(): tokenize (max_len 256) -> model.eval() forward -> softmax",
               "  -> PredictionResult(label, confidence, confidences, needs_review)",
               "formatting.format_confidences()/format_summary(): PredictionResult -> UI shapes",
               "REVIEW_THRESHOLD = 0.60 (calibration-derived) drives needs_review",
               "examples.EXAMPLES: boundary + clear case sample posts"])
    # Left Annotation - deps
    box(20, y + 40, 230, 120, C_SIDE,
        title="Runtime deps", title_font=f_smallb,
        lines=["gradio >= 4.0",
               "torch >= 2.0",
               "transformers >= 4.40",
               "",
               "(requirements.txt)"],
        line_font=f_small, align_center=False)
    varrow(CX, y + 214, y + 214 + 40, "predict() + format_*() results")

    # ---- Gradio App (thin UI layer) --------------------------------------
    y = 952
    box(LX, y, BW, 130, C_APP,
        title="Gradio UI Layer",
        sub="app.py  (python app.py)",
        lines=["Blocks layout (Textbox + Button + Label) calls",
               "takemeter.inference.predict() then takemeter.formatting.format_*()",
               "no model/business logic lives in app.py itself"],
        title_font=f_stage, line_font=f_small)
    varrow(CX, y + 130, y + 130 + 36, "label + confidence + triage")

    # ---- User ------------------------------------------------------------
    y = 1118
    box(LX, y, BW, 92, C_USER,
        title="User  (browser)",
        lines=["pastes an r/stocks post  ->  Classify",
               "sees predicted class, confidence bar chart, and",
               "auto-classify vs. route-to-human triage hint"],
        title_font=f_stage, line_font=f_small)

    # ---- Outputs / Artifacts Panel --------------------------------------
    y = 1250
    box(20, y, W - 40, 190, C_OUT,
        title="Committed artifacts  (results/)  +  tests/", title_font=f_smallb,
        lines=[
            "evaluation_results.json  -  baseline 0.809 . fine-tuned 0.851 . improvement +0.043 . label_map",
            "confusion_matrix.png     -  fine-tuned model on the 47-example test set",
            "calibration_curve.png    -  reliability diagram, ECE = 0.287",
            "tests/  -  pytest suite over takemeter/ (fast, fake model) + real-model integration tests",
            "",
            "Docs: README.md (project write-up)  .  planning.md (taxonomy, label definitions, error analysis)",
        ],
        line_font=f_small, align_center=False)

    # ---- Footer ----------------------------------------------------------
    center(d, W / 2, 1500,
           "Flow: annotate data -> fine-tune DistilBERT in notebook (vs. Groq baseline) "
           "-> save checkpoint -> takemeter.predict()/format_*() -> serve via Gradio app to the user",
           f_small, SUB)

    img.save(out_path)
    print("wrote", out_path, img.size)


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    gen_model_diagram(os.path.join(here, "Model-Architecture.png"))
    gen_repo_diagram(os.path.join(here, "Repo-Architecture.png"))
