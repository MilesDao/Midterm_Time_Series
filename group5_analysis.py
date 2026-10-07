# %% md
# Group 5 – Time Series Analysis of Hanoi Garment CPI Data and Indonesia Economic Data
Part 1 uses `Data01_05_GarmentCPI.csv`, Part 2 uses `Data02_05_Indonesia_C.csv`.

# %% setup
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf, adfuller, kpss
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import IsolationForest
import ruptures as rpt

plt.rcParams["figure.figsize"] = (10, 4)
plt.rcParams["figure.dpi"] = 110

cpi = pd.read_csv("GrProjCPIData/Data01_05_GarmentCPI.csv")
cpi.columns = cpi.columns.str.strip()
cpi.index = pd.date_range("2015-01-01", periods=len(cpi), freq="MS")
s1 = cpi["GarmentFWHattoDecCPI"].rename("CPI (series 1)")
s3 = cpi["CPI_rate"].rename("CPI rate (series 3)")
SERIES = {"CPI (series 1)": s1, "CPI rate (series 3)": s3}
print(cpi.head())
print(cpi.shape)
print(cpi[["GarmentFWHattoDecCPI", "CPI_toPM", "CPI_rate"]].describe().round(3))

# %% md
## 1.1 Time series description – A. Time series plot

# %% p1_A1
s1.plot(marker="o", ms=3, title="A1. Hanoi Garment, footwear & hat CPI (series 1), 2015-2022")
plt.axhline(100, color="grey", ls="--", lw=1)
plt.ylabel("CPI (previous period = 100)")
plt.show()

# %% p1_A2
s3.plot(marker="o", ms=3, color="tab:orange", title="A2. Garment CPI rate (series 3), 2015-2022")
plt.axhline(0, color="grey", ls="--", lw=1)
plt.ylabel("CPI rate (%)")
plt.show()

# %% md
## B. Time series trend checking
12-month rolling mean + linear regression of the series on time + seasonal profile by month.

# %% p1_B_func
def check_trend(s, color):
    t = np.arange(len(s))
    reg = stats.linregress(t, s.values)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(s.index, s, color=color, alpha=0.5, label="series")
    ax[0].plot(s.index, s.rolling(12).mean(), color="black", lw=2, label="12-month rolling mean")
    ax[0].plot(s.index, reg.intercept + reg.slope * t, "r--", label="linear trend")
    ax[0].legend(); ax[0].set_title(f"Trend of {s.name}")
    month_dev = s.groupby(s.index.month).mean() - s.mean()
    month_dev.plot(kind="bar", ax=ax[1], color=color)
    ax[1].set_title("Calendar-month mean minus overall mean"); ax[1].set_xlabel("month")
    plt.tight_layout(); plt.show()
    print(f"Linear trend: slope = {reg.slope:.5f} per month, p-value = {reg.pvalue:.4f}, R^2 = {reg.rvalue**2:.4f}")
    print("Month deviations:", month_dev.round(3).to_dict())
    print("Yearly means:"); print(s.groupby(s.index.year).mean().round(3).to_string())

# %% p1_B1
check_trend(s1, "tab:blue")

# %% p1_B2
check_trend(s3, "tab:orange")

# %% md
## C. Autocorrelation function (ACF)

# %% p1_C_func
def significant_lags(values, confint):
    # a lag is significant when the 95% confidence band (centred on 0) does not contain the coefficient
    half = confint[:, 1] - values
    return [k for k in range(1, len(values)) if abs(values[k]) > half[k]]

# %% p1_C1
plot_acf(s1, lags=24, title="C1. ACF of CPI (series 1)"); plt.show()
a1, ci = acf(s1, nlags=24, alpha=0.05)
print("ACF lags 1-12:", np.round(a1[1:13], 3))
print("Significant ACF lags:", significant_lags(a1, ci))

# %% p1_C2
plot_acf(s3, lags=24, title="C2. ACF of CPI rate (series 3)"); plt.show()
a3, ci = acf(s3, nlags=24, alpha=0.05)
print("ACF lags 1-12:", np.round(a3[1:13], 3))
print("Significant ACF lags:", significant_lags(a3, ci))

# %% md
## D. Partial autocorrelation function (PACF)

# %% p1_D1
plot_pacf(s1, lags=24, method="ywm", title="D1. PACF of CPI (series 1)"); plt.show()
pa1, ci = pacf(s1, nlags=24, method="ywm", alpha=0.05)
print("PACF lags 1-12:", np.round(pa1[1:13], 3))
print("Significant PACF lags:", significant_lags(pa1, ci))

