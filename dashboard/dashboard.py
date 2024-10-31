import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


# helper function
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby(by="product_category_name_english").product_id.count().rename("product_qty").sort_values(ascending=False).reset_index()
    
    return sum_order_items_df

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bycity_df

def create_bystate_df(df):
        bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
        bystate_df.rename(columns={
            "customer_id": "customer_count"
        }, inplace=True)
        most_state_order = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
        bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

        return bystate_df, most_state_order
    
def create_order_status_df(df):
        order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
        # most_status_order = order_status_df.idxmax()

        return order_status_df
    
def create_by_paymentmethod_df(df):
    by_payment_type_df = df.groupby(by="payment_type").order_id.nunique().sort_values(ascending=False).reset_index()

    by_payment_type_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)

    return by_payment_type_df


    
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule="M", on="order_purchase_timestamp").agg({
    "order_id": "nunique",
    "price": "sum"
    })

    monthly_orders_df.index = monthly_orders_df.index.strftime("%Y-%m")
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return monthly_orders_df

def create_review_score_df(df):
    review_scores = df['review_score'].value_counts().sort_values(ascending=False)

    return review_scores

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df


# Load berkas all_data.csv sebagai sebuah DataFrame
# all_df = pd.read_csv("dashboard/all_data.csv")
all_df = pd.read_csv("https://raw.githubusercontent.com/VanessaLeo24/ecommerce-data-analysis/refs/heads/main/dashboard/all_data.csv")


# Memastikan kolom order_purchase_timestamp dsb memiliki tipe datetime
datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
    
# Membuat komponen filter dengan widget date_input
min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()


# Membuat sidebar
with st.sidebar:
    
     st.title("Vanessa Leonora")
     
    # Menambahkan logo perusahaan)
     st.image("dashboard/adorable_cat.png", use_column_width=True)
 
    
     
     st.markdown("---")  # Garis pemisah
     
    
     
     # Mengambil start_date dan end_date dari widget date_input
     # try except digunakan untuk menghandle jika user tidak memilih tanggal
     
    #  try:
    #     start_date, end_date = st.date_input(
    #             label="Rentang Waktu",
    #             min_value=min_date,
    #             max_value=max_date,
    #             value=[min_date, max_date]
    #         )
            
    #  except:
    #         start_date = min_date
    #         end_date = max_date
            
            
        
     
    # #  Start_date dan end_date digunakan untuk memfilter DataFrame dan disimpan dalam main_df
    #  main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
    #             (all_df["order_purchase_timestamp"] <= str(end_date))]
     
     
       # Retrieving start_date and end_date from date_input
     start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
     )

     try:
    # Filtering DataFrame based on the selected date range
        main_df = all_df[
        (all_df["order_purchase_timestamp"] >= str(start_date)) & 
        (all_df["order_purchase_timestamp"] <= str(end_date))
    ]
    
     except Exception as e:
        st.error(f"An error occurred while filtering the data: {e}")
        main_df = None  # Optionally set main_df to None or handle as needed
     
     
     # Memanggil semua helper function yang telah dibuat sebelumnya
     sum_order_items_df = create_sum_order_items_df(main_df)
     bycity_df = create_bycity_df(main_df)
     bystate_df, most_state_order = create_bystate_df(main_df)
     order_status_df = create_order_status_df(main_df)
     by_payment_type_df = create_by_paymentmethod_df(main_df)
     monthly_orders_df = create_monthly_orders_df(main_df)
     review_score_df = create_review_score_df(main_df)
     rfm_df = create_rfm_df(main_df)
     
     
st.header("E-commerce Data Analysis Dashboard :chart_with_upwards_trend:")

st.markdown("---")  # Garis pemisah

# Menampilkan produk terlaris dan paling tidak laris
st.subheader("Best and Worst Performing Products")
     
