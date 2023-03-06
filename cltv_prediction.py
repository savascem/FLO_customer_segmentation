# ----------------------------------------------------------------------------------------------------------
# TODO 1) Data Preparation

# import
import pandas as pd
from pandas import Timestamp, Timedelta
import datetime as dt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns', 20)
df_ = pd.read_csv("flo.csv")
df = df_.copy()
df.info()
df.describe().T

# outlier thresholds
def outlier_thresholds(dataframe, variable):
    QRI1 = dataframe[variable].quantile(0.01)
    QRI3 = dataframe[variable].quantile(0.99)
    QRI = QRI3 - QRI1
    up_limit = QRI3 + 1.5 * QRI
    low_limit = QRI1 - 1.5 * QRI
    return round(low_limit), round(up_limit)

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

for col in df.columns:
    if (df[col].dtype == float) | (df[col].dtype == int):
        replace_with_thresholds(df, col)

# total omnichannel variables
df["omnichannel_total_order"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["omnichannel_total_price"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

# date variables convert to DateTime type
df["last_order_date"] = pd.to_datetime(df["last_order_date"])
df["first_order_date"] = pd.to_datetime(df["first_order_date"])
df["last_order_date_online"] = pd.to_datetime(df["last_order_date_online"])
df["last_order_date_offline"] = pd.to_datetime(df["last_order_date_offline"])

# ----------------------------------------------------------------------------------------------------------
# TODO 2) CLTV Data Structure

# analysis date
analysis_date = df.last_order_date.max() + Timedelta(days=2)

# recency_cltv_weekly
df["recency_cltv_weekly"] = (df["last_order_date"] - df["first_order_date"]).dt.days / 7
df["recency_cltv_weekly"] = df["recency_cltv_weekly"].apply(lambda x: f"{x:.0f} weeks")

# T_weekly
df["T_weekly"] = (analysis_date - df["first_order_date"]).dt.days / 7
df["T_weekly"] = df["T_weekly"].apply(lambda x: f"{x:.0f} weeks")

# frequency
df["frequency"] = df["omnichannel_total_order"]

# monetary_cltv_avg
df["monetary_cltv_avg"] = df["omnichannel_total_price"] / df["frequency"]

# Create new dataframe
cltv_df = df[["master_id", "recency_cltv_weekly", "T_weekly", "frequency", "monetary_cltv_avg"]]
cltv_df.columns = ["customer_id", "recency_cltv_weekly", "T_weekly", "frequency", "monetary_cltv_avg"]

# ----------------------------------------------------------------------------------------------------------
# TODO 3) BG/NBD & Gamma-Gamma Models, Predict CLTV for 6 Months

# date objects to integer
cltv_df["recency_cltv_weekly"] = cltv_df["recency_cltv_weekly"].str.extract(r"(\d+)").astype(int).to_numpy().squeeze()
cltv_df["T_weekly"] = cltv_df["T_weekly"].str.extract(r"(\d+)").astype(int).to_numpy().squeeze()

# BG/NBD Model
bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(
    cltv_df["frequency"],
    cltv_df["recency_cltv_weekly"],
    cltv_df["T_weekly"],
)

# Gamma-Gamma Model
ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df["frequency"], cltv_df["monetary_cltv_avg"])

# CLTV calculate
cltv_df["cltv"] = ggf.customer_lifetime_value(bgf,
                                   cltv_df['frequency'],
                                   cltv_df['recency_cltv_weekly'],
                                   cltv_df['T_weekly'],
                                   cltv_df['monetary_cltv_avg'],
                                   time=6,  # 6 months
                                   freq="W",
                                   discount_rate=0.01)

# CLTV scaling with MinMaxScaler()
scaler = MinMaxScaler(feature_range=(0, 100))
cltv_df["scaled_cltv"] = scaler.fit_transform(cltv_df[["cltv"]])

# ----------------------------------------------------------------------------------------------------------
# TODO 4) CLTV segmentation

# segmentation for 6 Months
cltv_df["cltv_segment"] = pd.qcut(cltv_df["cltv"], 4, labels=["D", "C", "B", "A"])
cltv_df.sort_values(by="cltv", ascending=False).head(50)

# analysis
cltv_df.groupby("cltv_segment").agg({"frequency":["count", "mean", "sum", "median", "std"]})
cltv_df.groupby("cltv_segment").agg({"recency_cltv_weekly":["count", "mean", "sum", "median", "std"]})
cltv_df.groupby("cltv_segment").agg({"T_weekly":["count", "mean", "sum", "median", "std"]})
cltv_df.groupby("cltv_segment").agg({"monetary_cltv_avg":["count", "mean", "sum", "median", "std"]})

# Result: The fact that the values of 'T_weekly' and 'recency_cltv_weekly'
# are close to each other and their values are low has created a positive impact.
# As a conclusion, we can infer that the company should focus on new customers who shop more frequently.
