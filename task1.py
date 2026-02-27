import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# 1. Load datasets
# -----------------------------
df = pd.read_csv('Police_Department_Incident_Reports__2018_to_Present_20260209.csv')
df_historical = pd.read_csv('Police_Department_Incident_Reports__Historical_2003_to_May_2018_20260209.csv')

# -----------------------------
# 2. Rename historical columns
# -----------------------------
mapping = {
    'IncidntNum': 'Incident Number',
    'Category': 'Incident Category',
    'Descript': 'Incident Description',
    'DayOfWeek': 'Day of Week',
    'Date': 'Incident Date',
    'Time': 'Incident Time',
    'PdDistrict': 'Police District',
    'Resolution': 'Resolution',
    'Address': 'Address',
    'X': 'Longitude',
    'Y': 'Latitude'
}

df_historical.rename(columns=mapping, inplace=True)

# -----------------------------
# 3. Convert dates
# -----------------------------
df['Incident Date'] = pd.to_datetime(df['Incident Date'], errors='coerce')
df_historical['Incident Date'] = pd.to_datetime(df_historical['Incident Date'], errors='coerce')

# -----------------------------
# 4. Select essential columns
# -----------------------------
essential_columns = {
    'Incident Number': ['IncidntNum', 'Incident Number'],
    'Incident Category': ['Category', 'Incident Category'],
    'Incident Description': ['Descript', 'Incident Description'],
    'Day of Week': ['DayOfWeek', 'Incident Day of Week'],
    'Incident Date': ['Date', 'Incident Date'],
    'Incident Time': ['Time', 'Incident Time'],
    'Police District': ['PdDistrict', 'Police District'],
    'Resolution': ['Resolution', 'Resolution'],
    'Longitude': ['X', 'Longitude'],
    'Latitude': ['Y', 'Latitude']
}

df_recent_selected = df[
    [col[1] for col in essential_columns.values() if col[1] in df.columns]
]

df_historical_selected = df_historical[
    [col[1] for col in essential_columns.values() if col[1] in df_historical.columns]
]

# -----------------------------
# 5. Combine datasets
# -----------------------------
df_combined = pd.concat(
    [df_recent_selected, df_historical_selected],
    ignore_index=True
)

# -----------------------------
# 6. Normalize category names
# -----------------------------
df_combined['Incident Category'] = (
    df_combined['Incident Category']
    .astype(str)
    .str.strip()
    .str.lower()
)

# -----------------------------
# 7. Define Personal Focus Crimes
# -----------------------------
personal_focus_crimes = ['assault', 'robbery', 'burglary']

# -----------------------------
# 8. Filter dataset
# -----------------------------
df_filtered = df_combined[
    df_combined['Incident Category'].isin(personal_focus_crimes)
].copy()

# -----------------------------
# 9. Extract year
# -----------------------------
df_filtered['Year'] = df_filtered['Incident Date'].dt.year

# -----------------------------
# 10. Plot yearly counts
# -----------------------------
plt.figure(figsize=(10, 6))

for crime in personal_focus_crimes:
    crime_data = df_filtered[
        df_filtered['Incident Category'] == crime
    ]
    
    crime_incidents_per_year = crime_data.groupby('Year').size()
    
    plt.plot(
        crime_incidents_per_year.index,
        crime_incidents_per_year.values,
        marker='o',
        label=crime.capitalize()
    )

plt.xlabel('Year')
plt.ylabel('Number of Incidents')
plt.title('Total Number of Incidents per Year for Personal Focus Crimes (2003–2025)')
plt.legend()
plt.grid(True)
plt.xlim(2003, 2025)
plt.xticks(range(2003, 2026, 2))

plt.tight_layout()
plt.show()