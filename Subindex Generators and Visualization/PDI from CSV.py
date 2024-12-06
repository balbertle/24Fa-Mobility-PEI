import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# 1. Load CSV Data
csv_file = "pdi_ENTERYEAR.csv"  # Replace with your CSV file path
df = pd.read_csv(csv_file, encoding='ISO-8859-1')  # Specify encoding if necessary

# 2. Clean and preprocess the data
# Strip any leading/trailing spaces from column names
df.columns = df.columns.str.strip()

# Clean the 'TotPop' column by removing any non-numeric characters (including commas and spaces)
df['TotPop'] = df['TotPop'].replace({',': '', 'Total population ': ''}, regex=True)

# Convert 'TotPop' to a numeric type (float) after cleaning
df['Population Count'] = pd.to_numeric(df['TotPop'], errors='coerce')

# Clean 'LandSQMI' column (strip any extra spaces and convert to float)
df['Land Area Sq. Miles'] = pd.to_numeric(df['LandSQMI'].replace({',': ''}, regex=True), errors='coerce')

# 3. Calculate Population Density
df['Population Density'] = df['Population Count'] / df['Land Area Sq. Miles']

# 4. Create a new DataFrame with GEOID and Population Density
# Assuming 'bg' is the column for GEOID (adjust if necessary)
density_df = df[['GEOID', 'Population Density']]
density_df.rename(columns={'GEOID': 'GEOID'}, inplace=True)

# 5. Save the results to a new CSV
output_csv = "tracts_ENTERYEAR_PDI.csv"  # Output file path
density_df.to_csv(output_csv, index=False)

print(f"Population density data saved to {output_csv}")


# 1. Load the CSV Data with population density
population_density_file = output_csv  # Your CSV file path
df_population_density = pd.read_csv(population_density_file, encoding='ISO-8859-1')


# Remove any rows with empty GEOID values
df_population_density = df_population_density.dropna(subset=['GEOID'])

# Clean the 'GEOID' in the CSV by removing the last 4 digits
df_population_density['Cleaned GEOID'] = df_population_density['GEOID']

# Debugging step: Check first few rows of the cleaned CSV data
print("First few rows of cleaned GEOIDs in CSV:")
print(df_population_density[['GEOID', 'Cleaned GEOID']].head())

# 2. Load the GeoJSON file (This is the file containing block groups with their GEOID)
geojson_file = "DESIREDGEOJSON.geojson"  # Replace with your actual GeoJSON file path
gdf = gpd.read_file(geojson_file)

# Clean the 'GEOID' in the GeoJSON by removing the last 4 digits
gdf['Cleaned GEOID'] = gdf['GEOID'].str.slice(0, -4)

# Debugging step: Check first few rows of the cleaned GeoJSON
print("First few rows of cleaned GEOIDs in GeoJSON:")
print(gdf[['GEOID', 'Cleaned GEOID']].head())

# 3. Merge the GeoDataFrame with the population density DataFrame based on the cleaned GEOID
merged_gdf = gdf.merge(df_population_density[['Cleaned GEOID', 'Population Density']], on='Cleaned GEOID', how='left')

# Debugging step: Check if merging worked by inspecting the first few rows of the merged GeoDataFrame
print("First few rows of merged GeoDataFrame:")
print(merged_gdf[['GEOID', 'Population Density']].head())

# 4. Drop rows with missing population density (if any GEOID does not have a match)
merged_gdf = merged_gdf.dropna(subset=['Population Density'])

# Debugging step: Check if there are still rows after dropping NaN population densities
print(f"Number of rows after dropping NaN values: {len(merged_gdf)}")

# 5. Normalize the Population Density column to be between 0 and 100
min_density = merged_gdf['Population Density'].min()
max_density = merged_gdf['Population Density'].max()

merged_gdf['Normalized Population Density'] = ((merged_gdf['Population Density'] - min_density) / (max_density - min_density)) * 100

# Debugging step: Check the first few rows after normalization
print("First few rows after normalization:")
print(merged_gdf[['GEOID', 'Population Density', 'Normalized Population Density']].head())

# 6. Save the new GeoJSON with the updated population density values
output_geojson_file = "normalized_PDI_tracts_ENTERNAME.geojson"
merged_gdf.to_file(output_geojson_file, driver="GeoJSON")

# Debugging step: Verify if GeoJSON was saved correctly
print(f"GeoJSON file saved to: {output_geojson_file}")