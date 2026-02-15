from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd

app = Flask(__name__)
app.secret_key = "change-this-in-production"


def compute_ratios(row):
    """
    Expects columns (lowercase names):
      current_assets, current_liabilities, total_debt,
      ebit, interest_expense, revenue_current, revenue_prior, total_assets
    """
    ratios = {}

    ca = row.get("current_assets")
    cl = row.get("current_liabilities")
    debt = row.get("total_debt")
    ebit = row.get("ebit")
    interest = row.get("interest_expense")
    rev_curr = row.get("revenue_current")
    rev_prior = row.get("revenue_prior")
    assets = row.get("total_assets")

    # Basic checks
    def safe_div(n, d):
        try:
            if d is None or d == 0:
                return None
            return float(n) / float(d)
        except Exception:
            return None

    ratios["current_ratio"] = safe_div(ca, cl)
    ratios["leverage_ratio"] = safe_div(debt, assets)
    ratios["interest_coverage"] = safe_div(ebit, (interest if interest and interest != 0 else None))
    ratios["revenue_growth"] = safe_div((rev_curr - rev_prior), rev_prior) if rev_prior not in (None, 0) else None
    ratios["return_on_assets"] = safe_div(ebit, assets)

    return ratios


def score_ratios(r):
    """
    Very simple heuristic scoring.
    Higher is better; approximate tiers 1–4.
    """
    score = 0
    details = []

    # Current ratio
    cr = r.get("current_ratio")
    if cr is not None:
        if cr >= 2:
            score += 3
            details.append("Strong liquidity (current ratio ≥ 2).")
        elif cr >= 1:
            score += 2
            details.append("Adequate liquidity (current ratio between 1 and 2).")
        else:
            score -= 2
            details.append("Weak liquidity (current ratio < 1).")

    # Leverage
    lev = r.get("leverage_ratio")
    if lev is not None:
        if lev <= 0.4:
            score += 3
            details.append("Conservative leverage (debt/assets ≤ 40%).")
        elif lev <= 0.7:
            score += 1
            details.append("Moderate leverage (debt/assets 40–70%).")
        else:
            score -= 3
            details.append("High leverage (debt/assets > 70%).")

    # Interest coverage
    ic = r.get("interest_coverage")
    if ic is not None:
        if ic >= 5:
            score += 3
            details.append("Very strong interest coverage (≥ 5x).")
        elif ic >= 2:
            score += 1
            details.append("Comfortable interest coverage (2–5x).")
        else:
            score -= 3
            details.append("Weak interest coverage (< 2x).")

    # Revenue growth
    g = r.get("revenue_growth")
    if g is not None:
        if g >= 0.1:
            score += 2
            details.append("Healthy top-line growth (≥ 10%).")
        elif g >= 0:
            score += 0
            details.append("Flat to modest growth.")
        else:
            score -= 2
            details.append("Negative revenue growth.")

    # ROA
    roa = r.get("return_on_assets")
    if roa is not None:
        if roa >= 0.08:
            score += 2
            details.append("Attractive returns on assets (≥ 8%).")
        elif roa >= 0.03:
            score += 1
            details.append("Acceptable returns on assets (3–8%).")
        else:
            score -= 1
            details.append("Low returns on assets (< 3%).")

    # Map numerical score to tier
    if score >= 7:
        tier = "Tier 1 – Strong"
        outlook = "Strong, stable credit profile."
    elif score >= 3:
        tier = "Tier 2 – Stable"
        outlook = "Generally sound credit profile with manageable risks."
    elif score >= -1:
        tier = "Tier 3 – Negative outlook"
        outlook = "Elevated risk; trends require close monitoring."
    else:
        tier = "Tier 4 – High-risk"
        outlook = "Weak credit profile; higher default risk."

    return score, tier, outlook, details


def generate_memo(counterparty, ratios, score, tier, outlook, details):
    lines = []
    lines.append(f"Counterparty: {counterparty}")
    lines.append(f"Overall health score: {score} ({tier})")
    lines.append("")
    lines.append("Key quantitative indicators:")
    if ratios.get("current_ratio") is not None:
        lines.append(f"- Current ratio: {ratios['current_ratio']:.2f}")
    if ratios.get("leverage_ratio") is not None:
        lines.append(f"- Leverage (Debt / Assets): {ratios['leverage_ratio']:.2f}")
    if ratios.get("interest_coverage") is not None:
        lines.append(f"- Interest coverage (EBIT / Interest): {ratios['interest_coverage']:.2f}")
    if ratios.get("revenue_growth") is not None:
        lines.append(f"- Revenue growth YoY: {ratios['revenue_growth']*100:.1f}%")
    if ratios.get("return_on_assets") is not None:
        lines.append(f"- Return on assets (EBIT / Assets): {ratios['return_on_assets']*100:.1f}%")

    lines.append("")
    lines.append("Analyst commentary:")
    for d in details:
        lines.append(f"- {d}")

    lines.append("")
    lines.append(f"Overall assessment: {outlook}")
    lines.append("Recommendation: Use this assessment as an input into the broader counterparty risk framework; not a standalone approval tool.")

    return "\n".join(lines)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            flash("Please upload a financials file (CSV or Excel).", "danger")
            return redirect(url_for("index"))

        try:
            if file.filename.lower().endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # Normalize column names
            df.columns = [c.strip().lower() for c in df.columns]

            required = [
                "counterparty",
                "current_assets",
                "current_liabilities",
                "total_debt",
                "ebit",
                "interest_expense",
                "revenue_current",
                "revenue_prior",
                "total_assets",
            ]
            missing = [c for c in required if c not in df.columns]
            if missing:
                raise ValueError(
                    "Missing required columns: " + ", ".join(missing)
                )

            # For demo, just process first row / counterparty
            row = df.iloc[0].to_dict()
            counterparty = row.get("counterparty", "Unknown")

            ratios = compute_ratios(row)
            score, tier, outlook, details = score_ratios(ratios)
            memo = generate_memo(counterparty, ratios, score, tier, outlook, details)

            # For display, round ratios
            display_ratios = {}
            for k, v in ratios.items():
                if v is None:
                    display_ratios[k] = None
                else:
                    display_ratios[k] = round(v, 3)

            return render_template(
                "index.html",
                results=True,
                counterparty=counterparty,
                ratios=display_ratios,
                score=score,
                tier=tier,
                outlook=outlook,
                details=details,
                memo=memo,
            )

        except Exception as e:
            flash(f"Error processing file: {e}", "danger")
            return redirect(url_for("index"))

    return render_template("index.html", results=False)


if __name__ == "__main__":
    app.run(debug=True)