# %% p1_D2
plot_pacf(s3, lags=24, method="ywm", title="D2. PACF of CPI rate (series 3)"); plt.show()
pa3, ci = pacf(s3, nlags=24, method="ywm", alpha=0.05)
print("PACF lags 1-12:", np.round(pa3[1:13], 3))
print("Significant PACF lags:", significant_lags(pa3, ci))

# %% md
## E. Stationarity test (ADF: H0 = unit root; KPSS: H0 = stationary)

# %% p1_E_func
def stationarity_test(s):
    adf = adfuller(s, autolag="AIC")
    print(f"ADF  statistic = {adf[0]:.4f}, p-value = {adf[1]:.6f}, lags used = {adf[2]}")
    print("     critical values:", {k: round(float(v), 3) for k, v in adf[4].items()})
    print("     ->", "stationary (reject H0)" if adf[1] < 0.05 else "non-stationary (cannot reject H0)")
    with warnings.catch_warnings():   # KPSS warns when p-value is beyond its table (p > 0.1)
        warnings.simplefilter("ignore")
        k = kpss(s, regression="c", nlags="auto")
    print(f"KPSS statistic = {k[0]:.4f}, p-value = {k[1]:.4f}")
    print("     ->", "stationary (cannot reject H0)" if k[1] >= 0.05 else "non-stationary (reject H0)")

# %% p1_E1
stationarity_test(s1)

# %% p1_E2
stationarity_test(s3)

# %% md
## 1.4 Estimating ARIMA models and model selection
Grid over p = 0..p_max, q = 0..q_max with d = 0 (from step 1.3). A model is *stable* when the 95%
confidence interval of every ARMA coefficient (ar.L*, ma.L*) excludes 0.

# %% p1_arima_func
def quiet_fit(data, order, seasonal_order=(0, 0, 0, 0)):
    # statsmodels re-enables its own warnings inside fit(), so silence them here
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ARIMA(data, order=order, seasonal_order=seasonal_order).fit()

def arima_grid(s, p_max, d, q_max):
    rows = []
    for p in range(p_max + 1):
        for q in range(q_max + 1):
            res = quiet_fit(s, (p, d, q))
            ci = res.conf_int()
            arma = [n for n in res.params.index if n.startswith(("ar.", "ma."))]
            stable = all(not (ci.loc[n, 0] <= 0 <= ci.loc[n, 1]) for n in arma)
            rows.append({"order": (p, d, q), "AIC": round(res.aic, 3), "BIC": round(res.bic, 3), "stable": stable})
    table = pd.DataFrame(rows).sort_values("AIC").reset_index(drop=True)
    best = table[table.stable].iloc[0]["order"]
    return table, best

# %% p1_14_A1
P1, D1, Q1 = 2, 0, 3   # maxima from step 1.3
table1, best1 = arima_grid(s1, P1, D1, Q1)
print(table1.to_string())

# %% p1_14_A2
print("Best stable model for CPI (series 1): ARIMA", best1)
best_fit1 = quiet_fit(s1, best1)
print(best_fit1.summary().tables[1])
print(f"AIC = {best_fit1.aic:.3f}")

# %% p1_14_B1
P3, D3, Q3 = 1, 0, 1   # maxima from step 1.3
table3, best3 = arima_grid(s3, P3, D3, Q3)
print(table3.to_string())

# %% p1_14_B2
print("Best stable model for CPI rate (series 3): ARIMA", best3)
best_fit3 = quiet_fit(s3, best3)
print(best_fit3.summary().tables[1])
print(f"AIC = {best_fit3.aic:.3f}")

# %% md
## 1.5 Mean values forecasting (next 12 months, 2023)

# %% p1_forecast_func
def forecast_mean(fit, s, steps=12, color="tab:blue"):
    fc = fit.get_forecast(steps=steps)
    mean, ci = fc.predicted_mean, fc.conf_int(alpha=0.05)
    out = pd.DataFrame({"forecast": mean, "lower 95%": ci.iloc[:, 0], "upper 95%": ci.iloc[:, 1]}).round(3)
    out.index = out.index.strftime("%Y-%m")
    print(out.to_string())
    ax = s.plot(color=color, label="observed")
    fit.fittedvalues.plot(ax=ax, color="green", alpha=0.6, label="fitted")
    mean.plot(ax=ax, color="red", label="forecast")
    ax.fill_between(ci.index, ci.iloc[:, 0], ci.iloc[:, 1], color="red", alpha=0.15, label="95% CI")
    ax.legend(); ax.set_title(f"12-month mean forecast of {s.name}"); plt.show()

# %% p1_15_A
forecast_mean(best_fit1, s1)

# %% p1_15_B
forecast_mean(best_fit3, s3, color="tab:orange")

# %% md
## 1.6 Machine learning in ARIMA forecasting
80% train / 20% test, walk-forward validation: re-fit on all history, forecast one month ahead, then
add the true value to the history.

