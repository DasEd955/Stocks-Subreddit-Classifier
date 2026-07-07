"""examples.py - curated sample r/stocks posts shown in the Gradio interface.

The examples fall into two groups. The first four are, by the taxonomy,
correct but sit on a model decision boundary. The deployed checkpoint
disagrees with the human label, which is exactly the calibration weakness
documented in planning.md. The second four were tuned against the actual
checkpoint so its argmax matches the intended label. Predictions noted below
are from checkpoint-56 (the shipped model).
"""

EXAMPLES = [
    # BOUNDARY - intended Evidence_Based_Analysis; model predicts Interpretive_Opinion
    # (~0.54). The canonical Analysis/Opinion confusion: the valuation verdict ("looks
    # fairly valued") reads as a personal take to the model despite the cited metrics.
    "NVDA's data center revenue grew 427% YoY to $47.5B in FY2024. At a forward P/E of ~35x on consensus FY2025 EPS of $28, the stock looks fairly valued relative to the S&P tech median of 32x. It is not the screaming buy bulls are claiming.",
    # BOUNDARY - intended Interpretive_Opinion; model predicts Low_Quality_Misleading
    # (~0.49, with Opinion ~0.41 just behind). The confident macro call tips it toward
    # the manipulation class even though there is no hype or call to action.
    "I think the Fed is going to pivot earlier than expected. Inflation feels like it's under control and they don't want to cause unnecessary damage to the labor market.",
    # BOUNDARY - intended News_Information; model predicts News but weakly (~0.35, with
    # Opinion ~0.28 close behind). Bare earnings figures with no headline/source cue sit
    # near the News/Opinion line for this checkpoint.
    "Apple reported Q2 FY2025 revenue of $95.4B, up 5% YoY. Services revenue hit a new record at $26.6B. EPS of $1.65 beat consensus by $0.04.",
    # BOUNDARY - intended Low_Quality_Misleading; model predicts Low_Quality (~0.56).
    # The only original example whose argmax matches the human label, though still under
    # the 0.60 review threshold.
    "GME to $500 by end of month. Shorts are TRAPPED. Anyone selling before $300 is leaving money on the table. This is the squeeze of the decade.",
    # CLEAR - Evidence_Based_Analysis (model predicts EBA ~0.48). EBA is the hardest
    # class for this checkpoint: it keys on length + a thesis that draws inferences from
    # data ("my thesis", "tells you", "the implication is"), plus the "Company Analysis"
    # tag seen in real EBA posts. Short data dumps get read as News or Opinion instead.
    "My thesis: Microsoft is the best positioned name in the cloud cycle, and the segment data backs it up rather than the other way around. Company Analysis Azure grew 33% YoY last quarter against AWS at 17% and Google Cloud at 28%, the third consecutive quarter it has outpaced both rivals, which tells you this is share gain, not just a rising tide. Commercial remaining performance obligations hit $315B, up 34% YoY; that contracted backlog means the growth is already booked, not hoped for. Operating margin held at 45% even as capex ramped to $20B, so I read this as durable compounding rather than growth bought with eroding profitability. The implication is that Microsoft is capturing a disproportionate share of new enterprise AI spend, and that is what justifies the ~35x forward P/E premium over the rest of big tech - you are paying up for the highest-quality compounder in the group, and on these numbers I think that premium is earned.",
    # CLEAR - Interpretive_Opinion (model predicts Opinion ~0.50). Purely subjective
    # ("feels", "gut sense", "vibe"), zero data, no manipulative call to action. So, it
    # stays clear of both Analysis and Low Quality.
    "Honestly I just don't trust this rally. Everything feels stretched to me and I've got a gut sense we're due for a real pullback before year end. Nothing concrete, just the vibe of the market right now. I'm staying mostly in cash until it feels healthier.",
    # CLEAR - News_Information (model predicts News ~0.51). Phrased in the headline +
    # category tag + URL structure the model learned for real news posts; without that
    # surface form (e.g. a bare "Breaking: ..." sentence) it mislabels facts as opinion.
    "Fed holds rates steady at 4.25%-4.50%, in line with expectations Broad market news The Federal Reserve held its benchmark interest rate at 4.25% to 4.50% at the conclusion of today's FOMC meeting. The central bank said it will wait for more data before deciding on any rate cuts. https://www.cnbc.com/fomc-decision.html",
    # CLEAR - Low_Quality_Misleading (model predicts Low_Quality ~0.50). Conspiracy
    # framing + unsupported certainty ("guaranteed 10-bagger") + inflammatory call to
    # action. Multiple planning.md criteria at once.
    "PLTR is about to explode and the suits on Wall Street are praying you stay asleep. Insiders are quietly loading the boat while the financial media tells you to sell. This is a guaranteed 10 bagger. Mortgage the house if you have to. Anyone who fades this will be crying in a year.",
]
