import matplotlib.pyplot as plt
import pandas as pd

df_combined = pd.read_csv(
    'Police_Department_Incident_Reports_Historical_Combined.csv',
    low_memory=False
)

# Convert to datetime (adjust column name if needed!)
df_combined['Date'] = pd.to_datetime(df_combined['Date'])

# Create a Month column
df_combined['Month'] = df_combined['Date'].dt.to_period('M')

# Now group
monthly = df_combined.groupby('Month').size()

# Plot
plt.figure(figsize=(10,5))
monthly.plot()

plt.title("Total Crime Over Time")
plt.xlabel("Month")
plt.ylabel("Number of Crimes")

plt.savefig("crime_timeseries.png")
plt.show()

import folium
from folium.plugins import HeatMap

m = folium.Map(location=[37.77, -122.42], zoom_start=12)

heat_data = list(zip(df_combined['Y'], df_combined['X']))
HeatMap(heat_data).add_to(m)

m.save("crime_map.html")

import plotly.express as px

fig = px.line(df_combined, x="Date", y="Count", color="Category")

fig.write_html("interactive_plot.html")