# %% p1_16_func
def split(s, ratio=0.8):
    n = int(len(s) * ratio)
    return s.iloc[:n], s.iloc[n:]

def walk_forward(s, order, seasonal_order=(0, 0, 0, 0)):
    train, test = split(s)
    history, preds = list(train), []
    for actual in test:
        fit = quiet_fit(history, order, seasonal_order)
        preds.append(fit.forecast()[0])
        history.append(actual)
    preds = pd.Series(preds, index=test.index)
    rmse = np.sqrt(mean_squared_error(test, preds))
    return preds, rmse

def plot_test(s, preds, title):
    train, test = split(s)
    ax = train.plot(label="train", color="grey")
    test.plot(ax=ax, label="test (actual)", color="tab:blue", marker="o", ms=3)
    preds.plot(ax=ax, label="prediction", color="red", marker="x", ms=4)
    ax.legend(); ax.set_title(title); plt.show()

# %% p1_16_A1
train1, test1 = split(s1)
print(f"Train: {train1.index[0]:%Y-%m} .. {train1.index[-1]:%Y-%m}  ({len(train1)} obs)")
print(f"Test : {test1.index[0]:%Y-%m} .. {test1.index[-1]:%Y-%m}  ({len(test1)} obs)")

# %% p1_16_A2
preds1, rmse1 = walk_forward(s1, best1)
print(f"ARIMA{best1}: test RMSE = {rmse1:.4f}")
plot_test(s1, preds1, f"CPI (series 1) - ARIMA{best1} walk-forward forecast, RMSE = {rmse1:.4f}")
rmse_grid1 = pd.DataFrame([{"order": str(o), "RMSE": round(walk_forward(s1, o)[1], 4)} for o in table1.order])
print(rmse_grid1.sort_values("RMSE").to_string(index=False))

# %% p1_16_B1
train3, test3 = split(s3)
print(f"Train: {train3.index[0]:%Y-%m} .. {train3.index[-1]:%Y-%m}  ({len(train3)} obs)")
print(f"Test : {test3.index[0]:%Y-%m} .. {test3.index[-1]:%Y-%m}  ({len(test3)} obs)")

# %% p1_16_B2
preds3, rmse3 = walk_forward(s3, best3)
print(f"ARIMA{best3}: test RMSE = {rmse3:.4f}")
plot_test(s3, preds3, f"CPI rate (series 3) - ARIMA{best3} walk-forward forecast, RMSE = {rmse3:.4f}")
rmse_grid3 = pd.DataFrame([{"order": str(o), "RMSE": round(walk_forward(s3, o)[1], 4)} for o in table3.order])
print(rmse_grid3.sort_values("RMSE").to_string(index=False))

# %% md
## 1.7 Machine learning in SARIMA forecasting – SARIMA(pO,dO,qO)(P,0,Q,12)

# %% p1_17_func
def sarima_grid(s, order, PQ=range(3)):
    rows = []
    for P in PQ:
        for Q in PQ:
            rows.append({"seasonal (P,D,Q,m)": (P, 0, Q, 12), "RMSE": round(walk_forward(s, order, (P, 0, Q, 12))[1], 4)})
    table = pd.DataFrame(rows).sort_values("RMSE").reset_index(drop=True)
    # (0,0,0,12) is plain ARIMA: keep it as the baseline but pick the best truly seasonal model
    best = table[table["seasonal (P,D,Q,m)"] != (0, 0, 0, 12)].iloc[0]["seasonal (P,D,Q,m)"]
    return table, best

# %% p1_17_A1
sp1, srmse1 = walk_forward(s1, best1, (1, 0, 1, 12))
print(f"SARIMA{best1}(1,0,1,12): test RMSE = {srmse1:.4f}")
plot_test(s1, sp1, f"CPI (series 1) - SARIMA{best1}(1,0,1,12), RMSE = {srmse1:.4f}")

# %% p1_17_A2
sg1, bs1 = sarima_grid(s1, best1)
print(sg1.to_string())
bp1, brmse1 = walk_forward(s1, best1, bs1)
print(f"Best: SARIMA{best1}{bs1}, RMSE = {brmse1:.4f}  (plain ARIMA{best1}: {rmse1:.4f})")
plot_test(s1, bp1, f"CPI (series 1) - best SARIMA{best1}{bs1}, RMSE = {brmse1:.4f}")

# %% p1_17_B1
sp3, srmse3 = walk_forward(s3, best3, (1, 0, 1, 12))
print(f"SARIMA{best3}(1,0,1,12): test RMSE = {srmse3:.4f}")
plot_test(s3, sp3, f"CPI rate (series 3) - SARIMA{best3}(1,0,1,12), RMSE = {srmse3:.4f}")

