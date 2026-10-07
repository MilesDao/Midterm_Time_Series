"""Report text for Group 5. ('code', tags) inserts the notebook cell(s) source + output."""

TITLE = "Time Series Analysis of Hanoi Garment CPI Data and Indonesia Economic Data"

STUDENTS = [
    ("Vu Thi Kim Oanh", "23BA14225"),
    ("Nguyen Khai Minh", "2410607"),
    ("Huynh Kim Gia Bao", "2410154"),
    ("Dang Nhat Minh", "2410667"),
    ("Dao Chi Trung", "23BA14295"),
]

CONTENT = [
("h1", "Introduction"),
("p", "This report applies time series analysis with machine learning in Python to two data sets assigned to "
      "group 5. Part 1 studies the monthly consumer price index (CPI) of the group \"Garments, footwear and hats\" "
      "in Hanoi from January 2015 to December 2022 (file Data01_05_GarmentCPI.csv): we describe the series, check "
      "trend, autocorrelation and stationarity, identify and estimate ARIMA models, forecast the mean values and "
      "evaluate ARIMA and SARIMA models with a train/test split. Part 2 studies annual economic indicators of "
      "Indonesia from 1990 to 2021 (file Data02_05_Indonesia_C.csv) and detects anomalies (Z-score, Isolation "
      "Forest) and change points (PELT). All computations were done in Python 3.12 with pandas, statsmodels 0.15, "
      "scikit-learn and ruptures; the complete runnable notebook is Group5_TimeSeries.ipynb."),

("pagebreak",),
("h1", "Part 1. Time Series Analysis of Hanoi CPI Data"),
("p", "Summary: We analyse the Hanoi garment, footwear and hat CPI and its monthly rate. Both series are stationary "
      "(d = 0). ARIMA(1,0,1) is selected for the CPI and ARIMA(0,0,1) for the CPI rate, by AIC and by test RMSE. "
      "Seasonal SARIMA terms do not improve the forecasts."),

("h2", "1.1 Introduction"),
("h3", "Time series analysis methodology"),
("p", "A time series is a sequence of observations ordered in time. Time series analysis describes the series "
      "(plot, trend, seasonality), measures its dependence on its own past with the autocorrelation function (ACF) "
      "and partial autocorrelation function (PACF), and checks stationarity (constant mean, variance and "
      "autocovariance) with the Augmented Dickey-Fuller (ADF) and KPSS tests. The Box-Jenkins approach then builds "
      "an ARIMA(p,d,q) model: d is the number of differences needed for stationarity, p the order of the "
      "autoregressive part (suggested by the PACF cut-off) and q the order of the moving-average part (suggested "
      "by the ACF cut-off). Candidate models are estimated by maximum likelihood and compared with the Akaike "
      "Information Criterion (AIC). In the machine-learning view, the series is split into a training part and a "
      "test part, the model is fitted on the training data and evaluated by the root mean squared error (RMSE) of "
      "its forecasts on the test data. SARIMA(p,d,q)(P,D,Q,m) adds seasonal AR and MA terms with period m "
      "(m = 12 for monthly data)."),
("h3", "CPI concept"),
("p", "The consumer price index measures the average change over time of the prices paid by households for a fixed "
      "basket of consumer goods and services. In Vietnam the General Statistics Office (GSO) publishes the CPI "
      "monthly for 11 main groups of goods and services; \"Garments, footwear and hats\" is one of them. An index "
      "value above 100 means prices are higher than in the base (reference) period, below 100 means they are "
      "lower. The CPI rate is the percentage change of prices relative to the previous period and is the usual "
      "measure of inflation."),
("h3", "Data array \"Data01_05_GarmentCPI.csv\""),
("p", "The file contains 96 monthly observations (January 2015 - December 2022) of the CPI of garments, footwear "
      "and hats in Hanoi. There are no missing values."),
("bullet", "+ Column 1: Time - timestamp index 1..96"),
("bullet", "+ Column 2: Year (2015-2022)"),
("bullet", "+ Column 3: Month (1-12)"),
("bullet", "+ Column 4: Series 1 - GarmentFWHattoDecCPI: monthly garment, footwear and hat CPI with December of the "
           "previous year = 100 (mean 100.14, range 99.44-100.70)"),
("bullet", "+ Column 5: Series 2 - CPI_toPM: monthly CPI relative to the previous month (= 100 x Series 1(t) / "
           "Series 1(t-1); in January it equals Series 1, whose base is the previous December)"),
("bullet", "+ Column 6: Series 3 - CPI_rate: monthly CPI rate in % = Series 2 - 100 (mean 0.023 %, range "
           "-0.59 % to +0.70 %)"),
("p", "Following the template, the analysis is done for Series 1 (CPI) and Series 3 (CPI rate)."),
("code", "setup"),

("h2", "1.2 Time series description"),
("h3", "A. Time series plot"),
("h4", "A1. CPI (series 1)"),
("code", "p1_A1"),
("comment", "The CPI moves in a narrow band between 99.44 and 100.70 around a mean of 100.14, and is above 100 in "
            "most months, i.e. garment prices in Hanoi are usually slightly higher than in the previous December. "
            "The highest values are January 2015 and December 2017 (100.7, before the Lunar New Year), followed by a "
            "plateau at 100.5-100.6 from July to December 2018. The lowest value is April 2020 (99.44), the month of "
            "the nationwide COVID-19 social distancing, and values below 100 also appear in late 2019 and early "
            "2020. From 2020 the values are recorded with two decimals and the fluctuations are smaller. The series "
            "has no explosive or long-run upward movement; it keeps returning to its mean, which suggests "
            "stationarity."),
("h4", "A2. CPI rate (series 3)"),
("code", "p1_A2"),
("comment", "The CPI rate oscillates around zero (mean 0.023 %, standard deviation 0.214 %) between -0.59 % "
            "(April 2020) and +0.70 % (January 2015). Positive and negative months alternate frequently: a rise is "
            "often followed by a fall, which already suggests negative autocorrelation at lag 1. The variance is "
            "roughly constant, slightly smaller after 2020. There is no visible trend."),

("h3", "B. Time series trend checking"),
("h4", "B1. CPI (series 1)"),
("code", ["p1_B_func", "p1_B1"]),
("comment", "The linear trend has a slope of -0.0017 per month (about -0.02 index points per year). Its p-value "
            "(0.020) is below 0.05, but R^2 = 0.056, so the trend explains less than 6 % of the variation and is "
            "practically negligible. The 12-month rolling mean shows medium-term swings rather than a trend: about "
            "100.2 in 2015-2017, a peak of about 100.36 in late 2018, a trough of about 99.93 in 2020 (COVID-19) and "
            "a recovery to 100.15 in 2022. The calendar-month profile shows a mild seasonal pattern: December "
            "(+0.13) and January (+0.04) are above the mean (Lunar New Year shopping), April (-0.13) and "
            "February-March are below it. The effect is small compared with the noise."),
("h4", "B2. CPI rate (series 3)"),
("code", "p1_B2"),
("comment", "The CPI rate has no trend: slope -0.0002 per month with p-value 0.81 and R^2 = 0.0006. The yearly "
            "means are all between 0.003 % and 0.058 %. The rolling mean stays close to zero. By calendar month, "
            "January (+0.16) and May (+0.10) have the largest increases and February (-0.13) and April (-0.10) the "
            "largest decreases, again a weak Tet-related pattern."),

("h3", "C. Autocorrelation function"),
("h4", "C1. CPI (series 1)"),
("code", ["p1_C_func", "p1_C1"]),
("comment", "The ACF is positive and decays gradually: 0.31, 0.36 and 0.25 at lags 1-3 lie outside the 95 % "
            "confidence band; from lag 4 on the coefficients are inside the band (lag 6 = 0.25 is close to the "
            "boundary) and are about 0 at lag 12. The quick decay confirms stationarity, and the absence of a spike "
            "at lag 12 shows that yearly seasonality is weak. The ACF suggests an MA order of at most 3."),
("h4", "C2. CPI rate (series 3)"),
("code", "p1_C2"),
("comment", "Only lag 1 is significant, with a strong negative value (-0.47); all other lags are inside the band. "
            "An ACF that cuts off after lag 1 is the signature of an MA(1) process. The value is close to -0.5, "
            "the theoretical lag-1 autocorrelation of a differenced white noise: the CPI rate is essentially the "
            "month-to-month change of series 1, which explains this pattern."),

("h3", "D. Partial autocorrelation function"),
("h4", "D1. CPI (series 1)"),
("code", "p1_D1"),
("comment", "The PACF has significant spikes at lags 1 (0.31) and 2 (0.29) and then cuts off (lag 3 = 0.11, all "
            "later lags inside the band). This is the pattern of an AR(2) process, so the maximum AR order is 2."),
("h4", "D2. CPI rate (series 3)"),
("code", "p1_D2"),
("comment", "Only lag 1 (-0.47) is significant. Lags 2-5 are small negative values (-0.17 to -0.12) decaying "
            "slowly inside the band, which is the tail expected from an MA(1) process. The maximum AR order is 1."),

("h3", "E. Stationarity test"),
("p", "ADF test: H0 = the series has a unit root (non-stationary). KPSS test: H0 = the series is stationary. "
      "Using both tests gives a more reliable conclusion."),
("h4", "E1. CPI (series 1)"),
("code", ["p1_E_func", "p1_E1"]),
("comment", "ADF statistic = -4.21 is below the 1 % critical value (-3.50), p-value = 0.0006 < 0.05, so the unit "
            "root hypothesis is rejected. KPSS statistic = 0.36 with p-value 0.094 > 0.05, so stationarity is not "
            "rejected. Both tests agree: the CPI series is stationary in levels and does not need differencing."),
("h4", "E2. CPI rate (series 3)"),
("code", "p1_E2"),
("comment", "ADF statistic = -6.63, p-value < 0.000001: the unit root is strongly rejected. KPSS statistic = 0.10, "
            "p-value >= 0.10: stationarity is not rejected. The CPI rate is stationary."),

("h2", "1.3 Determine parameters p, q and d in ARIMA(p,d,q) model"),
("h3", "Maximum value of p from the PACF"),
("p", "A1. CPI (series 1): the PACF is significant at lags 1 and 2 and cuts off after lag 2, so p_max = 2."),
("p", "A2. CPI rate (series 3): only lag 1 of the PACF is significant, so p_max = 1."),
("h3", "Maximum value of q from the ACF"),
("p", "B1. CPI (series 1): the ACF is significant at lags 1, 2 and 3, so q_max = 3."),
("p", "B2. CPI rate (series 3): the ACF cuts off after lag 1, so q_max = 1."),
("h3", "Value of d from the stationarity test"),
("p", "C1. CPI (series 1): ADF and KPSS both indicate stationarity in levels, so d = 0."),
("p", "C2. CPI rate (series 3): ADF and KPSS both indicate stationarity, so d = 0."),

("h2", "1.4 Estimating ARIMA models and model selection"),
("p", "For each series all combinations p = 0..p_max, q = 0..q_max with d = 0 are estimated in a loop. A model is "
      "considered to have stable parameters when the 95 % confidence interval of every AR and MA coefficient does "
      "not contain 0 (all coefficients significant). Among the stable models the one with the lowest AIC is "
      "selected."),
("h3", "CPI (series 1)"),
("h4", "A1. Estimating ARIMA(p,0,q), p = 0..2, q = 0..3"),
("code", ["p1_arima_func", "p1_14_A1"]),
("h4", "A2. Selecting the best ARIMA model"),
("code", "p1_14_A2"),
("comment", "Twelve models were estimated. ARIMA(1,0,1) has the lowest AIC (-52.99) and all its coefficients are "
            "significant: ar.L1 = 0.874 (CI 0.70 to 1.05) and ma.L1 = -0.632 (CI -0.91 to -0.35). ARIMA(2,0,0) is "
            "almost as good (AIC -52.84) and also stable; larger models such as ARIMA(2,0,1) or ARIMA(1,0,2) have "
            "higher AIC and contain insignificant coefficients (over-fitting). The best model is therefore "
            "ARIMA(pO,dO,qO) = ARIMA(1,0,1): CPI(t) = 100.159 + 0.874 (CPI(t-1) - 100.159) + e(t) - 0.632 e(t-1). "
            "The AR coefficient close to 1 shows that deviations from the mean decay slowly (persistence)."),
("h3", "CPI rate (series 3)"),
("h4", "B1. Estimating ARIMA(p,0,q), p = 0..1, q = 0..1"),
("code", "p1_14_B1"),
("h4", "B2. Selecting the best ARIMA model"),
("code", "p1_14_B2"),
("comment", "ARIMA(0,0,1) has the lowest AIC (-48.96) and is stable: ma.L1 = -0.569 (CI -0.69 to -0.45) and the "
            "constant 0.0205 (CI 0.004 to 0.037) are significant. ARIMA(1,0,1) has a higher AIC and an "
            "insignificant coefficient, ARIMA(1,0,0) is stable but has a higher AIC. The best model is "
            "ARIMA(pO,dO,qO) = ARIMA(0,0,1): rate(t) = 0.0205 + e(t) - 0.569 e(t-1), in agreement with the ACF/PACF "
            "analysis."),

("h2", "1.5 Mean values forecasting for ARIMA model"),
("h3", "CPI (series 1) - ARIMA(1,0,1), 12 months ahead"),
("code", ["p1_forecast_func", "p1_15_A"]),
("comment", "The forecast for January 2023 is 100.20 and it decreases smoothly to 100.17 in December 2023, "
            "converging to the long-run mean 100.16 at the speed given by the AR coefficient 0.874. The 95 % "
            "confidence interval is about 99.79-100.55 and widens only slightly with the horizon because the "
            "series is stationary. The fitted values follow the general level of the series but smooth out the "
            "isolated spikes (December 2017, April 2020)."),
("h3", "CPI rate (series 3) - ARIMA(0,0,1), 12 months ahead"),
("code", "p1_15_B"),
("comment", "An MA(1) model only remembers one past shock, so the forecast for January 2023 (-0.007 %) uses the "
            "last residual and from February 2023 it equals the mean 0.020 % per month. The 95 % interval "
            "(-0.39 % to +0.43 %) is wide compared with the mean: month-to-month changes of garment prices are "
            "hard to predict beyond one step."),

("h2", "1.6 Machine learning in ARIMA model forecasting"),
("p", "The series is split chronologically: the first 80 % (76 months) is the training part and the last 20 % "
      "(20 months) the test part. Walk-forward validation is used: at each test month the model is re-estimated on "
      "all data available up to that month, a one-step-ahead forecast is made, then the true value is added to the "
      "history. The accuracy is measured by RMSE on the test part. The forecast is also repeated for all (p,d,q) "
      "combinations of step 1.4 to find the model with the lowest RMSE."),
("h3", "CPI (series 1)"),
("h4", "A1. Train / test split"),
("code", ["p1_16_func", "p1_16_A1"]),
("h4", "A2. Forecasting with ARIMA(1,0,1) and with all combinations"),
("code", "p1_16_A2"),
("comment", "ARIMA(1,0,1) reaches a test RMSE of 0.1146 index points, the lowest among all 12 combinations, so the "
            "RMSE criterion confirms the AIC choice. ARIMA(1,0,0) is almost equal (0.1149), while the constant-mean "
            "model ARIMA(0,0,0) gives 0.1263, i.e. the ARIMA dynamics reduce the error by about 9 %. The predictions "
            "follow the level of the test data (the dip in mid-2021 and the rise in late 2022) but cannot "
            "anticipate individual monthly jumps."),
("h3", "CPI rate (series 3)"),
("h4", "B1. Train / test split"),
("code", "p1_16_B1"),
("h4", "B2. Forecasting with ARIMA(0,0,1) and with all combinations"),
("code", "p1_16_B2"),
("comment", "ARIMA(0,0,1) gives the lowest test RMSE (0.1195 percentage points) of the 4 combinations, again "
            "agreeing with the AIC selection; the constant-mean model gives 0.1320 (about 9 % worse). The MA(1) term "
            "captures the tendency of a large monthly change to be partly reversed in the next month."),

("h2", "1.7 Machine learning in SARIMA model forecasting"),
("p", "SARIMA(pO,dO,qO)(P,D,Q,m) adds seasonal terms with m = 12 and D = 0 to the optimal ARIMA orders. The same "
      "80/20 split and walk-forward procedure are used. P and Q are varied over 0, 1, 2; the combination "
      "(0,0,0,12) is the plain ARIMA model and is kept in the table only as a baseline."),
("h3", "CPI (series 1) - SARIMA(1,0,1)(P,0,Q,12)"),
("h4", "A1. Forecast with (P,D,Q,m) = (1,0,1,12)"),
("code", "p1_17_A1"),
("h4", "A2. Loop over P, Q = 0..2"),
("code", ["p1_17_func", "p1_17_A2"]),
("comment", "SARIMA(1,0,1)(1,0,1,12) gives RMSE 0.1168, worse than ARIMA(1,0,1) (0.1146). In the loop the best "
            "seasonal model is SARIMA(1,0,1)(0,0,1,12) with RMSE 0.1153, still slightly worse than the non-seasonal "
            "baseline, and models with more seasonal terms are worse (up to 0.126). This agrees with the ACF "
            "(autocorrelation at lag 12 is about 0.01) and the small calendar-month effects: the yearly seasonality "
            "of garment prices is too weak to be exploited, and the extra parameters only add estimation noise."),
("h3", "CPI rate (series 3) - SARIMA(0,0,1)(P,0,Q,12)"),
("h4", "B1. Forecast with (P,D,Q,m) = (1,0,1,12)"),
("code", "p1_17_B1"),
("h4", "B2. Loop over P, Q = 0..2"),
("code", "p1_17_B2"),
("comment", "SARIMA(0,0,1)(1,0,1,12) gives RMSE 0.1220 versus 0.1195 for ARIMA(0,0,1). The best seasonal model is "
            "SARIMA(0,0,1)(0,0,1,12) with RMSE 0.1196, practically identical to the plain ARIMA. Seasonal terms do "
            "not improve the forecast of the CPI rate either."),

("h2", "Part 1 conclusion"),
("p", "The Hanoi garment, footwear and hat CPI (2015-2022) fluctuates in a narrow range around 100.14 with no "
      "meaningful trend, weak seasonality (higher around Tet, lower in April) and shocks in 2018 and 2020 "
      "(COVID-19). ADF and KPSS tests show that both the CPI and the CPI rate are stationary, so d = 0. The ACF/PACF "
      "identify an AR(2)/ARMA structure for the CPI and an MA(1) structure for the CPI rate. The best models by "
      "AIC with stable (significant) parameters are ARIMA(1,0,1) for the CPI and ARIMA(0,0,1) for the CPI rate; "
      "the walk-forward train/test evaluation selects exactly the same models by RMSE (0.1146 and 0.1195), about 9 % "
      "better than a constant-mean forecast. Adding seasonal SARIMA terms with m = 12 does not reduce the RMSE, so "
      "the non-seasonal ARIMA models are recommended. The forecast for 2023 is a CPI of about 100.2 and a monthly "
      "CPI rate of about 0.02 %, with wide uncertainty."),

("pagebreak",),
("h1", "Part 2. Detecting anomalies and change points in time series of Asian economic data"),
("p", "Summary: Five annual indicators of Indonesia (1990-2021) are examined. The Z-score method flags only the "
      "1998 inflation (58 %). Isolation Forest flags extreme years in every series. PELT finds structural changes "
      "around 2010 for GDP, green GDP, FDI and inflation, and in 1996 and 2006 for military spending."),
("h2", "2.1 Introduction"),
("h3", "Methodology of anomaly and change point detection"),
("p", "An anomaly (outlier) is an observation that deviates strongly from the rest of the series; a change point is "
      "a time where the statistical properties of the series (mean, variance, distribution) change and stay "
      "changed. Three methods are used: (1) the Z-score method standardises each value, z = (x - mean) / std, and "
      "flags |z| > 3; it assumes an approximately normal, stationary series. (2) Isolation Forest (Liu, Ting and "
      "Zhou, 2008) builds random trees that split the data at random values; anomalies are isolated in fewer "
      "splits and get a lower score. The parameter contamination gives the expected share of anomalies (here 0.1, "
      "about 3 of 32 years). (3) Change point detection with the PELT algorithm (Killick et al., 2012) of the "
      "ruptures library finds the segmentation that minimises a cost (here the RBF kernel cost on the standardised "
      "series) plus a penalty (pen = 3) for each change point; each segment has at least 3 years."),
("h3", "Economic indicators"),
("bullet", "+ gdp - Gross Domestic Product: total value of final goods and services produced in a year (current USD)."),
("bullet", "+ ggdp - Green GDP: GDP adjusted for the depletion of natural resources and environmental damage (USD)."),
("bullet", "+ inf - inflation rate: annual percentage change of consumer prices (%)."),
("bullet", "+ fdi - foreign direct investment, net inflows (USD); negative values mean disinvestment by foreign investors."),
("bullet", "+ mil - government military expenditure as a percentage of GDP (%)."),
("h3", "Data array \"Data02_05_Indonesia_C.csv\""),
("p", "Annual data of Indonesia from 1990 to 2021 (32 years). ggdp is missing for 2020-2021 and mil for 1995; "
      "missing years are skipped (not imputed) for each series."),
("bullet", "+ Column 1: year"),
("bullet", "+ Column 2: country (Indonesia)"),
("bullet", "+ Column 3: ggdp = Green Gross Domestic Product"),
("bullet", "+ Column 4: mil = Government spending on military (% of GDP)"),
("bullet", "+ Column 5: inf = Inflation rate (%)"),
("bullet", "+ Column 6: fdi = Foreign direct investment (USD)"),
("bullet", "+ Column 7: gdp = Gross Domestic Product (USD)"),
("code", "p2_setup"),

("h2", "2.2 Detecting anomalies"),
("h3", "Z-Score Method (threshold = 3)"),
("h4", "A1. Series 1: ggdp"),
("code", ["p2_z_func", "p2_z_ggdp"]),
("comment", "No anomaly: the largest |z| is 1.89 (2019). Green GDP grows from 95 to 1,100 billion USD, so its mean "
            "and standard deviation are dominated by the trend and no single year is far from them. The 1998 crisis "
            "drop (200 to 86 billion USD) is not detected because the value is low but not extreme compared with "
            "the whole sample."),
("h4", "A2. Series 2: mil"),
("code", "p2_z_mil"),
("comment", "No anomaly. The highest value, 2.88 % in 1994, has z = 2.49 < 3. Military spending declines from "
            "about 2.5 % of GDP in the early 1990s to 0.6-0.9 % after 2006, so early years are the farthest from "
            "the mean but not beyond the threshold."),
("h4", "A3. Series 3: inf"),
("code", "p2_z_inf"),
("comment", "One anomaly: 1998 with inflation of 58.45 % (z = 5.05), caused by the Asian financial crisis and the "
            "collapse of the rupiah. The 1999 value (20.5 %) is also high but has z = 1.19 only, because the 1998 "
            "value itself inflates the standard deviation (masking effect)."),
("h4", "A4. Series 4: fdi"),
("code", "p2_z_fdi"),
("comment", "No anomaly: the maximum |z| is 1.72 (2014). The negative FDI of 1998-2001 (net outflows up to -4.55 "
            "billion USD in 2000) is economically abnormal but not extreme in z-score terms because of the strong "
            "upward trend after 2010."),
("h4", "A5. Series 5: gdp"),
("code", "p2_z_gdp"),
("comment", "No anomaly: the maximum |z| is 1.79 (2021). As for green GDP, the Z-score method is not suitable for a "
            "strongly trending series; the crisis of 1998 (GDP falling from 216 to 95 billion USD) is not detected."),

("h3", "Isolation Forest Method"),
("h4", "A1. Series 1: ggdp"),
("code", ["p2_if_func", "p2_if_ggdp"]),
("comment", "Isolation Forest flags 2009, 2010 and 2019. 2019 is the maximum (1,100 billion USD, lowest score "
            "-0.132). 2009 and 2010 lie in the sparse region created by the jump from 510 to 720 billion USD "
            "between them, so they are easy to isolate."),
("h4", "A2. Series 2: mil"),
("code", "p2_if_mil"),
("comment", "Flags 1994 (2.88 %, strongest, score -0.197), 1992 (2.43 %) and 2003 (1.50 %). The early 1990s are the "
            "high-spending period; 2003 is a local jump from 1.26 % (2002) to 1.50 %, the year of the military "
            "operation in Aceh."),
("h4", "A3. Series 3: inf"),
("code", "p2_if_inf"),
("comment", "Flags 1998 (58.45 %, score -0.305, by far the strongest), 1999 (20.48 %), 2006 (13.11 %) and 2021 "
            "(1.56 %, the lowest inflation). Unlike the Z-score method, Isolation Forest also detects the 1999 "
            "after-crisis inflation, since it does not depend on the mean and standard deviation."),
("h4", "A4. Series 4: fdi"),
("code", "p2_if_fdi"),
("comment", "Flags 2000 (-4.55 billion USD, the largest net outflow after the crisis), 2010 (15.3 billion USD, a "
            "jump from 4.9 billion in 2009), 2014 (25.1 billion, the maximum) and 2019 (25.0 billion). The scores "
            "are close to 0 (-0.04 to -0.001), so these anomalies are weak: they are mainly the extremes of the "
            "distribution."),
("h4", "A5. Series 5: gdp"),
("code", "p2_if_gdp"),
("comment", "Flags 2021 (1,190 billion USD, the maximum, score -0.111), 2019, 2010 and 2009. As for green GDP, "
            "Isolation Forest on raw values flags the largest values and the years around the 2009-2010 jump. For "
            "trending series a better input would be growth rates, which would reveal the 1998 collapse."),

("h2", "2.3 Change Point detection"),
("h4", "A1. Series 1: ggdp"),
("code", ["p2_cp_func", "p2_cp_ggdp"]),
("comment", "One change point in 2010: the mean green GDP rises from 220 billion USD (1990-2009) to 901 billion USD "
            "(2010-2019). The level shift corresponds to the jump from 510 to 720 billion USD in 2010, reflecting "
            "fast growth after the 2008-2009 global financial crisis, the commodity boom and the appreciation of "
            "the rupiah."),
("h4", "A2. Series 2: mil"),
("code", "p2_cp_mil"),
("comment", "Two change points, in 1996 and 2006, give three regimes: 2.58 % of GDP (1990-1994), 1.24 % (1996-2005) "
            "and 0.73 % (2006-2021). Military spending as a share of GDP fell in steps: the economy grew much faster "
            "than the defence budget."),
("h4", "A3. Series 3: inf"),
("code", "p2_cp_inf"),
("comment", "One change point in 2010: mean inflation falls from 11.5 % (1990-2009) to 4.2 % (2010-2021), a move to "
            "a low and stable inflation regime under Bank Indonesia's inflation-targeting framework. The 1998 spike "
            "is not a change point: it is a single-year anomaly and inflation returned to its previous level, which "
            "illustrates the difference between an anomaly and a change point."),
("h4", "A4. Series 4: fdi"),
("code", "p2_cp_fdi"),
("comment", "One change point in 2010: mean FDI inflows rise from 2.5 billion USD (1990-2009, including the negative "
            "years after the crisis) to 19.5 billion USD (2010-2021). Indonesia became a major destination of "
            "foreign investment after 2010."),
("h4", "A5. Series 5: gdp"),
("code", "p2_cp_gdp"),
("comment", "One change point in 2010: the mean GDP rises from 236 billion USD (1990-2009) to 966 billion USD "
            "(2010-2021). The same break year as green GDP, FDI and inflation suggests a common structural change in "
            "the Indonesian economy around 2010."),

("h2", "Part 2 conclusion"),
("p", "For Indonesia 1990-2021, the Z-score method (|z| > 3) detects only one anomaly, the 58 % inflation of 1998 "
      "(Asian financial crisis); it is not suitable for trending series such as GDP, green GDP and FDI and suffers "
      "from masking. Isolation Forest is more flexible: it detects 1998-1999 inflation, the 2000 FDI outflow and the "
      "high military spending of 1992-1994, but on raw trending data it mostly flags the extreme (latest) values and "
      "its number of anomalies is fixed by the contamination parameter. Change point detection with PELT shows a "
      "common structural break in 2010 for GDP, green GDP, FDI (level up) and inflation (level down), and a "
      "step-wise decline of military spending in 1996 and 2006. Anomaly detection and change point detection are "
      "complementary: the 1998 crisis is a short shock (anomaly), while 2010 marks a lasting change of regime."),

("pagebreak",),
("h1", "Reference"),
("p", "1. Box, G. E. P., Jenkins, G. M., Reinsel, G. C. and Ljung, G. M. (2015). Time Series Analysis: "
      "Forecasting and Control, 5th ed. Wiley."),
("p", "2. Hyndman, R. J. and Athanasopoulos, G. (2021). Forecasting: Principles and Practice, 3rd ed. OTexts. "
      "https://otexts.com/fpp3/"),
("p", "3. Dickey, D. A. and Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series "
      "with a unit root. Journal of the American Statistical Association, 74(366), 427-431."),
("p", "4. Kwiatkowski, D., Phillips, P. C. B., Schmidt, P. and Shin, Y. (1992). Testing the null hypothesis of "
      "stationarity against the alternative of a unit root. Journal of Econometrics, 54, 159-178."),
("p", "5. Liu, F. T., Ting, K. M. and Zhou, Z.-H. (2008). Isolation Forest. Proceedings of the IEEE International "
      "Conference on Data Mining, 413-422."),
("p", "6. Killick, R., Fearnhead, P. and Eckley, I. A. (2012). Optimal detection of changepoints with a linear "
      "computational cost. Journal of the American Statistical Association, 107(500), 1590-1598."),
("p", "7. Truong, C., Oudre, L. and Vayatis, N. (2020). Selective review of offline change point detection methods. "
      "Signal Processing, 167. (ruptures library)"),
("p", "8. Seabold, S. and Perktold, J. (2010). statsmodels: Econometric and statistical modeling with Python. "
      "Proceedings of the 9th Python in Science Conference."),
("p", "9. Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning "
      "Research, 12, 2825-2830."),
("p", "10. General Statistics Office of Vietnam. Consumer Price Index methodology and monthly CPI releases. "
      "https://www.gso.gov.vn"),
("p", "11. World Bank. World Development Indicators. https://databank.worldbank.org"),
("p", "12. Course notes: Time Series Analysis - Machine Learning with Python, USTH ICT Department, 2026."),
]
