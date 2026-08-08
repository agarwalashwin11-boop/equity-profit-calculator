from flask import Flask, render_template_string, request

app = Flask(__name__)

# ---- Charges & Rates (from your sheet) ----
RATES = {
    "KOTAK_DELIVERY": {
        "brokerage_per_leg": 1e-3,
        "stt_buy": 1e-3,
        "stt_sell": 1e-3,
        "stamp_buy": 1.5e-4,
        "exchange_txn": 3.07e-5,
        "sebi": 1e-6,
        "gst": 0.18,
        "dp_charges": 0.0,
    },
    "ZERODHA_DELIVERY": {
        "brokerage_per_leg": 0.0,
        "stt_buy": 1e-3,
        "stt_sell": 1e-3,
        "stamp_buy": 1.5e-4,
        "exchange_txn": 3.07e-5,
        "sebi": 1e-6,
        "gst": 0.18,
        "dp_charges": 0.0,
    }
}

HTML = """
<!doctype html>
<title>Equity Profit Calculator</title>
<h2>Equity Trade – Net Profit Calculator</h2>
<form method="post">
  <label>Broker:</label>
  <select name="broker">
    <option value="KOTAK_DELIVERY">Kotak Delivery</option>
    <option value="ZERODHA_DELIVERY">Zerodha Delivery</option>
  </select><br><br>

  <label>Quantity:</label>
  <input type="number" name="qty" step="1" required><br><br>

  <label>Purchase Price:</label>
  <input type="number" name="buy_price" step="0.01" required><br><br>

  <label>Sale Price:</label>
  <input type="number" name="sell_price" step="0.01" required><br><br>

  <label>Interest Cost (₹):</label>
  <input type="number" name="interest" step="0.01" value="0"><br><br>

  <button type="submit">Calculate</button>
</form>

{% if result %}
<hr>
<h3>Result</h3>
<p>Purchase Value: ₹{{ result.purchase_value }}</p>
<p>Sale Value: ₹{{ result.sale_value }}</p>
<p>Gross P/L: ₹{{ result.gross_pl }}</p>
<p>Total Charges: ₹{{ result.total_charges }}</p>
<p>Interest Cost: ₹{{ result.interest_cost }}</p>
<p><b>Net P/L: ₹{{ result.net_pl }}</b></p>
<p>Net Return %: {{ result.net_return_pct }}%</p>
<p>Break-even Sale Price: ₹{{ result.break_even_price }}</p>
{% endif %}
"""

def calc_trade(broker_key, qty, buy_price, sell_price, interest_cost):
    r = RATES[broker_key]

    purchase_value = qty * buy_price
    sale_value = qty * sell_price
    gross_pl = sale_value - purchase_value

    # Brokerage
    buy_brokerage = purchase_value * r["brokerage_per_leg"]
    sell_brokerage = sale_value * r["brokerage_per_leg"]

    # STT
    stt_buy = purchase_value * r["stt_buy"]
    stt_sell = sale_value * r["stt_sell"]

    # Stamp duty (only on buy)
    stamp_duty = purchase_value * r["stamp_buy"]

    # Exchange + SEBI (both legs)
    exch_buy = purchase_value * r["exchange_txn"]
    exch_sell = sale_value * r["exchange_txn"]
    sebi_buy = purchase_value * r["sebi"]
    sebi_sell = sale_value * r["sebi"]

    # GST on brokerage + exchange + sebi
    gst_base = buy_brokerage + sell_brokerage + exch_buy + exch_sell + sebi_buy + sebi_sell
    gst = gst_base * r["gst"]

    # DP charges (delivery)
    dp = r["dp_charges"]

    total_charges = (
        buy_brokerage + sell_brokerage +
        stt_buy + stt_sell +
        stamp_duty +
        exch_buy + exch_sell +
        sebi_buy + sebi_sell +
        gst +
        dp
    )

    net_pl = gross_pl - total_charges - interest_cost
    net_return_pct = (net_pl / purchase_value * 100) if purchase_value != 0 else 0

    # Break-even sale price: sale price where net_pl = 0
    # Let S = break-even sale price:
    # Net P/L = (S*qty - purchase_value) - charges(S) - interest = 0
    # Approximate by ignoring STT_sell dependence on S for simplicity:
    break_even_price = (purchase_value + total_charges + interest_cost) / qty

    return {
        "purchase_value": round(purchase_value, 2),
        "sale_value": round(sale_value, 2),
        "gross_pl": round(gross_pl, 2),
        "total_charges": round(total_charges, 2),
        "interest_cost": round(interest_cost, 2),
        "net_pl": round(net_pl, 2),
        "net_return_pct": round(net_return_pct, 2),
        "break_even_price": round(break_even_price, 2),
    }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        broker = request.form.get("broker")
        qty = int(request.form.get("qty"))
        buy_price = float(request.form.get("buy_price"))
        sell_price = float(request.form.get("sell_price"))
        interest = float(request.form.get("interest") or 0)

        result = calc_trade(broker, qty, buy_price, sell_price, interest)

    return render_template_string(HTML, result=result)

if __name__ == "__main__":
    app.run(debug=True)