try:
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

        colors = ["#FFA62F", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

        sns.barplot(x="product_qty", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
        ax[0].set_ylabel(None)
        ax[0].set_xlabel(None)
        ax[0].set_title("Best Performing Product", loc="center", fontsize=15)
        ax[0].tick_params(axis ='y', labelsize=12)

        sns.barplot(x="product_qty", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_qty", ascending=True).head(5), palette=colors, ax=ax[1])
        ax[1].set_ylabel(None)
        ax[1].set_xlabel(None)
        ax[1].invert_xaxis()
        ax[1].yaxis.set_label_position("right")
        ax[1].yaxis.tick_right()
        ax[1].set_title("Worst Performing Product", loc="center", fontsize=15)
        ax[1].tick_params(axis='y', labelsize=12)

        st.pyplot(fig)
        
except Exception:
        st.error(f"An error occurred while plotting the data, please try another date range")

st.markdown("---")  # Garis pemisah


# Menampilkan demografis pelanggan
st.subheader("Customer Demographics")

# Menampilkan jumlah pelanggan berdasarkan kota, negara bagian, dan status pesanan
tab1, tab2, tab3 = st.tabs(["City", "State", "Order Status"])


# Berdasarkan kota
with tab1:

     try:
        most_common_city = bycity_df.loc[bycity_df['customer_count'].idxmax(), 'customer_city']
        
        fig, ax = plt.subplots(figsize=(20, 10))
        colors = ["#FFA62F", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        
        st.markdown(f"Majority of customers are from the city of **{most_common_city}**")
        
        sns.barplot(
            x="customer_count", 
            y="customer_city",
            data=bycity_df.sort_values(by="customer_count", ascending=False).head(10),
            palette=colors,
            ax=ax
        )
        ax.set_title("Number of Customer by Cities", loc="center", fontsize=30)
        ax.set_ylabel("City", fontsize=20, labelpad=10)
        ax.set_xlabel("Total Customers", fontsize=20, labelpad=10)
        ax.xaxis.set_label_coords(0.5, -0.1) # Set x-axis label position
        ax.tick_params(axis='y', labelsize=20)
        ax.tick_params(axis='x', labelsize=15)
        
        st.pyplot(fig)
        
     except Exception:
        st.error(f"An error occurred while plotting the data, please try another date range")

        
# Berdasarkan negara bagian
with tab2:
    
     try:
        most_state_order = bystate_df.customer_state.value_counts().index[0]
        most_common_state = bystate_df.loc[bycity_df['customer_count'].idxmax(), 'customer_state']
        st.markdown(f"Majority of customers are from the state of **{most_common_state}**")

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x=bystate_df.customer_state.value_counts().index,
                    y=bystate_df.customer_count.values, 
                    data=bystate_df,
                    palette=["#FFA62F" if state == most_state_order else "#D3D3D3" for state in bystate_df.customer_state],
                        )
        

        plt.title("Number of Customer by States", fontsize=15)
        plt.xlabel("State")
        plt.ylabel("Total Customers")
        ax.xaxis.set_label_coords(0.5, -0.1) # Set x-axis label position
        plt.xticks(fontsize=12)
        st.pyplot(fig)
    
     except Exception:
        st.error(f"An error occurred while plotting the data, please try another date range")

        
# Berdasarkan status pesanan
with tab3:
    
     try:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        st.markdown(f"Majority of orders are in the **{order_status_df.idxmax()}** status")
        
        order_status_df.plot(kind='bar', color=['#FFA62F', '#D3D3D3', '#D3D3D3', '#D3D3D3', '#D3D3D3'])


        plt.title("Number of Customers by Order Status", loc="center", fontsize=15)
        plt.ylabel("Total Customers", fontsize=12)
        plt.xlabel("Order Status", fontsize=12)
        ax.xaxis.set_label_coords(0.5, -0.3) # Set x-axis label position
        ax.yaxis.set_label_coords(-0.1, 0.5) # Set y-axis label position
        plt.tick_params(axis='x', labelsize=12)

        st.pyplot(fig)
        
     except Exception:
        st.error(f"An error occurred while plotting the data, please try another date range")

    

st.markdown("---")  # Garis pemisah

# Menampilkan metode pembayaran yang paling banyak digunakan
st.subheader("Payment Method Analysis")

try :
    colors_payment= ["#FFA62F", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3"]

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(
        y = "order_count",
        x = "payment_type",
        data = by_payment_type_df,
        palette=colors_payment
    )

    plt.title("Number of Orders by Payment Type", loc="center", fontsize=15)
    plt.ylabel("Total Orders", fontsize=12)
    plt.xlabel("Payment Type", fontsize=12)
    plt.tick_params(axis='y', labelsize=12)

    st.pyplot(fig)

except Exception:
        st.error(f"An error occurred while plotting the data, please try another date range")
        

st.markdown("---")  # Garis pemisah

st.subheader("Monthly Orders and Revenue")

try :

    col1, col2 = st.columns(2)

    with col1:
        total_orders = monthly_orders_df.order_count.sum()
        st.metric("Total Orders", value=total_orders)
        
    with col2:
        total_revenue = format_currency(monthly_orders_df.revenue.sum(),  "AUD", locale='es_CO')
        st.metric("Total Revenue", value=total_revenue)
        
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        monthly_orders_df["order_purchase_timestamp"],
        monthly_orders_df["order_count"],
        marker="o",
        linewidth=2,
        color="#FFA62F"
    )

    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15, rotation=90)
    ax.set_title("Number of Orders per Month (2016-2018)", fontsize=20)


    st.pyplot(fig)


    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        monthly_orders_df["order_purchase_timestamp"],
        monthly_orders_df["revenue"],
        marker="o",
        linewidth=2,
        color="#FFA62F"
    )

    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15, rotation=90)
    ax.set_title("Total Revenue per Month (2016-2018)", fontsize=20)

    st.pyplot(fig)
    
