import streamlit as st

st.title("Equity Profit Calculator - Maharashtra")

# --- Inputs (Yellow cells) ---
broker = st.selectbox("Broker", ["Kotak", "Zerodha"])
trade_type = st.selectbox("Trade Type", ["Delivery", "Intraday"])
quantity = st.number_input("Quantity", min_value=1, value=100)
purchase_price = st.number_input("Purchase Price", min_value=0.0, value=1000.0)
sale_price = st.number_input("Sale Price", min_value=0.0, value=0.0)

# --- Calculations (Green cells) ---
purchase_value = quantity * purchase_price
sale_value = quantity * sale_price
gross_profit = sale_value - purchase_value

# --- Charges & Rates ---
if broker == "Kotak" and trade_type == "Delivery":
    brokerage_rate = 0.001
    stt_buy = 0.001
    stt_sell = 0.001
    stamp_duty = 0.00015
elif broker == "Kotak" and trade_type == "Intraday":
    brokerage_rate = 0.0001
    stt_buy = 0
    stt_sell = 0.00025
    stamp_duty = 0.00003
elif broker == "Zerodha" and trade_type == "Delivery":
    brokerage_rate = 0.0
    stt_buy = 0.001
    stt_sell = 0.001
    stamp_duty = 0.00015
else:  # Zerodha Intraday
    brokerage_rate = 0.0001
    stt_buy = 0
    stt_sell = 0.00025
    stamp_duty = 0.00003

exchange_txn = 0.0000307
sebi_charge = 0.000001
gst_rate = 0.18

# --- Charges ---
buy_brokerage = brokerage_rate * purchase_value
sell_brokerage = brokerage_rate * sale_value
stt_buy_val = stt_buy * purchase_value
stt_sell_val = stt_sell * sale_value
stamp_duty_val = stamp_duty * purchase_value
exchange_val = exchange_txn * (purchase_value + sale_value)
sebi_val = sebi_charge * (purchase_value + sale_value)
gst_val = gst_rate * (buy_brokerage + sell_brokerage + exchange_val)

total_charges = (
    buy_brokerage + sell_brokerage +
    stt_buy_val + stt_sell_val +
    stamp_duty_val + exchange_val +
    sebi_val + gst_val
)

net_profit = gross_profit - total_charges
net_return_pct = (net_profit / purchase_value * 100) if purchase_value > 0 else 0
break_even_sale_price = (purchase_value + total_charges) / quantity

# --- Outputs (Green cells) ---
st.write("### Results")
st.write(f"Purchase Value: ₹{purchase_value:.2f}")
st.write(f"Sale Value: ₹{sale_value:.2f}")
st.write(f"Gross Profit/Loss: ₹{gross_profit:.2f}")
st.write(f"Total Charges: ₹{total_charges:.2f}")
st.write(f"Net Profit/Loss: ₹{net_profit:.2f}")
st.write(f"Net Return %: {net_return_pct:.2f}%")
st.write(f"Break-even Sale Price: ₹{break_even_sale_price:.2f}")
