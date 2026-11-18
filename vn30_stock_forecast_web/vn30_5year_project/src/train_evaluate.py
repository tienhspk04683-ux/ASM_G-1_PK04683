
from pathlib import Path
import pandas as pd, numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"processed"/"supervised_features_all_30.csv"
OUT=ROOT/"reports"; OUT.mkdir(exist_ok=True)
features=["Open","High","Low","Close","Matched_Volume","Price_Range","Daily_Return","MA5","MA20","Lag_1","Lag_2"]
df=pd.read_csv(DATA,parse_dates=["Date","Target_Date"])
cutoff=pd.Timestamp("2025-11-18")
all_metrics=[]; all_preds=[]; val_metrics=[]
for ticker,g in df.groupby("Ticker"):
    g=g.sort_values("Target_Date").copy()
    dev=g[g.Target_Date<cutoff]
    test=g[g.Target_Date>=cutoff]
    # chronological validation: last 20% of 4-year development window
    val_start=dev.Target_Date.quantile(0.8)
    tr=dev[dev.Target_Date<val_start]
    va=dev[dev.Target_Date>=val_start]
    sc=StandardScaler()
    Xtr=sc.fit_transform(tr[features]); Xva=sc.transform(va[features])
    model=LinearRegression().fit(Xtr,tr["Target_Next_Close"])
    pv=model.predict(Xva)
    val_metrics.append({"Ticker":ticker,"Validation_rows":len(va),
       "MAE":mean_absolute_error(va.Target_Next_Close,pv),
       "RMSE":mean_squared_error(va.Target_Next_Close,pv)**0.5,
       "R2":r2_score(va.Target_Next_Close,pv)})
    # refit scaler/model on all first 4 years, then evaluate untouched final year
    sc_final=StandardScaler()
    Xdev=sc_final.fit_transform(dev[features]); Xtest=sc_final.transform(test[features])
    final_model=LinearRegression().fit(Xdev,dev["Target_Next_Close"])
    pred=final_model.predict(Xtest)
    mse=mean_squared_error(test.Target_Next_Close,pred)
    all_metrics.append({"Ticker":ticker,"Development_rows":len(dev),"Final_Test_rows":len(test),
       "MAE":mean_absolute_error(test.Target_Next_Close,pred),"MSE":mse,
       "RMSE":mse**0.5,"R2":r2_score(test.Target_Next_Close,pred)})
    p=test[["Date","Target_Date","Ticker","Target_Next_Close"]].copy()
    p["Predicted_Next_Close"]=pred
    all_preds.append(p)
m=pd.DataFrame(all_metrics).sort_values("Ticker")
v=pd.DataFrame(val_metrics).sort_values("Ticker")
p=pd.concat(all_preds,ignore_index=True)
m.to_csv(OUT/"final_test_metrics_by_ticker_30.csv",index=False,encoding="utf-8-sig")
v.to_csv(OUT/"validation_metrics_by_ticker_30.csv",index=False,encoding="utf-8-sig")
p.to_csv(OUT/"final_test_predictions_30.csv",index=False,encoding="utf-8-sig")
print(m.to_string(index=False))
print("\\nMean metrics:")
print(m[["MAE","MSE","RMSE","R2"]].mean().to_string())