except Exception:
        st.error(f"An error occurred while plotting the data, please try another date range")

st.markdown("---")  # Garis pemisah

# Menampilkan skor ulasan
st.subheader("Review Rating Analysis")
st.markdown("The most common review score is **{most_review_score}**")

try :

    most_review_score = review_score_df.idxmax()

    service_review_colors = ["#FFA62F" if score == most_review_score else "#D3D3D3" for score in review_score_df.index]

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(
        x=review_score_df.index,
        y=review_score_df.values,
        order=review_score_df.index,
        palette=service_review_colors
    )

    plt.title("Customer Rating For Service", loc="center", fontsize=15)
    plt.ylabel("Total Customers", fontsize=12)
    plt.xlabel("Rating Score", fontsize=12)
    plt.tick_params(axis='y', labelsize=12)
    ax.xaxis.set_label_coords(0.5, -0.1) # Set x-axis label position
    ax.yaxis.set_label_coords(-0.1, 0.5) # Set y-axis label position

    st.pyplot(fig)
    
except Exception:
    st.error(f"An error occurred while plotting the data, please try another date range")

st.markdown("---")  # Garis pemisah

# Menampilkan RFM Analysis
st.subheader("Best Customers Based on RFM Analysis")

try :
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency", value=avg_recency)
        
    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)

    with col3:
        avg_monetary = format_currency(rfm_df.monetary.mean(),  "AUD", locale='es_CO')
        st.metric("Average Monetary", value=avg_monetary)



    fig, ax = plt.subplots(nrows=1, ncols=3,figsize=(45, 12))
    colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

    # Top 5 customers by Recency
    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])   
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("By Recency", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=30)
    ax[0].tick_params(axis='x', labelsize=35)
    ax[0].tick_params(axis='x', labelsize=14, rotation=30)
    for label in ax[0].get_xticklabels():
        label.set_ha('right')



    # Top 5 customers by Frequency
    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title("By Frequency", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=30)
    ax[1].tick_params(axis='x', labelsize=35)
    ax[1].tick_params(axis='x', labelsize=14, rotation=30)
    for label in ax[1].get_xticklabels():
        label.set_ha('right')
        


    # Top 5 customers by Monetary
    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title("By Monetary", loc="center", fontsize=50)
    ax[2].tick_params(axis='y', labelsize=30)
    ax[2].tick_params(axis='x', labelsize=35)
    ax[2].tick_params(axis='x', labelsize=14, rotation=30)
    for label in ax[2].get_xticklabels():
        label.set_ha('right')


    st.pyplot(fig)

except Exception:
    st.error(f"An error occurred while plotting the data, please try another date range")

st.markdown("---")  # Garis pemisah

# Centering and change font size of the caption
s = f"<p style='font-size:20px;text-align:center'>{'Copyright (c) Vanessa Leonora 2024'}</p>"
st.caption(s, unsafe_allow_html=True)  






