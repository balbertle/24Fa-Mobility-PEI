import pandas as pd
import geopandas as gpd
import os

def calculate_pei(year, output_csv, output_geojson):
    # File prefixes for the components of PEI
    components = ["PDI", "CDI", "IDI", "LDI"]
    
    # Initialize a dictionary to store component data
    component_data = {}
    
    # Read relevant year-specific CSV and GeoJSON files
    for component in components:
        file_csv = f"tracts_{year}_{component}.csv"
        if os.path.exists(file_csv):
            component_data[component] = pd.read_csv(file_csv)[['GEOID', component]]
        else:
            print(f"Missing file: {file_csv}")
            return
        
    result_df = None
    
    # Merge all the data tables on 'GEOID' and 'geometry'
    for key, df in component_data.items():
        # Rename the column corresponding to the key (e.g., PDI, CDI, etc.)
        df = df.rename(columns={key: key.upper()})
        
        # Merge the current DataFrame with the result DataFrame
        if result_df is None:
            result_df = df
        else:
            result_df = pd.merge(result_df, df[['GEOID', key.upper()]], on='GEOID', how='inner')
    
    # Fill null values in PDI, IDI, LDI, CDI columns with 0.5
    pei_columns = ['PDI', 'IDI', 'LDI', 'CDI']
    for col in pei_columns:
        if col not in result_df.columns:
            raise ValueError(f"Missing required column '{col}' for PEI calculation.")
        result_df[col] = result_df[col].fillna(0.5) #SETTING NULL VALUES TO 0.5????!?!?!?!?
    
    # Calculate PEI
    result_df['PEI'] = ((1 + result_df['PDI']) * 
                        (1 + result_df['IDI']) * 
                        (1 + result_df['LDI']) * 
                        (1 + result_df['CDI'])) / 16
    final_df = result_df[['GEOID', 'PEI']]
    
    #print(final_df)

    # Save to CSV
    final_df.to_csv(output_csv, index=False)

    # Load the GeoJSON file for geometry and coordinates
    geojson_file = f"tracts_{year}_PDI.geojson"
    if os.path.exists(geojson_file):
        gdf = gpd.read_file(geojson_file)
        # Merge PEI scores into the GeoJSON DataFrame
        final_df['GEOID'] = final_df['GEOID'].astype('int64')
        gdf['GEOID'] = gdf['GEOID'].astype('int64')
        gdf = gdf[['GEOID', 'geometry']].merge(final_df[['GEOID', 'PEI']], on='GEOID', how='inner')
        gdf = gdf[['GEOID','PEI','geometry']]
        
        # Save to GeoJSON
        gdf.to_file(output_geojson, driver="GeoJSON")
    else:
        print(f"Missing GeoJSON file: {geojson_file}")
        return
    return

# Define years and output file paths
years = [2013, 2017, 2022]
for year in years:
    output_csv = f"tracts_{year}_PEI.csv"
    output_geojson = f"tracts_{year}_PEI.geojson"
    calculate_pei(year, output_csv, output_geojson)