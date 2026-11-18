# Bộ dữ liệu và mô hình hồi quy – 30 mã

- Nguồn dữ liệu: CafeF (theo các workbook trong ZIP mới).
- Giai đoạn: 18/11/2021–17/11/2026.
- Danh sách 30 mã: ACB, BID, CTG, DGC, FPT, GAS, GVR, HDB, HPG, LPB, MBB, MSN, MWG, PLX, POW, SAB, SHB, SSB, SSI, STB, TCB, TPB, VCB, VHM, VIB, VIC, VJC, VNM, VPB, VRE.
- Mục tiêu: Close phiên kế tiếp (chưa điều chỉnh).
- Development: Target_Date < 18/11/2025.
- Final Test: Target_Date từ 18/11/2025 đến 17/11/2026.
- MCH không đưa vào do thiếu giai đoạn 18/11/2023–18/11/2024.
- Có 90 bản ghi trùng được loại theo Ticker-Date; 3 điểm Close ngoài biên High-Low cần xác minh.

Kết quả macro-average theo 30 mã:
- MAE: 0.984092
- MSE: 6.835487
- RMSE: 1.608896
- R²: 0.941525

Lưu ý: nếu yêu cầu môn học bắt buộc nguồn Vietstock, cần xác nhận với giảng viên vì workbook hiện tại là CafeF.
