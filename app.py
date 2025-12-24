import streamlit as st
import pandas as pd

# --- 페이지 설정 ---
st.set_page_config(page_title="Provident Trading Master", layout="wide")
st.title("🛡️ Provident Principle Futures: 엑셀 기반 매매 계산기")

# --- 사이드바 설정 ---
st.sidebar.header("📊 Global Risk Setting")
seed = st.sidebar.number_input("Total Seed ($)", value=5000.0) #
risk_pct = st.sidebar.slider("Risk per Trade (%)", 0.1, 5.0, 2.0) / 100 #
one_r = seed * risk_pct #
st.sidebar.info(f"**현재 1R 리스크: ${one_r:,.1f}**")

# --- 탭 구성 ---
tab1, tab2 = st.tabs(["🎯 RR & Position Calculator", "💀 Liquidation Calculator"])

# --- Tab 1: RR Calculator (엑셀 시트 1 로직) ---
with tab1:
    st.header("1. Risk & Reward / Position Sizing")
    col1, col2 = st.columns(2)
    
    with col1:
        side = st.selectbox("거래 방향", ["Long", "Short"])
        entry_p = st.number_input("진입가 (Entry Price)", value=100.0)
        stop_p = st.number_input("손절가 (Stop Loss)", value=99.0)
        target_rr = st.number_input("목표 손익비 (Target RR)", value=1.5)
        leverage = st.number_input("레버리지 (Leverage x)", value=10)

    price_diff = abs(entry_p - stop_p)
    if price_diff > 0:
        pos_size_units = one_r / price_diff
        pos_value = pos_size_units * entry_p
        required_margin = pos_value / leverage
        tp_p = entry_p + (price_diff * target_rr) if side == "Long" else entry_p - (price_diff * target_rr)
        
        with col2:
            st.success(f"**권장 포지션 가치: ${pos_value:,.2f}**")
            st.info(f"**진입 수량 (Qty): {pos_size_units:,.4f} Units**")
            st.warning(f"**필요 증거금 (Margin): ${required_margin:,.2f}**")
            st.markdown(f"**🎯 목표 익절가: ${tp_p:,.4f}**")

# --- Tab 2: 청산가 계산기 (엑셀 시트 2 로직) ---
with tab2:
    st.header("2. Average Price & Liquidation (5-Step)") #
    col_a, col_b = st.columns(2)
    with col_a:
        entries = []
        for i in range(1, 6):
            c1, c2 = st.columns(2)
            p = c1.number_input(f"{i}차 진입가", value=0.0, key=f"lp{i}")
            q = c2.number_input(f"{i}차 수량(Qty)", value=0.0, key=f"lq{i}")
            if p > 0 and q > 0: entries.append((p, q))
            
    if entries:
        df_l = pd.DataFrame(entries, columns=['price', 'qty'])
        total_q = df_l['qty'].sum()
        avg_p = (df_l['price'] * df_l['qty']).sum() / total_q
        
        mmr = 0.005 #
        if side == "Long":
            liq_p = avg_p * (1 - (1/leverage) + mmr)
        else:
            liq_p = avg_p * (1 + (1/leverage) - mmr)
            
        with col_b:
            st.metric("최종 평단가", f"${avg_p:,.4f}")
            st.error(f"예상 청산가: ${liq_p:,.4f}")
