from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parent
RAW_PATH = ROOT / 'data' / 'processed' / 'market_data_5y_30_tickers.csv'
FEATURE_PATH = ROOT / 'data' / 'processed' / 'supervised_features_all_30.csv'
METRICS_PATH = ROOT / 'reports' / 'final_test_metrics_by_ticker_30.csv'
FEATURES = ['Open','High','Low','Close','Matched_Volume','Price_Range','Daily_Return','MA5','MA20','Lag_1','Lag_2']
CUTOFF = pd.Timestamp('2025-11-18')

st.set_page_config(page_title='VN30 Stock Forecast', page_icon='📈', layout='wide')
st.markdown('''<style>
.block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: rgba(120,120,120,.07); padding: 14px; border-radius: 12px;}
</style>''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    raw = pd.read_csv(RAW_PATH, parse_dates=['Date'])
    feat = pd.read_csv(FEATURE_PATH, parse_dates=['Date','Target_Date'])
    metrics = pd.read_csv(METRICS_PATH) if METRICS_PATH.exists() else pd.DataFrame()
    return raw, feat, metrics

@st.cache_resource
def fit_models(feat):
    models = {}
    for ticker, group in feat.groupby('Ticker'):
        dev = group[group['Target_Date'] < CUTOFF].dropna(subset=FEATURES + ['Target_Next_Close'])
        if len(dev) < 30:
            continue
        scaler = StandardScaler()
        X = scaler.fit_transform(dev[FEATURES])
        model = LinearRegression().fit(X, dev['Target_Next_Close'])
        models[ticker] = (scaler, model)
    return models

def latest_feature(group):
    g = group.sort_values('Date').copy()
    if len(g) < 21:
        raise ValueError('Không đủ dữ liệu lịch sử để tạo đặc trưng MA20.')
    last = g.iloc[-1]
    return pd.DataFrame([{
        'Open': last['Open'], 'High': last['High'], 'Low': last['Low'],
        'Close': last['Close'], 'Matched_Volume': last['Matched_Volume'],
        'Price_Range': last['High'] - last['Low'],
        'Daily_Return': g['Close'].pct_change().iloc[-1],
        'MA5': g['Close'].tail(5).mean(), 'MA20': g['Close'].tail(20).mean(),
        'Lag_1': g['Close'].iloc[-2], 'Lag_2': g['Close'].iloc[-3]
    }], columns=FEATURES), pd.Timestamp(last['Date']), float(last['Close'])

raw, feat, metrics = load_data()
models = fit_models(feat)
tickers = sorted(set(raw['Ticker'].dropna().astype(str)) & set(models))

st.title('📈 VN30 – Hệ thống phân tích và dự báo giá cổ phiếu')
st.caption('Đồ án học máy · Hồi quy tuyến tính (Linear Regression) · Dự báo giá đóng cửa phiên kế tiếp')

with st.sidebar:
    st.header('Thiết lập dự báo')
    ticker = st.selectbox('Chọn mã cổ phiếu', tickers, index=tickers.index('FPT') if 'FPT' in tickers else 0)
    st.divider()
    st.caption('Dữ liệu được đóng gói cùng ứng dụng. Dự báo chỉ cập nhật khi bạn thay bộ dữ liệu mới.')
    st.caption('Nguồn dữ liệu trong bộ hiện tại: CafeF (file lịch sử do người dùng cung cấp).')

stock = raw[raw['Ticker'].astype(str) == ticker].sort_values('Date').copy()
X_latest, last_date, last_close = latest_feature(stock)
scaler, model = models[ticker]
prediction = float(model.predict(scaler.transform(X_latest))[0])
change = prediction - last_close
pct = change / last_close * 100 if last_close else np.nan

c1,c2,c3,c4 = st.columns(4)
c1.metric('Giá đóng cửa gần nhất', f'{last_close:,.2f}')
c2.metric('Giá dự báo phiên kế tiếp', f'{prediction:,.2f}', f'{change:+,.2f} ({pct:+.2f}%)')
c3.metric('Phiên dữ liệu gần nhất', last_date.strftime('%d/%m/%Y'))
c4.metric('Số phiên lịch sử', f'{len(stock):,}')

st.info('Lưu ý: Đây là dự báo từ dữ liệu lịch sử đến ngày ' + last_date.strftime('%d/%m/%Y') + '. Không phải dữ liệu giá trực tuyến và không phải khuyến nghị mua/bán cổ phiếu.')

left, right = st.columns([1.65,1])
with left:
    st.subheader(f'Lịch sử giá đóng cửa – {ticker}')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock['Date'], y=stock['Close'], mode='lines', name='Giá đóng cửa'))
    fig.add_trace(go.Scatter(x=[last_date, last_date + pd.Timedelta(days=1)], y=[last_close, prediction], mode='lines+markers', name='Điểm dự báo', line=dict(dash='dash')))
    fig.update_layout(height=420, margin=dict(l=10,r=10,t=20,b=10), xaxis_title='Ngày', yaxis_title='Giá', legend=dict(orientation='h', y=1.08))
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader('Thông tin mô hình')
    st.write('**Thuật toán:** Linear Regression')
    st.write('**Biến đầu vào:** Open, High, Low, Close, Volume, Price Range, Daily Return, MA5, MA20, Lag1, Lag2')
    st.write('**Biến mục tiêu:** Close phiên kế tiếp')
    st.write('**Development:** trước 18/11/2025')
    st.write('**Final Test:** từ 18/11/2025')
    if not metrics.empty:
        row = metrics[metrics['Ticker'] == ticker]
        if not row.empty:
            r = row.iloc[0]
            st.markdown('**Kết quả Final Test của mã**')
            st.metric('MAE', f"{r['MAE']:.4f}")
            st.metric('RMSE', f"{r['RMSE']:.4f}")
            st.metric('R²', f"{r['R2']:.4f}")

st.subheader('Dữ liệu gần nhất')
st.dataframe(stock[['Date','Open','High','Low','Close','Matched_Volume']].tail(10).sort_values('Date', ascending=False), use_container_width=True, hide_index=True)

with st.expander('Xem kết quả đánh giá Final Test của toàn bộ mã'):
    if not metrics.empty:
        st.dataframe(metrics.sort_values('Ticker'), use_container_width=True, hide_index=True)
        st.download_button('Tải bảng kết quả CSV', metrics.to_csv(index=False).encode('utf-8-sig'), file_name='final_test_metrics_30_tickers.csv', mime='text/csv')

st.divider()
st.caption('Đồ án Học máy trong Phân tích và Dự báo Thị trường Chứng khoán Việt Nam · Bản demo học thuật.')
