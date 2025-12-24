import streamlit as st
import pandas as pd
import plotly.express as px

# --- 페이지 설정 ---
st.set_page_config(page_title="Provident Risk Master", layout="wide")
st.title("🏆 Provident Principle Futures: Millionaire 2030")

# --- 사이드바: 고정 리스크 설정 (사용자 원칙 반영) ---
st.sidebar.header("🛡️ Risk Management")
seed = st.sidebar.number_input("Total Seed ($)", value=5000.0) #
risk_pct = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 2.0) / 100 #
one_r = seed * risk_pct # 1R 리스크 금액 ($100)

st.sidebar.info(f"**Your 1R Risk Amount: ${one_r:,.1f}**")

# --- 탭 구성: 업로드한 엑셀 기반 ---
tab1, tab2, tab3 = st.tabs(["📊 RR Calculator", "💀 Liquidation Calc", "🚀 Goal Tracker"])

# --- Tab 1: RR Calculator (엑셀 시트 1 로직) ---
with tab1:
    st.header("🎯 Position Size & RR Calculator")
    c1, c2 = st.columns(2)
    
    with c1:
        entry_p = st.number_input("Entry Price", value=100.0)
        stop_p = st.number_input("Stop Loss Price", value=99.0)
        target_rr = st.slider("Target RR (1:X)", 1.0, 10.0, 1.5)
    
    # 계산 로직: 엑셀 수식 반영
    price_diff = abs(entry_p - stop_p)
    if price_diff > 0:
        # 포지션 규모 = 리스크 금액 / (진입가 - 손절가)
        pos_size_units = one_r / price_diff
        pos_size_value = pos_size_units * entry_p
        take_profit_p = entry_p + (entry_p - stop_p) * target_rr if entry_p > stop_p else entry_p - (stop_p - entry_p) * target_rr
        
        with c2:
            st.success(f"**Recommended Position:** ${pos_size_value:,.2f}")
            st.info(f"**Quantity:** {pos_size_units:,.4f} Units")
            st.warning(f"**Take Profit Price:** ${take_profit_p:,.4f}")
            
            # 예상 수익/손실
            st.write(f"💰 Potential Profit: ${one_r * target_rr:,.1f}")
            st.write(f"📉 Potential Loss: -${one_r:,.1f}")

# --- Tab 2: 청산가 계산기 (엑셀 시트 2 로직) ---
with tab2:
    st.header("💀 Liquidation & Avg Price")
    st.caption("5분할 진입 시 평단가와 청산가를 계산합니다.") #
    
    col_l, col_r = st.columns(2)
    with col_l:
        lev = st.number_input("Leverage (x)", value=10)
        side = st.selectbox("Direction", ["Long", "Short"])
        
        # 5분할 입력 섹션
        entries = []
        for i in range(1, 6):
            cc1, cc2 = st.columns(2)
            p = cc1.number_input(f"Price {i}", value=0.0, key=f"p{i}")
            q = cc2.number_input(f"Qty {i}", value=0.0, key=f"q{i}")
            if p > 0 and q > 0: entries.append((p, q))
            
    if entries:
        df_entries = pd.DataFrame(entries, columns=['price', 'qty'])
        total_q = df_entries['qty'].sum()
        avg_p = (df_entries['price'] * df_entries['qty']).sum() / total_q
        
        # 청산가 계산 공식 (엑셀 로직 반영)
        mmr = 0.005 # Maintenance Margin 0.5%
        if side == "Long":
            liq_p = avg_p * (1 - (1/lev) + mmr)
        else:
            liq_p = avg_p * (1 + (1/lev) - mmr)
            
        with col_r:
            st.metric("Average Entry Price", f"${avg_p:,.4f}")
            st.error(f"Estimated Liquidation: ${liq_p:,.4f}")
            
            # 손절가와 청산가 비교 경고
            if side == "Long" and liq_p > (avg_p * 0.99):
                st.error("⚠️ 경고: 청산가가 1% 손절가보다 위에 있습니다! 레버리지를 낮추세요.")

# --- Tab 3: Goal Tracker ($8,000 목표) ---
with tab3:
    st.header("🏁 Monthly Goal: $8,000") #
    current_profit = st.number_input("이번 달 현재 수익 ($)", value=0.0)
    progress = min(current_profit / 8000, 1.0)
    st.progress(progress)
    st.write(f"목표 달성률: {progress*100:.1f}% (${current_profit} / $8,000)")
