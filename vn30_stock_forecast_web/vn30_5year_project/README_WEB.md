# Chạy website dự báo VN30

## 1. Chạy trên máy tính cá nhân

Cài Python 3.10–3.12, giải nén dự án và mở Terminal/CMD tại thư mục `vn30_5year_project`.

```bash
python -m venv .venv
```

Kích hoạt môi trường:
- Windows: `.venv\\Scripts\\activate`
- macOS/Linux: `source .venv/bin/activate`

Cài thư viện và chạy website:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Mở địa chỉ được in trong Terminal (thường là `http://localhost:8501`).

## 2. Đưa website lên Internet bằng Streamlit Community Cloud

1. Tạo tài khoản GitHub và đăng nhập.
2. Tạo repository mới, ví dụ `vn30-stock-forecast`.
3. Upload toàn bộ nội dung thư mục dự án lên repository (giữ nguyên thư mục `data/processed` và `reports`). Không cần upload `data/raw` nếu muốn giảm dung lượng repository; ứng dụng chỉ đọc các CSV đã xử lý.
4. Truy cập https://share.streamlit.io/ và kết nối GitHub.
5. Chọn **Create app**, chọn repository vừa tạo, branch `main`, file chính `app.py`.
6. Chọn **Deploy**. Khi build thành công, Streamlit cấp một đường dẫn `*.streamlit.app` để chia sẻ.

## 3. Cấu trúc tối thiểu cần có khi deploy

```text
app.py
requirements.txt
 data/
   processed/
     market_data_5y_30_tickers.csv
     supervised_features_all_30.csv
 reports/
   final_test_metrics_by_ticker_30.csv
```

## Lưu ý học thuật và dữ liệu

- Website hiện dùng dữ liệu đóng gói trong dự án, không tự lấy giá realtime. Mã dự báo sử dụng phiên gần nhất có trong CSV.
- Muốn cập nhật dự báo theo phiên mới, cần cập nhật `market_data_5y_30_tickers.csv` và `supervised_features_all_30.csv` đồng bộ, sau đó redeploy/restart app.
- Nguồn dữ liệu trong bộ hiện tại là các file CafeF đã cung cấp. Nếu đề bài bắt buộc Vietstock, cần thay bằng dữ liệu đúng nguồn và chạy lại pipeline.
- Dự báo là kết quả học thuật, không phải khuyến nghị đầu tư.
