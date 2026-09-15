import streamlit as st
import time
from tradingview_ta import TA_Handler, Interval

# Mobile screen size ke mutabiq page set karna
st.set_page_config(page_title="Quotex Signal Bot", page_icon="🎯", layout="centered")

# Custom CSS design (Gol daira aur animations ke liye)
st.markdown("""
    <style>
    .main { text-align: center; }
    .stButton>button {
        border-radius: 50% !important;
        width: 150px !important;
        height: 150px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        color: white !important;
        background: linear-gradient(145deg, #1e293b, #0f172a) !important;
        border: 4px solid #38bdf8 !important;
        box-shadow: 0 0 15px #38bdf8 !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 25px #38bdf8 !important;
    }
    </style>
""", unsafe_allowed_html=True)

st.title("🎯 Quotex Smart Bot")
st.write("Apna asset select karein aur gol daire par click karein.")

# 1. User Inputs (Dropdown Boxes)
col1, col2 = st.columns(2)
with col1:
    asset = st.selectbox("Country/Asset Select Karein", ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD"])
with col2:
    timeframe = st.selectbox("Timeframe Select Karein", ["1m", "5m", "15m"])

# Timeframe ko TradingView ke mutabiq set karna
if timeframe == "1m": tf = Interval.INTERVAL_1_MINUTE
elif timeframe == "5m": tf = Interval.INTERVAL_5_MINUTES
else: tf = Interval.INTERVAL_15_MINUTES

# Daily trade limit check karne ke liye session storage
if 'trade_count' not in st.session_state:
    st.session_state.trade_count = 0

st.subheader(s=f"Aaj ki Trades: {st.session_state.trade_count} / 2")

# 2. Gol Daira (Button) Aur Signal Logic
if st.session_state.trade_count >= 2:
    st.error("⚠️ Aapki aaj ke 2 signals ki limit poori ho chuki hai! Kal dobara aayin.")
else:
    # Gol Daira Button
    if st.button("CLICK\nFOR\nSIGNAL"):
        # Ghoomne ya loading ka ehsas dilane ke liye spinner animation
        with st.spinner("Market ko scan kiya ja raha hai..."):
            time.sleep(2) # 2 seconds ka wait taake real feel aaye
            
            try:
                # TradingView se live data uthana
                handler = TA_Handler(
                    symbol=asset,
                    exchange="FX_IDC" if "USD" in asset and "BTC" not in asset else "BINANCE",
                    screener="forex" if "USD" in asset and "BTC" not in asset else "crypto",
                    interval=tf
                )
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                ema200 = analysis.indicators["EMA200"]
                close_price = analysis.indicators["close"]
                
                # Signal Faisla (EMA 200 aur RSI Strategy)
                if close_price > ema200 and rsi <= 35:
                    st.markdown("<h1 style='text-align: center; color: #22c55e;'>🟢 UP (CALL)</h1>", unsafe_allow_html=True)
                    st.success(f"Mazboot Signal! Market up trend mein hai aur sasti hai. (RSI: {round(rsi,1)})")
                    st.session_state.trade_count += 1
                    st.balloons() # Kamyabi ki animation
                    
                elif close_price < ema200 and rsi >= 65:
                    st.markdown("<h1 style='text-align: center; color: #ef4444;'>🔴 DOWN (PUT)</h1>", unsafe_allow_html=True)
                    st.error(f"Mazboot Signal! Market down trend mein hai aur mehangi hai. (RSI: {round(rsi,1)})")
                    st.session_state.trade_count += 1
                    
                else:
                    st.markdown("<h1 style='text-align: center; color: #94a3b8;'>⚪ WAIT</h1>", unsafe_allow_html=True)
                    st.warning("Abhi market darmiyan mein hai. Sahi moka nahi hai, thodi der baad dobara click karein.")
                    
            except Exception as e:
                st.error("Data nikalne mein masla hua. Check karein ke internet chal raha hai.")
