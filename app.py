import streamlit as st
import FinanceDataReader as fdr
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="종가 베팅 스캐너", layout="wide")
st.title("🛡️ 종가 베팅 전략 실시간 대시보드")

@st.cache_data(ttl=3600)
def get_results():
    # 코스피/코스닥 주요 종목 스캔 (속도를 위해 KRX 주요 종목 샘플링)
    df_krx = fdr.StockListing('KRX').head(200) 
    final_list = []
    for _, row in df_krx.iterrows():
        try:
            df = fdr.DataReader(row['Code']).tail(250)
            if len(df) < 240: continue
            df['MA20'] = ta.sma(df['Close'], length=20)
            df['MA240'] = ta.sma(df['Close'], length=240)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['Value'] = df['Close'] * df['Volume'] / 1_000_000
            curr, prev = df.iloc[-1], df.iloc[-2]
            last_5 = df.iloc[-5:]
            last_20 = df.iloc[-20:]
            
            # 조건식 검증 (A~M 및 RSI 50-60 반영)
            c1 = 0 <= ((curr['Open'] - prev['Close']) / prev['Close'] * 100) <= 5.0
            c2 = curr['High'] > prev['High']
            c3 = curr['Volume'] == last_5['Volume'].max()
            c4 = curr['Close'] > curr['Open']
            c5 = curr['Close'] == last_5['Close'].max()
            c6 = last_20['Value'].max() >= 30000
            c7 = curr['Close'] >= curr['MA20'] and curr['Close'] >= curr['MA240']
            c8 = 50 <= curr['RSI'] <= 60

            if all([c1, c2, c3, c4, c5, c6, c7, c8]):
                final_list.append([row['Name'], int(curr['Close']), round(curr['RSI'], 1), int(curr['Value']/100)])
        except: continue
    return pd.DataFrame(final_list, columns=['종목명', '현재가', 'RSI', '거래대금(억)'])

if st.button("🚀 종목 스캔 시작"):
    with st.spinner('조건에 맞는 종목을 찾는 중입니다...'):
        res = get_results()
        if not res.empty:
            st.table(res)
        else:
            st.warning("조건에 맞는 종목이 없습니다.")