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

# -------------------------------
# CREATE TIME FEATURES
# -------------------------------
df['Month'] = df['Date'].dt.to_period('M')
df['Month_ts'] = df['Month'].dt.to_timestamp()

# -------------------------------
# 📊 1. STATIC PLOT (TIME SERIES)
# -------------------------------
monthly = df.groupby('Month').size()
monthly.index = monthly.index.to_timestamp()

plt.figure(figsize=(12,6))
plt.plot(monthly.index, monthly.values, linewidth=2)

plt.title("Total Reported Crime in San Francisco (2015–2022)", fontsize=14)
plt.xlabel("Year", fontsize=12)
plt.ylabel("Number of Incidents", fontsize=12)

plt.grid(True, linestyle='--', alpha=0.6)

# Highlight COVID period
plt.axvspan(
    pd.Timestamp("2020-03-01"),
    pd.Timestamp("2021-06-01"),
    alpha=0.2
)

# Optional annotation (nice touch)
plt.annotate(
    "COVID lockdown",
    xy=(pd.Timestamp("2020-04-01"), monthly.max()),
    xytext=(pd.Timestamp("2017-01-01"), monthly.max()*0.9),
    arrowprops=dict(arrowstyle="->")
)

plt.tight_layout()
plt.savefig("crime_timeseries.png")
plt.show()

print("✅ Saved: crime_timeseries.png")


# -------------------------------
# 🗺️ 2. MAP (HEATMAP)
# -------------------------------

# Sample to avoid performance issues
df_sample = df.sample(n=20000, random_state=42)

# Create map
m = folium.Map(location=[37.77, -122.42], zoom_start=12)

heat_data = list(zip(df_sample['Latitude'], df_sample['Longitude']))

HeatMap(
    heat_data,
    radius=8,
    blur=10,
    max_zoom=13
).add_to(m)

m.save("crime_map.html")

print("✅ Saved: crime_map.html")


# -------------------------------
# 📈 3. INTERACTIVE PLOT (PLOTLY)
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

print("✅ Saved: interactive_plot.html")