import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Provident Trading Calc", layout="wide")
st.title("🧮 Futures Position & Liquidation Calculator")

# --- 2. 사이드바 리스크 설정 ---
st.sidebar.header("⚙️ Risk Setting")
total_seed = st.sidebar.number_input("시작 자산 ($)", value=5000.0) #
one_r = total_seed * 0.02 # 2% 리스크 ($100)

# --- 3. 탭 구성 (계산기 탭 추가) ---
tab1, tab2, tab3 = st.tabs(["🔢 Position & Liq Calc", "📊 MEXC Journal", "🚀 2030 Roadmap"])

with tab1:
    st.header("📉 선물 진입 및 청산가 상세 계산")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ 평단가(Avg Price) 계산")
        st.caption("5분할 진입 시 각 차수별 가격과 물량을 입력하세요.") #
        
        # 입력 데이터 구조
        entry_data = []
        for i in range(1, 6):
            c_a, c_b = st.columns(2)
            p = c_a.number_input(f"{i}차 진입가", value=0.0, key=f"p{i}")
            q = c_b.number_input(f"{i}차 수량(Qty)", value=0.0, key=f"q{i}")
            if p > 0 and q > 0:
                entry_data.append({'price': p, 'qty': q})
        
        if entry_data:
            df_entry = pd.DataFrame(entry_data)
            # 평단가 공식: (가격 * 수량)의 합 / 총 수량
            total_qty = df_entry['qty'].sum()
            avg_price = (df_entry['price'] * df_entry['qty']).sum() / total_qty
            st.info(f"✅ **최종 평단가: ${avg_price:,.4f}**")
            st.info(f"📦 **총 포지션 규모: {total_qty:,.2f} Units**")

    with col2:
        st.subheader("2️⃣ 청산가(Liq Price) 및 레버리지")
        leverage = st.slider("사용 레버리지 (x)", 1, 100, 10) #
        side = st.radio("포지션 방향", ["Long", "Short"])
        
        if entry_data:
            # 단순화된 격리(Isolated) 청산가 계산 공식
            # Long: Entry * (1 - 1/Lev + MaintenanceMargin)
            # Short: Entry * (1 + 1/Lev - MaintenanceMargin)
            mmr = 0.005 # 유지 증거금율 0.5% 가정
            
            if side == "Long":
                liq_price = avg_price * (1 - (1/leverage) + mmr)
            else:
                liq_price = avg_price * (1 + (1/leverage) - mmr)
                
            st.error(f"🚨 **예상 청산가 ({side}): ${liq_price:,.4f}**")
            
            # 리스크 경고
            stop_loss_1r = avg_price * 0.99 if side == "Long" else avg_price * 1.01
            st.warning(f"⚠️ 사용자 원칙 손절가 (-1%): ${stop_loss_1r:,.4f}") #
            
            if (side == "Long" and liq_price > stop_loss_1r) or (
