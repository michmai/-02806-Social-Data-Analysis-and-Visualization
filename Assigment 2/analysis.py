import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import plotly.express as px

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv(
    'Police_Department_Incident_Reports_Historical_Combined.csv',
    low_memory=False
)

# -------------------------------
# CLEAN DATA
# -------------------------------

# Convert date
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])

# Fix coordinates (convert from string with comma → float)
df['Latitude'] = (
    df['Latitude']
    .astype(str)
    .str.replace(',', '.', regex=False)
    .astype(float)
)

df['Longitude'] = (
    df['Longitude']
    .astype(str)
    .str.replace(',', '.', regex=False)
    .astype(float)
)

# Drop missing coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])

# Focus period: year before COVID, COVID years, and year after
analysis_start = pd.Timestamp("2019-01-01")
analysis_end = pd.Timestamp("2022-12-31")
df = df[(df['Date'] >= analysis_start) & (df['Date'] <= analysis_end)].copy()

if df.empty:
    raise ValueError("No data available in selected analysis window (2019-2022).")

# -------------------------------
# CREATE TIME FEATURES
# -------------------------------
df['Month'] = df['Date'].dt.to_period('M')
df['Month_ts'] = df['Month'].dt.to_timestamp()

# -------------------------------
#  1. STATIC PLOT (TIME SERIES)
# -------------------------------
monthly = df.groupby('Month').size()
monthly.index = monthly.index.to_timestamp()

plt.figure(figsize=(12,6))
plt.plot(monthly.index, monthly.values, linewidth=2)

plt.title("Total Reported Crime in San Francisco (2019–2022)", fontsize=14)
plt.xlabel("Year", fontsize=12)
plt.ylabel("Number of Incidents", fontsize=12)
plt.xlim(analysis_start, analysis_end)

plt.grid(True, linestyle='--', alpha=0.6)

# Highlight COVID period
plt.axvspan(
    pd.Timestamp("2020-03-01"),
    pd.Timestamp("2021-06-01"),
    alpha=0.2
)

# Label lockdown period directly inside shaded area
lockdown_mid = pd.Timestamp("2020-10-01")
plt.text(
    lockdown_mid,
    monthly.max() * 0.95,
    "COVID lockdown",
    ha="center",
    va="center",
    fontsize=11,
    color="black"
)

plt.tight_layout()
plt.savefig("crime_timeseries.png")
plt.show()

print(" Saved: crime_timeseries.png")


# -------------------------------
#  2. MAP COMPARISON (PRE-COVID VS COVID)
# -------------------------------

# Split data into periods
df_pre = df[(df['Date'] >= pd.Timestamp("2019-01-01")) & (df['Date'] < pd.Timestamp("2020-03-01"))].copy()
df_covid = df[(df['Date'] >= pd.Timestamp("2020-03-01")) & (df['Date'] <= pd.Timestamp("2021-06-01"))].copy()

# Sample safely
sample_size = 10000
df_pre_sample = df_pre.sample(n=min(sample_size, len(df_pre)), random_state=42)
df_covid_sample = df_covid.sample(n=min(sample_size, len(df_covid)), random_state=42)

# Pre-COVID map
m_pre = folium.Map(location=[37.77, -122.42], zoom_start=12)

heat_data_pre = list(zip(df_pre_sample['Latitude'], df_pre_sample['Longitude']))

HeatMap(
    heat_data_pre,
    radius=8,
    blur=10,
    max_zoom=13
).add_to(m_pre)

m_pre.save("crime_map_pre_covid.html")
print("Saved: crime_map_pre_covid.html")

# COVID map
m_covid = folium.Map(location=[37.77, -122.42], zoom_start=12)

heat_data_covid = list(zip(df_covid_sample['Latitude'], df_covid_sample['Longitude']))

HeatMap(
    heat_data_covid,
    radius=8,
    blur=10,
    max_zoom=13
).add_to(m_covid)

m_covid.save("crime_map_covid.html")
print("Saved: crime_map_covid.html")


# -------------------------------
#  3. INTERACTIVE PLOT (PLOTLY)
# -------------------------------

# Keep only top 5 categories (cleaner visualization)
top_categories = df['Unified Category'].value_counts().nlargest(5).index
df_filtered = df[df['Unified Category'].isin(top_categories)]

category_time = (
    df_filtered.groupby(['Month_ts', 'Unified Category'])
    .size()
    .reset_index(name='Count')
)

fig = px.line(
    category_time,
    x="Month_ts",
    y="Count",
    color="Unified Category",
    title="Top Crime Types Over Time",
)

# Improve layout
fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Incidents",
    legend_title="Crime Type"
)

fig.write_html("interactive_plot.html")

print(" Saved: interactive_plot.html")