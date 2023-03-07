# Explanation:

This dataset has been used in the 'Data Scientist' bootcamp I took from the 'miuul' company. The dataset will never be shared by me. Thank you for your understanding.

# Dataset 

FLO is one of the biggest companies in Turkiye.The dataset consists of information obtained from the past shopping behaviors of customers who shopped both online and offline (OmniChannel) in their last transactions in 2020-2021 at FLO.

## Variables

master_id                           :   customer ID

order_channel                       :   The Platform for Shopping (Android, ios, Desktop, Mobile)

last_order_channel                  :   The platform where the last purchase was made

first_order_date                    :   First Order Date

last_order_date                     :   Last Order Date

last_order_date_online              :   Date of the customer's last purchase on the online platform

last_order_date_offline             :   Date of the customer's last offline purchase

order_num_total_ever_online         :   Total number of purchases made by the customer on the online platform

order_num_total_ever_offline        :   Total number of offline purchases made by the customer

customer_value_total_ever_offline   :   Total price paid by the customer for offline shopping

customer_value_total_ever_online    :   Total price paid by the customer for online shopping

interested_in_categories_12         :   List of categories in which the customer has shopped in the last 12 months

# RFM Metrics Calculating & Segmentation 

In this file, the 'RFM' metrics of all customers in the dataset were calculated and their segments were determined.

The segments were created according to the table below:

https://miro.medium.com/v2/resize:fit:720/format:webp/1*TjJt4rUiBtXLAF84--V-Cg.png

## The TODO list followed in this file is as follows:

### 1) Data Understanding & Preparing

1.1. import

1.2. read csv file

1.3. data understanding

1.4. total omnichannel variables

1.5. date variables convert to DateTime type

1.6. groupby => order_channel - omnichannel_total_order & omnichannel_total_price

1.7. omnichannel_total_price top 10

1.8. omnichannel_total_order top 10

### 2) Calculating RFM metrics

2.1. "recency", "frequency", "monetary" variables  calculating & creating

2.2. rfm DataFrame creating

### 3) Calculating RF and RFM Scores

3.1. metrics score

3.2. rfm score

3.3. rf score

### 4) Create segments with the help of 'RF' scores.

4.1. segmentation map

4.2. creating segments

### 5) Analyze the recency, frequency, and monetary averages of the segments.

5.1. Analysis of the segments by product categories

### 6) Exporting the file

6.1. Exporting function creating

# Customer Lifetime Value Prediction (CLTV)

In this file, the 'CLTV' of all customers in the dataset were calculated with the help BG/NBD Model & Gamma-Gamma Submodel.

## The TODO list followed in this file is as follows:

### 1) Data Preparing

1.1. imports

1.2. 'outlier thresholds' and 'replace_with_thresholds' functions were created to replace outliers with thresholds.

1.3. total omnichannel variables

1.4. date variables convert to DateTime type

### 2) CLTV Data Structure

2.1. analysis date

2.2. customer_id, recency_cltv_weekly, T_weekly, frequency ve ,monetary_cltv_avg variables creating

2.3. create new dataframe

### 3) BG/NBD & Gamma-Gamma Models, Predict CLTV for 6 Months

3.1. date objects to integer

3.2. BG/NBD Model

3.3. Gamma-Gamma Model

3.4. CLTV calculate for 6 months

3.5. CLTV scaling with MinMaxScaler()

### 4) CLTV segmentation

4.1. segmentation for 6 Months

4.2. analysis