# %% p1_17_B2
sg3, bs3 = sarima_grid(s3, best3)
print(sg3.to_string())
bp3, brmse3 = walk_forward(s3, best3, bs3)
print(f"Best: SARIMA{best3}{bs3}, RMSE = {brmse3:.4f}  (plain ARIMA{best3}: {rmse3:.4f})")
plot_test(s3, bp3, f"CPI rate (series 3) - best SARIMA{best3}{bs3}, RMSE = {brmse3:.4f}")

# %% md
# Part 2 – Anomalies and change points in Indonesia economic data (1990-2021)

# %% p2_setup
eco = pd.read_csv("GrProjEconData/Data02_05_Indonesia_C.csv", index_col="year")
print(eco.drop(columns="country").describe().T.round(3))
print("Missing values:", eco.isna().sum()[eco.isna().sum() > 0].to_dict())
COLS = ["ggdp", "mil", "inf", "fdi", "gdp"]
NAMES = {"ggdp": "Green GDP (USD)", "mil": "Military spending (% of GDP)", "inf": "Inflation (%)",
         "fdi": "FDI net inflows (USD)", "gdp": "GDP (USD)"}

def get(col):
    return eco[col].dropna()   # missing years are skipped, not imputed

# %% md
## 2.1 Z-score method (|z| > 3)

# %% p2_z_func
def zscore_anomalies(col, threshold=3):
    s = get(col)
    z = (s - s.mean()) / s.std()
    out = s[z.abs() > threshold]
    ax = s.plot(marker="o", ms=4, title=f"Z-score anomalies (|z| > {threshold}) - {NAMES[col]}")
    ax.scatter(out.index, out, color="red", s=80, zorder=3, label="anomaly")
    ax.legend(); plt.show()
    print(pd.DataFrame({"value": s, "z": z.round(3)}).loc[z.abs().sort_values(ascending=False).index[:3]])
    print("Anomalies:", {int(y): round(float(v), 3) for y, v in out.items()} or "none")

# %% p2_z_ggdp
zscore_anomalies("ggdp")

# %% p2_z_mil
zscore_anomalies("mil")

# %% p2_z_inf
zscore_anomalies("inf")

# %% p2_z_fdi
zscore_anomalies("fdi")

# %% p2_z_gdp
zscore_anomalies("gdp")

# %% md
## 2.1 Isolation Forest (contamination = 0.1, i.e. about 3 of 32 years)

# %% p2_if_func
def iforest_anomalies(col, contamination=0.1):
    s = get(col)
    model = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    X = s.values.reshape(-1, 1)
    label = model.fit_predict(X)
    score = model.decision_function(X)
    out = s[label == -1]
    ax = s.plot(marker="o", ms=4, title=f"Isolation Forest anomalies - {NAMES[col]}")
    ax.scatter(out.index, out, color="red", s=80, zorder=3, label="anomaly")
    ax.legend(); plt.show()
    print(pd.DataFrame({"value": out, "score": score[label == -1].round(4)}))

# %% p2_if_ggdp
iforest_anomalies("ggdp")

# %% p2_if_mil
iforest_anomalies("mil")

# %% p2_if_inf
iforest_anomalies("inf")

# %% p2_if_fdi
iforest_anomalies("fdi")

# %% p2_if_gdp
iforest_anomalies("gdp")

# %% md
## 2.2 Change point detection (ruptures PELT, RBF cost, on the standardised series)

# %% p2_cp_func
def change_points(col, pen=3):
    s = get(col)
    x = ((s - s.mean()) / s.std()).values
    bkps = rpt.Pelt(model="rbf", min_size=3).fit(x).predict(pen=pen)
    years = [int(s.index[b]) for b in bkps[:-1]]   # first year of each new regime
    ax = s.plot(marker="o", ms=4, title=f"Change points (PELT) - {NAMES[col]}")
    for y in years:
        ax.axvline(y - 0.5, color="red", ls="--")
    for a, b in zip([0] + bkps[:-1], bkps):
        seg = s.iloc[a:b]
        ax.hlines(seg.mean(), seg.index[0] - 0.5, seg.index[-1] + 0.5, color="green", lw=2)
    plt.show()
    print("Change points (first year of new regime):", years)
    for a, b in zip([0] + bkps[:-1], bkps):
        seg = s.iloc[a:b]
        print(f"  segment {seg.index[0]}-{seg.index[-1]}: mean = {seg.mean():.4g}")

# %% p2_cp_ggdp
change_points("ggdp")

# %% p2_cp_mil
change_points("mil")

# %% p2_cp_inf
change_points("inf")

# %% p2_cp_fdi
change_points("fdi")

# %% p2_cp_gdp
change_points("gdp")
