"""app.py - Streamlit page for signal_engine.py
Run:  streamlit run app.py   (keep app.py, signal_engine.py and the CSV in the same folder)
"""
import os
import pandas as pd
import streamlit as st
import altair as alt

import signal_engine as crypto

st.set_page_config(page_title="Crypto signal", page_icon="📈")

# ------------------------------------------------------------ title + sidebar
st.title("Crypto signal: Decision Tree / Random Forest / XGBoost")
st.caption("Supervised learning on free Binance data. Paper money only.")

st.sidebar.header("Settings")
sec = st.sidebar.slider("Bar size (seconds)", 1, 10, 1)
ahead = st.sidebar.slider("Predict ahead (bars)", 5, 60, 10)
tail = st.sidebar.slider("BUY / SELL share", 0.10, 0.40, 0.25, 0.05)
cash = st.sidebar.number_input("Paper cash (USDT)", 100.0, 1_000_000.0, 1000.0)
risk = st.sidebar.slider("Risk per trade (%)", 1, 50, 10)


# ------------------------------------------------------------ load data
@st.cache_data(show_spinner="Loading trades...")
def get_bars(file_bytes, name, sec):
    import io
    f = io.BytesIO(file_bytes)
    trades = crypto.load_trades(f, nrows=500000)
    return crypto.features(crypto.to_bars(trades, sec)).tail(30000).reset_index(drop=True)


up = st.file_uploader("Upload Binance trades CSV (optional)", type="csv")
if up is not None:
    data, name = up.getvalue(), up.name
elif os.path.exists(crypto.DATA_FILE):
    with open(crypto.DATA_FILE, "rb") as fh:
        data, name = fh.read(), crypto.DATA_FILE
else:
    st.info("Upload a trades CSV to begin.")
    st.stop()

bars = get_bars(data, name, sec)
st.subheader(f"Loaded {len(bars):,} bars")

plot = bars[["timestamp", "price"]].iloc[::6]            # fewer points = faster chart
st.altair_chart(
    alt.Chart(plot).mark_line(color="#ff4b4b").encode(
        x=alt.X("timestamp:T", title=None),
        y=alt.Y("price:Q", scale=alt.Scale(zero=False), title="price (USDT)"),
    ).properties(width="container", height=300)
)

# ------------------------------------------------------------ train
if "models" not in st.session_state:
    st.session_state.models = None
    st.session_state.results = None

if st.button("Train models"):
    models, rows = crypto.get_models(), []
    with st.spinner("Training..."):
        for mname, m in models.items():
            acc, base = crypto.train(bars, m, ahead=ahead, tail=tail)
            rows.append({"Model": mname, "Accuracy": round(acc, 3), "Baseline": round(base, 3)})
    st.session_state.models = models
    st.session_state.results = pd.DataFrame(rows)

if st.session_state.results is not None:
    st.table(st.session_state.results.set_index("Model"))
    st.caption("Accuracy should beat Baseline, otherwise the model learned nothing useful.")

    # -------------------------------------------------------- live signal
    choice = st.selectbox("Model for live signal", list(st.session_state.models))
    if st.button("Get live signal"):
        try:
            sig, conf, price = crypto.live_signal(st.session_state.models[choice], sec)
            st.session_state.live = (sig, conf, price)
        except Exception as e:
            st.error(f"Could not get live data: {e}")

    if "live" in st.session_state:
        sig, conf, price = st.session_state.live
        color = {"BUY": "#16a34a", "SELL": "#dc2626", "HOLD": "#6b7280"}[sig]
        st.caption("Signal")
        st.markdown(
            f"<h1 style='color:{color};margin:0'>{sig}</h1>"
            f"<p style='color:{color}'>confidence {conf:.0%} | price {price:,.2f}</p>",
            unsafe_allow_html=True,
        )
        st.info(crypto.paper_plan(sig, price, cash, risk))
else:
    st.caption("Click **Train models** to see accuracy and get a live signal.")