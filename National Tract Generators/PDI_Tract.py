import geopandas as gpd
import pandas as pd
from census import Census
import os

def get_tract_population(census_gdf, census_api_key, year, output_file, csv_output_file, aggregate_file):
    """
    Retrieves population data for block groups based on a given year and saves the processed data to a file.

    Parameters:
        census_gdf (GeoDataFrame): The GeoDataFrame containing the geometries for the census block groups.
        census_api_key (str): The Census API key.
        year (int): The year for which the data is retrieved (e.g., 2013, 2022).
        output_file (str): The filename where the processed data will be saved.
        csv_output_file (str): The filename for saving the processed CSV data.

    Returns:
        None: The function saves the processed data to the specified files.
    """
    # Check if the API key is provided
    if not census_api_key:
        raise ValueError("API key must be provided as the 'census_api_key' parameter.")

    # Gets state and county FIPS codes
    state_fips = census_gdf.STATEFP[0]
    county_fips = census_gdf.COUNTYFP.unique()

    # Initialize the Census API with the provided key
    c = Census(census_api_key)

    census_pop = []

    # Retrieve census data by block group for the specified state and county
    for county_fip in county_fips:
        data = c.acs5.state_county_blockgroup('B01003_001E', state_fips, county_fip, Census.ALL, year=year)
        census_pop.extend(data)

    # Convert the retrieved population data to a DataFrame and add an index to align with census_gdf
    census_pop_df = pd.DataFrame(census_pop)
    census_pop_df['index'] = census_pop_df.index  # Add an index column to match order

    print(f"Data retrieved from the Census API (first few rows):\n{census_pop_df.head()}")

    # Rename columns in census_gdf to match the names in census_pop_df
    census_gdf.rename(columns={
        'STATEFP': 'state',
        'COUNTYFP': 'county',
        'TRACTCE': 'tract',
    }, inplace=True)

    # Add an index column to census_gdf as well to ensure we can align by index
    census_gdf['index'] = census_gdf.index

    # Merge census_gdf with the population DataFrame by the 'index' column to ensure order-based merging
    merged_gdf = census_gdf.merge(census_pop_df[['index', 'B01003_001E']], on='index', how='left')

    # Drop the index column as it's no longer needed
    merged_gdf = merged_gdf.drop(columns=['index'])

    # Rename the population column to something more user-friendly
    merged_gdf.rename(columns={'B01003_001E': 'Population Count'}, inplace=True)

    # Create the 'GEOID' column
    merged_gdf['GEOID'] = merged_gdf['state'] + merged_gdf['county'] + merged_gdf['tract'] 

    # Calculate area in square kilometers
    area_sqkm = merged_gdf['ALAND'] / 10**6
    merged_gdf['Polygon Area'] = area_sqkm

    # Calculate population density
    merged_gdf['Population Density'] = merged_gdf['Population Count'] / area_sqkm

    # Calculate PDI (Population Density Index) as a percentage of the max density
    max_density = merged_gdf['Population Density'].max() if not merged_gdf['Population Density'].isna().all() else 1
    merged_gdf['PDI'] = (merged_gdf['Population Density'] / max_density) * 100  # PDI as percentage of max, ranging from 0 to 100

    # Ensure that merged_gdf has a valid geometry
    merged_gdf = gpd.GeoDataFrame(merged_gdf, geometry='geometry')

    # Calculate centroids and extract coordinates
    merged_gdf['Centroid'] = merged_gdf.geometry.centroid
    merged_gdf['Coordinates'] = merged_gdf['Centroid'].apply(lambda x: f"({x.y:.6f}, {x.x:.6f})")

    # Drop the Centroid column before saving to GeoJSON
    merged_gdf = merged_gdf.drop(columns=['Centroid'])

    # Save processed data to GeoJSON
    merged_gdf.to_file(output_file, driver="GeoJSON")
    print(f"Data saved to {output_file}")

    # Prepare CSV output with specified column names and order
    csv_output = merged_gdf[['GEOID', 'Population Count', 'Population Density', 'PDI', 'Polygon Area', 'Coordinates']]
    csv_output.to_csv(csv_output_file, index=False)
    print(f"CSV data saved to {csv_output_file}")
    
    # Append population density to aggregate file
    geoidandyear = merged_gdf["GEOID"] + "+" + str(year)
    aggregate_df = pd.DataFrame({
        "GEOID": geoidandyear,
        "Population Density": merged_gdf["Population Density"]
    })
    if os.path.exists(aggregate_file):
        aggregate_df.to_csv(aggregate_file, mode='a', header=False, index=False)
    else:
        aggregate_df.to_csv(aggregate_file, mode='w', header=True, index=False)

    return merged_gdf
# Tract execution

census_api_key = "bb8ddb8b99dc18f4759d67d905c25e1486077c4d"  # ATHARVA's API KEY
census_gdf = gpd.read_file('tracts.geojson')
census_gdf_2013 = get_tract_population(
    census_gdf, year=2013, census_api_key=census_api_key,
    output_file="tracts_2013_PDI.geojson", #INSERT FILES
    csv_output_file="tracts_2013_PDI.csv",
    aggregate_file="PDI_tract_all.csv"
)
census_gdf = gpd.read_file('tracts.geojson')
census_gdf_2017 = get_tract_population(
    census_gdf, year=2017, census_api_key=census_api_key,
    output_file="tracts_2017_PDI.geojson", #INSERT FILES
    csv_output_file="tracts_2017_PDI.csv",
    aggregate_file="PDI_tract_all.csv"
)
census_gdf = gpd.read_file('tracts.geojson')
census_gdf_2022 = get_tract_population(
    census_gdf, year=2022, census_api_key=census_api_key,
    output_file="tracts_2022_PDI.geojson", #INSERT FILES
    csv_output_file="tracts_2022_PDI.csv",
    aggregate_file="PDI_tract_all.csv"
)