import streamlit as st

# 1. 계산 핵심 로직 (함수화)
def calculate_liquidation_price(side, entry_price, leverage, mmr=0.01):
    """
    MEXC 격리 마진 기준 청산가 계산
    mmr: 유지 증거금율 (고배율일수록 높게 설정, 기본 1% 권장)
    """
    if side == "LONG":
        return entry_price * (1 - (1 / leverage) + mmr)
    else:
        return entry_price * (1 + (1 / leverage) - mmr)

def calculate_risk_metrics(margin, leverage, entry_price, stop_loss_price):
    """
    리스크 관리 계산 (손절가 기준 손실 금액 및 비율)
    """
    position_size = margin * leverage
    quantity = position_size / entry_price
    
    # 손실 금액 계산
    loss_amount = abs(entry_price - stop_loss_price) * quantity
    loss_percentage = (loss_amount / margin) * 100
    
    return position_size, loss_amount, loss_percentage

# 2. Streamlit UI 구성
st.set_page_config(page_title="MEXC 통합 트레이딩 계산기", layout="wide")
st.title("📊 통합 리스크 & 청산가 계산기")

# 사이드바: 공통 설정 (레버리지, 증거금)
st.sidebar.header("⚙️ 기본 설정")
side = st.sidebar.radio("포지션 방향", ["LONG", "SHORT"])
leverage = st.sidebar.select_slider("레버리지 (Leverage)", options=[20, 50, 100, 125, 150, 200])
margin = st.sidebar.number_input("투자 증거금 (Margin, USDT)", value=1000)

# 메인 화면: 입력 정보
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 진입 정보")
    entry_price = st.number_input("진입 평단가 (Entry Price)", value=65000.0, step=100.0)
    stop_loss_price = st.number_input("손절가 (Stop Loss)", value=63000.0, step=100.0)

# 3. 실시간 계산 수행 (레버리지나 값이 바뀔 때마다 자동 실행됨)
liq_price = calculate_liquidation_price(side, entry_price, leverage)
pos_size, loss_amt, loss_pct = calculate_risk_metrics(margin, leverage, entry_price, stop_loss_price)

with col2:
    st.subheader("📉 청산 및 리스크 결과")
    
    # 결과 요약 카드형태 표시
    st.error(f"⚠️ 예상 청산가: {liq_price:,.2f} USDT")
    
    res_col1, res_col2 = st.columns(2)
    res_col1.metric("총 포지션 규모", f"{pos_size:,.0f} USDT")
    res_col1.metric("예상 손실액", f"-{loss_amt:,.2f} USDT")
    
    res_col2.metric("레버리지 배율", f"{leverage}x")
    res_col2.metric("증거금 대비 손실률", f"{loss_pct:.2f}%", delta=f"-{loss_pct:.2f}%", delta_color="inverse")

# 4. 추가 팁 (유지 증거금 설명)
with st.expander("ℹ️ 계산 기준 안내"):
    st.write("""
    - **청산가**: MEXC 격리 마진 공식을 기준으로 하며, 유지 증거금율(MMR) 1%를 가정합니다.
    - **통합 관리**: 레버리지를 슬라이더로 조절하면 청산가와 리스크 지표가 즉시 업데이트됩니다.
    - **주의**: 실제 거래소의 청산가는 시장 수수료 및 펀딩비에 따라 미세하게 다를 수 있습니다.
    """)
