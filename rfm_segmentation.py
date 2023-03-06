# ----------------------------------------------------------------------------------------------------------
# TODO 1) Data Understanding & Preparing

# import
import pandas as pd
import numpy as np
import datetime
from pandas import Timestamp, Timedelta
pd.set_option('display.max_columns', 20)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# read csv file
df_ = pd.read_csv("flo.csv")
df = df_.copy()

# data understanding
df.head(10)
df.columns
df.shape
df.describe()
df.nunique()
df.isnull().sum()
df.info()

# total omnichannel variables
df["omnichannel_total_order"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["omnichannel_total_price"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

# date variables convert to DateTime type
df["last_order_date"] = pd.to_datetime(df["last_order_date"])
df["first_order_date"] = pd.to_datetime(df["first_order_date"])
df["last_order_date_online"] = pd.to_datetime(df["last_order_date_online"])
df["last_order_date_offline"] = pd.to_datetime(df["last_order_date_offline"])

# groupby => order_channel - omnichannel_total_order & omnichannel_total_price
df.groupby("order_channel").agg({
                                 "omnichannel_total_order": "sum",
                                 "omnichannel_total_price": "sum",
                                 })

# omnichannel_total_price top 10
df[["master_id", "omnichannel_total_price"]].sort_values("omnichannel_total_price",ascending=False).head(10)

# omnichannel_total_order top 10
df[["master_id", "omnichannel_total_order"]].sort_values("omnichannel_total_order",ascending=False).head(10)

# ----------------------------------------------------------------------------------------------------------
# TODO 2) Calculating RFM metrics

analysis_date = df.last_order_date.max() + Timedelta(days=2)

# recency = analysis_date - last_order_date
# frequency = df["omnichannel_total_order"]
# monetary = df["omnichannel_total_price"]
df["recency"] = analysis_date - df["last_order_date"]

# rfm DataFrame
rfm = df[["master_id", "recency", "omnichannel_total_order", "omnichannel_total_price"]]
rfm.columns = ["master_id", "recency", "frequency", "monetary"]

# TODO 3) Calculating RF and RFM Scores

# metrics score
rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

# rfm score
rfm["RFM_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str) + rfm["monetary_score"].astype(str)

# rf score
rfm["RF_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)

# ----------------------------------------------------------------------------------------------------------
# TODO 4) Create segments with the help of 'RF' scores.

# segmentation map
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm["segment"] = rfm["RF_SCORE"].replace(seg_map, regex=True)

# ----------------------------------------------------------------------------------------------------------
# TODO 5) Analyze the recency, frequency, and monetary averages of the segments.

rfm.describe()
rfm.sort_values("frequency", ascending=False)
rfm["monetary_div_frequency"] = rfm["monetary"] / rfm["frequency"]
rfm["categories"] = df["interested_in_categories_12"]

rfm.groupby("categories").agg({"frequency": ["sum", "count"],
                               "monetary": ["sum", "mean"]})
# The 'AKTIFSPOR' category appears to be at the top
# in terms of the 'frequency' and 'monetary' variables.

# ----------------------------------------------------------------------------------------------------------
# TODO 6) Exporting the file

def select_categories(dataframe, categories, file=False):

    dataframe[f"include_{categories}"] = np.nan

    for i in range(len(dataframe)):
        if categories in rfm["categories"].iloc[i]:
            dataframe[f"include_{categories}"].loc[i] = 1
        else:
            dataframe[f"include_{categories}"].loc[i] = 0

    if file:
        segmentType = input("--------------------------------------------------------------------\n"
                            "The customer types you can choose from are,\n"
                            "{'hibernating' | 'at_Risk' | 'cant_loose' | 'champions'\n"
                            "'need_attention' | 'loyal_customers' | 'promising' | 'new_customers'\n"
                            "'potential_loyalists' | 'about_to_sleep'}\n"
                            "Please make your choice:\n"
                            "--------------------------------------------------------------------")

        categories = rfm[(rfm["segment"] == segmentType) & (rfm[f"include_{categories}"] == 1)]

        fileType = input("--------------------------------------------------------------------\n"
                         "The file types you can choose from are,\n"
                         "{ 'csv' | 'xml' | 'excel' | 'sql' | 'html' }\n"
                         "Please make your choice:\n"
                         "--------------------------------------------------------------------")
        categories["master_id"].to_csv(f"{segmentType}.{fileType}")

    return rfm

select_categories(rfm, "KADIN", file=True)
