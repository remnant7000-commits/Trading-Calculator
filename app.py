import streamlit as st
import pandas as pd

# 페이지 설정 (제목 및 아이콘)
st.set_page_config(page_title="Futures Trading Calculator", page_icon="📈")

# 스타일링 (모바일 가독성 향상)
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .result-box { padding: 15px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("📈 선물 트레이딩 통합 계산기")
st.caption("컴퓨터 & 모바일 호환 (BTC, ETH, SOL 등 공통)")

# 탭 구분 (RR 계산기 / 청산가 계산기)
tab1, tab2 = st.tabs(["🎯 리스크/RR 계산기", "☠️ 청산가 계산기"])

# --- 탭 1: 리스크/RR 계산기 ---
with tab1:
    st.header("리스크 관리 & RR 설정")

    # 1. 입력 섹션
    col1, col2 = st.columns(2)
    with col1:
        direction = st.radio("포지션 방향", ["LONG", "SHORT"], index=0, key="rr_dir")
        entry_price = st.number_input("진입가 (Entry Price)", value=88000.0, step=1.0, format="%.2f")
    with col2:
        position_size = st.number_input("포지션 규모 (USD)", value=20000.0, step=100.0)
        risk_amount = st.number_input("리스크 감수 금액 (USD)", value=30.0, step=1.0)

    # 2. 계산 로직
    if position_size > 0 and entry_price > 0:
        # 변동폭 계산 (Risk Amount / Position Size)
        risk_ratio = risk_amount / position_size
        price_move_1r = entry_price * risk_ratio
        
        # 손절가(SL) 계산
        if direction == "LONG":
            stop_loss = entry_price - price_move_1r
        else:
            stop_loss = entry_price + price_move_1r
            
        # 3. 결과 표시
        st.markdown("---")
        st.markdown(f"#### 📊 분석 결과")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("가격 이동폭 (1R)", f"{price_move_1r:.2f}")
        c2.metric("손절가 (Stop Loss)", f"{stop_loss:.2f}")
        c3.metric("리스크 비율", f"{risk_ratio*100:.2f}%")

        # 4. RR 배수 테이블 생성
        st.subheader("RR 배수별 익절가 (Take Profit)")
        
        rr_data = []
        for i in range(1, 11): # 1~10배
            if direction == "LONG":
                tp_price = entry_price + (price_move_1r * i)
            else:
                tp_price = entry_price - (price_move_1r * i)
            
            rr_data.append({
                "RR 배수": f"1:{i}",
                "익절가 (TP)": f"{tp_price:.2f}",
                "수익금 (예상)": f"${risk_amount * i:.2f}"
            })
        
        df_rr = pd.DataFrame(rr_data)
        st.dataframe(df_rr, use_container_width=True, hide_index=True)

# --- 탭 2: 청산가 계산기 ---
with tab2:
    st.header("청산가 계산 (단순화 모델)")
    
    # 1. 입력 섹션
    t2_col1, t2_col2 = st.columns(2)
    with t2_col1:
        liq_direction = st.radio("방향", ["LONG", "SHORT"], index=0, key="liq_dir")
        liq_entry = st.number_input("진입가", value=87500.0, step=1.0, format="%.2f", key="liq_entry")
        leverage = st.number_input("레버리지 (x)", value=200, step=1, key="liq_lev")
        
    with t2_col2:
        initial_notional = st.number_input("최초 포지션 (USD)", value=5000.0, step=100.0)
        add_on_notional = st.number_input("추가 매수 (USD)", value=10000.0, step=100.0)
        mmr = st.number_input("유지증거금 비율(MMR)", value=0.005, step=0.001, format="%.4f", help="0.5%면 0.005 입력")

    total_notional = initial_notional + add_on_notional
    
    # 2. 계산 로직 (표준 격리/교차 단순화 공식 적용)
    # 주의: 거래소마다 청산 공식이 미세하게 다르므로 일반적인 근사치 공식 사용
    if total_notional > 0 and liq_entry > 0 and leverage > 0:
        
        # 초기 증거금 (Initial Margin)
        im = total_notional / leverage
        # 유지 증거금 (Maintenance Margin) = 전체 사이즈 * MMR
        mm = total_notional * mmr
        
        # 청산가 계산 로직 (격리 마진 기준 근사치)
        # Long Liq = Entry * (1 - (1/Lev) + MMR)
        # Short Liq = Entry * (1 + (1/Lev) - MMR)
        
        if liq_direction == "LONG":
            liq_price = liq_entry * (1 - (1/leverage) + mmr)
        else:
            liq_price = liq_entry * (1 + (1/leverage) - mmr)

        # 진입가 대비 청산까지 %
        diff_percent = ((liq_price - liq_entry) / liq_entry) * 100

        # 3. 결과 표시
        st.markdown("---")
        st.markdown(f"#### ☠️ 청산 분석 결과")
        
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.error(f"예상 청산가: {liq_price:.2f}")
            st.metric("총 포지션 규모", f"${total_notional:,.0f}")
            
        with res_col2:
            st.metric("청산까지 거리 (%)", f"{diff_percent:.2f}%")
            st.metric("필요 유지증거금", f"${mm:.2f}")

    st.info("💡 참고: 실제 거래소의 청산가는 수수료 및 펀딩비 등의 변수로 인해 미세한 차이가 있을 수 있습니다.")
