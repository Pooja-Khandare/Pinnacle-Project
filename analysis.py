import matplotlib.pyplot as plt
import seaborn as sns

# Set style for professional charts
sns.set_theme(style="whitegrid")

# Group data by customer for analysis
customer_summary = clean_df.groupby('Customer').agg(
    Frequency=('Invoice_No', 'nunique'),
    Total_Sales=('Total_Price', 'sum'),
    Mean_Spend=('Total_Price', 'mean'),
    Median_Spend=('Total_Price', 'median')
).reset_index()

# 1. Customer vs Total Sales Chart
top_customers_sales = customer_summary.sort_values(by='Total_Sales', ascending=False).head(10)
plt.figure(figsize=(10, 5))
sns.barplot(data=top_customers_sales, x='Customer', y='Total_Sales', palette='Blues_d')
plt.title('Top 10 Customers vs Total Sales Figure')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('customer_vs_sales.png')
plt.close()

# 2. Customer vs Purchase Frequency Chart
top_customers_freq = customer_summary.sort_values(by='Frequency', ascending=False).head(10)
plt.figure(figsize=(10, 5))
sns.barplot(data=top_customers_freq, x='Customer', y='Frequency', palette='Greens_d')
plt.title('Top 10 Customers vs Purchase Frequency')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('customer_vs_frequency.png')
plt.close()

print("Charts generated and saved successfully!")