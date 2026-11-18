# Five-year stock forecasting project – current status

## Scope
- User-provided source archive: `du_lieu.zip` (CafeF historical-price Excel workbooks).
- Period: 2021-11-18 to 2026-11-17.
- Current archive contains 145 workbooks and **29 distinct tickers**.
- After removing 87 overlapping duplicate ticker-date rows: 36,009 unique observations.
- One-year final holdout: target dates 2025-11-18 to 2026-11-17.
- Target: next trading session's unadjusted `Close`, per user confirmation.

## Important completeness note
The archive contains 29 symbols, not 30. The current processed dataset and metrics therefore cover 29 symbols. Supply the 30th ticker's five-year historical file(s) before describing this as a 30-ticker dataset. Do not fill or synthesize missing prices.

## Split design
- Development: target dates before 2025-11-18 (approximately four years).
- Final Test: target dates from 2025-11-18 through 2026-11-17.
- Features are calculated within each ticker and sorted by trading date.
- Development is further split chronologically 80/20 for validation.
- StandardScaler is fitted only on training data.
- The final baseline is refitted on all development data and evaluated on the untouched final year.

## Model
Linear Regression per ticker.
Features: Open, High, Low, Close, Matched_Volume, Price_Range, Daily_Return, MA5, MA20, Lag_1, Lag_2.
Target: `Target_Next_Close`.

## Current 29-ticker final test macro averages (unweighted)
- MAE: 1.010101
- MSE: 7.064959
- RMSE: 1.649712
- R2: 0.942609

## Quality notes
- No missing values in the core Date/Ticker/OHLC/Matched_Volume fields.
- 87 duplicate ticker-date rows removed; duplicate OHLCV values matched.
- Two Close values are outside Low-High bounds: MWG 2025-05-08 and STB 2025-05-06. Preserved and listed in `reports/ohlc_anomalies_review.csv` for source verification.
- `Close` is unadjusted as requested; corporate actions may cause discontinuities.

## Reproduce
```bash
pip install -r requirements.txt
python src/train_evaluate.py
```
Open `notebooks/01_five_year_eda_linear_regression.ipynb` and run from top to bottom.
