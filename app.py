##DASHBOARD
import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Executive Live Dashboard", layout="wide", initial_sidebar_state="expanded")

# Dashboard Title
st.title("📊 Dabang Executive Dashboard")
st.markdown("Real-time automated analytics stream for search queries, hits, and revenue.")

# Sidebar Filters
st.sidebar.header("Dashboard Filters")
selected_time = st.sidebar.selectbox("Select Time Period", ["All", "Morning", "Afternoon", "Evening", "Night"])

# Data loading with ISO Codes for mapping
data = {
    'Time of day': ['Morning', 'Afternoon', 'Evening', 'Night', 'Morning', 'Afternoon', 'Evening', 'Night'],
    'Location': ['Michigan', 'Chicago', 'London', 'Pennsylvania', 'Ontario', 'Alaska', 'Missouri', 'Kentucky'],
    'ISO_Code': ['US', 'US', 'GB', 'US', 'CA', 'US', 'US', 'US'],
    'Hits': [443000, 184100, 200500, 254200, 330000, 119500, 93900, 107900],
    'Related Searches': [22, 160, 141, 105, 13, 119, 132, 142],
    'Revenue': [4120, 13800, 10632, 7743, 4920, 9538, 11629, 12867]
}
df_dash = pd.DataFrame(data)

if selected_time != "All":
    df_dash = df_dash[df_dash['Time of day'] == selected_time]

# Top KPI Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Hits", value=f"{df_dash['Hits'].sum():,}", delta="+12% from yesterday")
with col2:
    st.metric(label="Related Searches", value=f"{df_dash['Related Searches'].sum():,}", delta="+5.2% from yesterday")
with col3:
    st.metric(label="Total Revenue", value=f"${df_dash['Revenue'].sum():,}", delta="+8.4% from yesterday")
with col4:
    st.metric(label="Active Locations", value=f"{df_dash['Location'].nunique()}", delta="Live Stream Active")

st.markdown("---")

# Charts Layout
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Total Revenue / Hits by Location")
    fig_bar = px.bar(df_dash, x='Location', y='Hits', color='Time of day', barmode='group', template='plotly_white')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Visitor Insights & Trends")
    fig_line = px.line(df_dash, x='Location', y='Related Searches', markers=True, template='plotly_white')
    st.plotly_chart(fig_line, use_container_width=True)

# Geo Map & Table
col_map, col_table = st.columns(2)
with col_map:
    st.subheader("Sales Mapping by Country / State")
    # Fixed to use dynamic column matching filtered dataframe length
    fig_scatter = px.scatter_geo(df_dash, locations='ISO_Code', size='Hits', color='Location', template='plotly_white')
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_table:
    st.subheader("Top Performing Search Keywords")
    top_products = pd.DataFrame({
        'Name': ['Smartphone', 'Laptop', 'Washing Machine', 'Fridge'],
        'Popularity': [92, 85, 78, 65],
        'Sales': ['2,400', '1,850', '1,200', '950']
    })
    st.dataframe(top_products, use_container_width=True)