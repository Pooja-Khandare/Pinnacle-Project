import pandas as pd
import streamlit as st
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Hotel Business Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dashboard Title
st.title("🏨 Hotel Business & Customer Revenue Executive Dashboard")
st.markdown(
    "Real-time analytics, revenue distribution, and statistical metrics based on hotel customer data."
)

# Load Excel Data
file_path = "Hotel Business Analysis.xlsx"
df = pd.read_excel(file_path, sheet_name=0, skiprows=4)
df_clean = df.dropna(subset=["Customer ID"]).copy()

# Map room categories to budgets and calculate Revenue
cat_mapping = {
    "A": "Budget A",
    "B": "Budget B",
    "C": "Budget C",
    "D": "Budget D",
    "E": "Budget E",
    "F": "Budget F",
    "G": "Budget G",
}

def calculate_revenue(row):
    cat = row["Rooms Category Purchased"]
    col = cat_mapping.get(cat, "Budget A")
    return row[col] * row["No. of Days"]

df_clean["Total_Revenue"] = df_clean.apply(calculate_revenue, axis=1)

# Sidebar Filters
st.sidebar.header("Dashboard Filters")
selected_month = st.sidebar.selectbox(
    "Select Month", options=["All"] + list(df_clean["Month"].unique())
)

if selected_month != "All":
    filtered_df = df_clean[df_clean["Month"] == selected_month]
else:
    filtered_df = df_clean

# Top KPI Cards
total_rev = filtered_df["Total_Revenue"].sum()
max_rev = filtered_df.groupby("Customer ID")["Total_Revenue"].sum().max()
min_rev = filtered_df.groupby("Customer ID")["Total_Revenue"].sum().min()
avg_rev = filtered_df.groupby("Customer ID")["Total_Revenue"].sum().mean()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Revenue", value=f"₹ {total_rev:,.2f}")
with col2:
    st.metric(label="Max Customer Revenue", value=f"₹ {max_rev:,.2f}")
with col3:
    st.metric(label="Min Customer Revenue", value=f"₹ {min_rev:,.2f}")
with col4:
    st.metric(label="Average Customer Revenue", value=f"₹ {avg_rev:,.2f}")

st.markdown("---")

# Charts Layout
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top Customers by Total Revenue")
    cust_rev = (
        filtered_df.groupby("Customer ID")["Total_Revenue"]
        .sum()
        .reset_index()
        .sort_values(by="Total_Revenue", ascending=False)
        .head(10)
    )
    fig_bar = px.bar(
        cust_rev,
        x="Customer ID",
        y="Total_Revenue",
        color="Total_Revenue",
        template="plotly_white",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Rooms Category Distribution")
    cat_counts = (
        filtered_df["Rooms Category Purchased"].value_counts().reset_index()
    )
    cat_counts.columns = ["Category", "Count"]
    fig_pie = px.pie(
        cat_counts,
        names="Category",
        values="Count",
        hole=0.4,
        template="plotly_white",
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Detailed Customer Revenue Table
st.subheader("📊 Customer Revenue Breakdown & Statistical Overview")
customer_summary = (
    filtered_df.groupby("Customer ID")["Total_Revenue"]
    .sum()
    .reset_index()
    .sort_values(by="Total_Revenue", ascending=False)
)
st.dataframe(customer_summary, use_container_width=True)