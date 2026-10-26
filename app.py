from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lot Size Calculator</title>
  <style>
    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      font-family: "Segoe UI", Roboto, Arial, sans-serif;
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      color: #e2e8f0;
    }

    .wrap {
      width: 100%;
      max-width: 880px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    .panel {
      background: #111827;
      border: 1px solid #263244;
      border-radius: 18px;
      padding: 32px 28px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
    }

    h1 { margin: 0 0 4px; font-size: 24px; color: #fff; }
    .subtitle { margin: 0 0 26px; font-size: 14px; color: #94a3b8; }

    label {
      display: block;
      margin-bottom: 6px;
      font-size: 13px;
      font-weight: 600;
      color: #cbd5e1;
    }
    .hint { font-weight: 400; color: #64748b; }

    input {
      width: 100%;
      padding: 13px 14px;
      margin-bottom: 18px;
      font-size: 16px;
      color: #fff;
      background: #0b1220;
      border: 1px solid #2b3a52;
      border-radius: 10px;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    input:focus {
      border-color: #22c55e;
      box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2);
    }

    button {
      width: 100%;
      padding: 14px;
      font-size: 16px;
      font-weight: 700;
      color: #04130a;
      background: linear-gradient(135deg, #22c55e, #16a34a);
      border: none;
      border-radius: 10px;
      cursor: pointer;
      transition: transform 0.1s, opacity 0.2s;
    }
    button:hover { opacity: 0.92; }
    button:active { transform: scale(0.98); }

    /* Right-hand result panel */
    .result-panel {
      display: flex;
      flex-direction: column;
      justify-content: center;
      text-align: center;
    }

    .result-label {
      font-size: 13px;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 1.5px;
    }

    .result-value {
      margin: 10px 0 4px;
      font-size: 72px;
      font-weight: 800;
      line-height: 1;
      color: #22c55e;
    }
    .result-value.empty { color: #334155; }

    .result-unit { font-size: 15px; color: #94a3b8; }

    .summary {
      margin-top: 28px;
      padding-top: 20px;
      border-top: 1px solid #263244;
      text-align: left;
      font-size: 14px;
      color: #94a3b8;
    }
    .summary div {
      display: flex;
      justify-content: space-between;
      padding: 6px 0;
    }
    .summary span:last-child { color: #e2e8f0; font-weight: 600; }

    .placeholder {
      margin-top: 24px;
      font-size: 14px;
      color: #64748b;
    }

    .error {
      margin-top: 24px;
      padding: 14px;
      font-size: 14px;
      color: #fecaca;
      background: rgba(239, 68, 68, 0.12);
      border: 1px solid rgba(239, 68, 68, 0.4);
      border-radius: 10px;
    }

    .formula {
      margin-top: 24px;
      font-size: 12px;
      color: #64748b;
    }

    /* Phones: stack the panels */
    @media (max-width: 720px) {
      .wrap { grid-template-columns: 1fr; }
      .result-value { font-size: 56px; }
    }
  </style>
</head>
<body>
  <div class="wrap">

    <!-- LEFT: inputs -->
    <div class="panel">
      <h1>Lot Size Calculator</h1>
      <p class="subtitle">Work out the right position size before you trade.</p>

      <form method="post">
        <label>Stop loss <span class="hint">(pips)</span></label>
        <input type="number" step="any" name="pips" value="{{ pips }}" placeholder="e.g. 12" required>

        <label>Amount you are risking <span class="hint">(account currency)</span></label>
        <input type="number" step="any" name="risk" value="{{ risk }}" placeholder="e.g. 470" required>

        <label>Pip value <span class="hint">(per 1 lot)</span></label>
        <input type="number" step="any" name="pip_value" value="{{ pip_value }}" placeholder="e.g. 50" required>

        <button type="submit">Calculate lot size</button>
      </form>
    </div>

    <!-- RIGHT: result -->
    <div class="panel result-panel">
      <div class="result-label">Lot size to use</div>

      {% if result %}
        <div class="result-value">{{ result }}</div>
        <div class="result-unit">lots</div>

        <div class="summary">
          <div><span>Stop loss</span><span>{{ pips }} pips</span></div>
          <div><span>Risking</span><span>{{ risk }}</span></div>
          <div><span>Pip value</span><span>{{ pip_value }} per lot</span></div>
        </div>
      {% else %}
        <div class="result-value empty">0.00</div>
        <div class="result-unit">lots</div>
        <div class="placeholder">Enter your numbers and press Calculate.</div>
      {% endif %}

      {% if error %}
        <div class="error">{{ error }}</div>
      {% endif %}

      <div class="formula">lot size = risk &divide; (pips &times; pip value)</div>
    </div>

  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    pips = ""
    risk = ""
    pip_value = ""
    result = None
    error = None

    if request.method == "POST":
        pips = request.form["pips"]
        risk = request.form["risk"]
        pip_value = request.form["pip_value"]

        try:
            lot = float(risk) / (float(pips) * float(pip_value))
            result = f"{lot:.2f}"
        except ZeroDivisionError:
            error = "Pips and pip value cannot be zero."
        except ValueError:
            error = "Please enter numbers only."

    return render_template_string(
        PAGE, pips=pips, risk=risk, pip_value=pip_value,
        result=result, error=error
    )

app.run(host="127.0.0.1", port=5000)